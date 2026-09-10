#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <ThingSpeak.h>
#include <DHT.h>
#include <driver/adc.h>
#include <esp_adc_cal.h>
#include <esp_system.h>
#include <esp_timer.h>
#include "pin_config.h"
#include "monitoring_core.h"
#include "build_info.h"
#include "experimental_models.h"
#include "telemetry_v4.h"
#include "ispu_control.h"
#include "rolling_ispu.h"
#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#endif

using namespace stuzha;
DHT dht(PIN_DHT22, DHT22);
WiFiClient client;
esp_adc_cal_characteristics_t adc_cal;
IspuControl control;
RollingIspu rolling;
constexpr uint32_t PM_SCALE_UNVERIFIED = 4096, INDEX_ABOVE_RANGE = 8192,
                   GP_SATURATED = 16384, AVERAGE_PENDING = 32768;
QueueHandle_t acquisition_queue, telemetry_queue;
char boot_id[9];
uint32_t reset_reason;

struct AnalogFrame {
    uint64_t uptime_ms = 0;
    uint32_t seq = 0, n = 0, bad_timing = 0, rails = 0;
    float dust = NAN, mq7 = NAN, mq135 = NAN;
    uint16_t dust_min = 4095, dust_max = 0;
    uint32_t period_max_us = 0, pulse_max_us = 0;
};
struct Telemetry {
    AnalogFrame raw;
    uint32_t flags = 0, infer_us = 0, heap = 0;
    float temp = NAN, rh = NAN, dust_pin_mv = NAN;
    float model_pm = NAN, model_co = NAN, score = NAN;
    float pm24 = NAN, co24 = NAN, index24 = NAN, coverage = 0;
    int category = 0, critical = 0;
    uint8_t level = 1;
};

// Only this task reads ADCs. Network calls cannot block this task.
// Task scheduling is measured; it is not a hardware timing guarantee.
void sampleTask(void *) {
    TickType_t wake = xTaskGetTickCount();
    uint32_t seq = 0, n = 0, bad = 0, rails = 0, max_period = 0, max_pulse = 0;
    uint16_t lo = 4095, hi = 0;
    uint64_t previous_us = 0, window_us = esp_timer_get_time();
    double dust_sum = 0, mq7_sum = 0, mq135_sum = 0;
    for (;;) {
        digitalWrite(PIN_DUST_ILED, LOW);
        const uint64_t start = esp_timer_get_time();
        uint32_t period = previous_us ? uint32_t(start - previous_us) : 10000;
        previous_us = start;
        max_period = std::max(max_period, period);
        delayMicroseconds(280);
        const uint64_t read_start = esp_timer_get_time();
        const int dust = adc1_get_raw(ADC1_CHANNEL_6); // GPIO34; configured before task starts
        int32_t remaining = 320 - int32_t(esp_timer_get_time() - start);
        if (remaining > 0) delayMicroseconds(remaining);
        digitalWrite(PIN_DUST_ILED, HIGH);
        uint32_t pulse = uint32_t(esp_timer_get_time() - start);
        max_pulse = std::max(max_pulse, pulse);
        if (period < 9000 || period > 11000 || read_start - start > 300 || pulse > 340) ++bad;
        const int mq7 = adc1_get_raw(ADC1_CHANNEL_4); // GPIO32
        const int mq135 = adc1_get_raw(ADC1_CHANNEL_5); // GPIO33
        if (dust <= 1 || dust >= 4094) rails |= GP_RAIL;
        if (mq7 <= 1 || mq7 >= 4094) rails |= MQ7_RAIL;
        if (mq135 <= 1 || mq135 >= 4094) rails |= MQ135_RAIL;
        dust_sum += dust; mq7_sum += mq7; mq135_sum += mq135; ++n;
        lo = std::min(lo, uint16_t(dust)); hi = std::max(hi, uint16_t(dust));
        uint64_t now = esp_timer_get_time();
        if (now - window_us >= 1000000) {
            AnalogFrame f;
            f.uptime_ms = now / 1000; f.seq = ++seq; f.n = n;
            f.dust = dust_sum / n; f.mq7 = mq7_sum / n; f.mq135 = mq135_sum / n;
            f.bad_timing = bad; f.rails = rails; f.dust_min = lo; f.dust_max = hi;
            f.period_max_us = max_period; f.pulse_max_us = max_pulse;
            xQueueOverwrite(acquisition_queue, &f);
            dust_sum = mq7_sum = mq135_sum = 0;
            n = bad = rails = max_period = max_pulse = 0;
            lo = 4095; hi = 0; window_us = now;
        }
        vTaskDelayUntil(&wake, pdMS_TO_TICKS(10));
        // Do not issue catch-up pulses in a burst following a long scheduling stall.
        if (xTaskGetTickCount() - wake > pdMS_TO_TICKS(10)) wake = xTaskGetTickCount();
    }
}

String numberOrEmpty(float value, int decimals = 3) {
    return std::isfinite(value) ? String(value, decimals) : String("");
}

// Cloud is a snapshot every 20 seconds, not a durable offline queue.
void networkTask(void *) {
    ThingSpeak.begin(client);
    client.setTimeout(3); // Arduino-ESP32 2.0.17 WiFiClient uses SECONDS here.
    uint64_t last_slot = 0, last_reconnect = 0;
    uint32_t slot = 0, attempts = 0, failures = 0, skipped = 0;
    for (;;) {
        uint64_t now = esp_timer_get_time() / 1000;
        bool online = WiFi.status() == WL_CONNECTED;
        if (!online && now - last_reconnect >= 10000) {
            last_reconnect = now;
            WiFi.reconnect();
        }
        if (now - last_slot >= 20000) {
            last_slot = now;
            // Slot identity follows the boot clock, not only successful task iterations.
            // Count missed scheduling slots as unattempted, never as successful sends.
            uint32_t due_slot = uint32_t(now / 20000);
            if (due_slot > slot + 1) skipped += due_slot - slot - 1;
            slot = due_slot;
            Telemetry t;
            if (xQueuePeek(telemetry_queue, &t, 0) == pdTRUE) {
                if (!online) ++skipped;
                else {
                    if (now - t.raw.uptime_ms > 2500) t.flags |= PROCESSING_STALE;
                    ++attempts;
                    const auto fields = cloudFieldsV4(t.temp, t.rh, t.model_pm, coMgToPpm(t.model_co),
                        t.score, PWM[t.level - 1] * 100.0f / 255.0f, t.raw.mq135, t.category);
                    for (unsigned i = 0; i < fields.size(); ++i)
                        ThingSpeak.setField(i + 1, numberOrEmpty(fields[i], 6));
                    char status[256];
                    StatusV4 metadata{STUZHA_VERSION, STUZHA_BUILD, STUZHA_MODELS, boot_id,
                        t.raw.uptime_ms, reset_reason, t.level, t.flags, t.raw.seq,
                        t.raw.n, t.raw.bad_timing, t.infer_us, attempts, failures, skipped, slot, t.heap,
                        t.raw.dust, t.raw.mq7, t.pm24, t.co24, t.index24, t.coverage, t.critical};
                    int length = formatStatusV4(status, sizeof(status), metadata);
                    int result = -101;
                    if (length > 0 && length < int(sizeof(status)) && ThingSpeak.setStatus(status) == 200)
                        result = ThingSpeak.writeFields(myChannelNumber, myWriteAPIKey);
                    if (result != 200) ++failures;
                    if (result == 200) {
                        Serial.printf("[ThingSpeak] Data berhasil dikirim ke Cloud IoT (HTTP 200, Slot %lu)\n", (unsigned long)slot);
                    } else {
                        Serial.printf("[ThingSpeak] Gagal mengirim data, HTTP Error: %d (Slot %lu)\n", result, (unsigned long)slot);
                    }
                }
            }
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void setup() {
    // Brownout detection stays enabled: do not conceal power failures.
    Serial.begin(115200);
    snprintf(boot_id, sizeof(boot_id), "%08lx", (unsigned long)esp_random());
    reset_reason = esp_reset_reason();
    pinMode(PIN_DUST_ILED, OUTPUT); digitalWrite(PIN_DUST_ILED, HIGH);
    pinMode(PIN_BUZZER, OUTPUT); digitalWrite(PIN_BUZZER, LOW);
    ledcSetup(FAN_PWM_CHANNEL, FAN_PWM_FREQ, FAN_PWM_RES);
    ledcAttachPin(PIN_FAN_PWM, FAN_PWM_CHANNEL);
    ledcWrite(FAN_PWM_CHANNEL, FAN_SPEED_STANDBY);
    // noTone() writes zero duty even before the first alarm; initialize its
    // separate channel so silent operation does not produce LEDC errors.
    ledcSetup(15, 1000, 10);
    ledcAttachPin(PIN_BUZZER, 15);
    ledcWrite(15, 0);
    setToneChannel(15); // Separate timer from fan channel 0.
    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(ADC1_CHANNEL_6, ADC_ATTEN_DB_12);
    adc1_config_channel_atten(ADC1_CHANNEL_4, ADC_ATTEN_DB_12);
    adc1_config_channel_atten(ADC1_CHANNEL_5, ADC_ATTEN_DB_12);
    auto cal_source = esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_12, ADC_WIDTH_BIT_12, 1100, &adc_cal);
    dht.begin();
    acquisition_queue = xQueueCreate(1, sizeof(AnalogFrame));
    telemetry_queue = xQueueCreate(1, sizeof(Telemetry));
    if (!acquisition_queue || !telemetry_queue) abort();
    Serial.println(F("\n=================================================="));
    Serial.println(F(" Project Stuzha — Edge AI ISPU Indoor Air Quality"));
    Serial.printf(" ESP32 TinyML Random Forest Firmware v%s\n", STUZHA_VERSION);
    Serial.printf(" Build:%s | Model:%s | Boot:%s\n", STUZHA_BUILD, STUZHA_MODELS, boot_id);
    Serial.println(F("=================================================="));
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    WiFi.setTxPower(WIFI_POWER_15dBm);
    WiFi.begin(ssid, password);
    if (xTaskCreatePinnedToCore(sampleTask, "stuzha_adc", 4096, nullptr, 4, nullptr, 1) != pdPASS) abort();
    if (xTaskCreatePinnedToCore(networkTask, "stuzha_cloud", 8192, nullptr, 1, nullptr, 0) != pdPASS) abort();
}

void loop() {
    static uint64_t last_frame_ms = 0;
    static bool stale_handled = false;
    static Telemetry latest;
    AnalogFrame f;
    if (xQueueReceive(acquisition_queue, &f, pdMS_TO_TICKS(100)) != pdTRUE) {
        const uint64_t now = esp_timer_get_time() / 1000;
        if (!stale_handled && acquisitionStale(now, last_frame_ms)) {
            stale_handled = true;
            control.update(NAN, false, false, now);
            ledcWrite(FAN_PWM_CHANNEL, PWM[control.level-1]);
            noTone(PIN_BUZZER); digitalWrite(PIN_BUZZER, LOW);
            rolling.update(now, NAN, NAN, false);
            // Preserve the real sample timestamp/sequence; do not invent a reading.
            latest.flags |= PROCESSING_STALE | MODEL_INVALID |
                            MQ7_HEATER_UNVERIFIED | MODEL_TRANSFER_UNVERIFIED | PM_SCALE_UNVERIFIED;
            if (!std::isfinite(latest.index24)) latest.flags |= AVERAGE_PENDING;
            latest.model_pm = latest.model_co = latest.score = NAN;
            latest.category = latest.critical = 0;
            latest.infer_us = 0;
            latest.level = control.level;
            xQueueOverwrite(telemetry_queue, &latest);
            Serial.println("EVENT,acquisition_stale,fan_fallback");
        }
        return;
    }
    const uint64_t processing_ms = esp_timer_get_time() / 1000;
    last_frame_ms = f.uptime_ms;
    stale_handled = false;
    Telemetry t;
    t.raw = f;
    t.flags = f.rails | MQ7_HEATER_UNVERIFIED | MODEL_TRANSFER_UNVERIFIED | PM_SCALE_UNVERIFIED;
    if (f.bad_timing) t.flags |= GP_TIMING;
    if (f.n < 90 || f.n > 110) t.flags |= FRAME_INCOMPLETE;
    if (acquisitionStale(processing_ms, f.uptime_ms)) t.flags |= PROCESSING_STALE;
    // DHT22 cached between 2-second acquisitions. Invalid readings stay invalid.
    static uint64_t last_dht = 0;
    static bool dht_attempted = false;
    static float temperature = NAN, humidity = NAN;
    if (!dht_attempted || f.uptime_ms - last_dht >= 2000) {
        dht_attempted = true;
        last_dht = f.uptime_ms;
        temperature = dht.readTemperature();
        humidity = dht.readHumidity();
    }
    if (std::isfinite(temperature) && std::isfinite(humidity) &&
        temperature >= -40 && temperature <= 80 && humidity >= 0 && humidity <= 100) {
        t.temp = temperature; t.rh = humidity;
    } else t.flags |= DHT_INVALID;
    if (WiFi.status() != WL_CONNECTED) t.flags |= WIFI_OFFLINE;
    // Conversion of the SAME raw ADC to estimated pin millivolts. Not sensor calibration.
    t.dust_pin_mv = esp_adc_cal_raw_to_voltage(uint32_t(lround(f.dust)), &adc_cal);
    // Experimental soft-sensor outputs are the PRIMARY inputs to the controller.
    // No claim of physical concentration calibration or proven drift correction.
    const bool optical_saturated = f.dust >= 4094;
    if (optical_saturated) t.flags |= GP_SATURATED;
    // A single rail sample is diagnostic, not proof the whole frame is broken.
    bool valid_inputs = !(t.flags & (DHT_INVALID | FRAME_INCOMPLETE | PROCESSING_STALE)) &&
                        f.bad_timing <= f.n / 10;
    if (valid_inputs) {
        uint32_t begin = micros();
        const ModelOutput output = predictExperimental(f.dust, f.mq7, t.temp, t.rh);
        t.infer_us = micros() - begin;
        t.model_pm = output.pm; t.model_co = output.co;
        valid_inputs = output.valid();
    }
    if (!valid_inputs) t.flags |= MODEL_INVALID;
    // Legacy PM numeric scale is an explicit unvalidated nominal ug/m3 assumption.
    // CO model target is mg/m3; ppm is for display only, index converts mg -> ug.
    const IspuResult result = estimateIspu(t.model_pm, t.model_co);
    t.score = result.maximum; t.category = result.category; t.critical = result.critical;
    if (result.above_range) t.flags |= INDEX_ABOVE_RANGE;
    rolling.update(f.uptime_ms,t.model_pm,t.model_co,valid_inputs);
    t.pm24=rolling.pm_mean; t.co24=rolling.co_mean; t.index24=rolling.index;
    t.coverage=rolling.coverage;
    if (!std::isfinite(t.index24)) t.flags |= AVERAGE_PENDING;
    control.update(t.score,valid_inputs,optical_saturated,processing_ms);
    t.level=control.level;
    ledcWrite(FAN_PWM_CHANNEL, PWM[t.level-1]);
    // Alarm requires a current model-based high category. Fault recovery is silent.
    // Rate-limit chirps independently; neither alarm nor decay blocks acquisition.
    static uint64_t last_chirp=0;
    if (control.pollution_alarm && f.uptime_ms-last_chirp>=5000) {
        tone(PIN_BUZZER,1000,100); last_chirp=f.uptime_ms;
    } else if (!control.pollution_alarm) { noTone(PIN_BUZZER); digitalWrite(PIN_BUZZER,LOW); }
    t.heap = ESP.getFreeHeap();
    latest = t;
    xQueueOverwrite(telemetry_queue, &t);
    const char *crit = t.critical == 1 ? "PM2.5" : (t.critical == 2 ? "CO" : (t.critical == 3 ? "Seimbang" : "-"));
    const int fan_pct = (int)lround(PWM[t.level - 1] * 100.0f / 255.0f);
    Serial.printf("[TELEMETRI] T:%.1f C | RH:%.1f %% | PM2.5:[ADC:%.0f -> ML:%.1f] ug/m3 | CO:[ADC:%.0f -> ML:%.2f ppm] | ISPU:%.0f (%s) | Dominan:%s | Kipas:%d %% (Level %d)\r\n",
                  t.temp, t.rh,
                  f.dust, t.model_pm,
                  f.mq7, coMgToPpm(t.model_co),
                  t.score, categoryName(t.category),
                  crit, fan_pct, t.level);
}

