#ifndef STUZHA_MONITORING_CORE_H
#define STUZHA_MONITORING_CORE_H
#include <cmath>
#include <cstdint>
#include <algorithm>

namespace stuzha {
// Engineering response levels, NOT health limits or ISPU categories.
constexpr uint32_t BASELINE_FRAMES = 120;
constexpr float MIN_SCALE_ADC = 10.0f;
// Floors are engineering parameters in model-output units, NOT exposure limits.
constexpr float MIN_SCALE_PM_MODEL = 5.0f;
constexpr float MIN_SCALE_CO_MODEL = 0.2f;
constexpr float UP_THRESHOLDS[] = {3.0f, 6.0f, 12.0f, 24.0f};
constexpr int PWM[] = {33, 38, 56, 128, 217};
constexpr uint64_t DOWN_HOLD_MS = 30000;
enum Flags : uint32_t {
    DHT_INVALID = 1, GP_RAIL = 2, MQ7_RAIL = 4, MQ135_RAIL = 8,
    GP_TIMING = 16, BASELINE_PENDING = 32, WIFI_OFFLINE = 64,
    MODEL_INVALID = 128, MQ7_HEATER_UNVERIFIED = 256, FRAME_INCOMPLETE = 512,
    PROCESSING_STALE = 1024, MODEL_TRANSFER_UNVERIFIED = 2048
};

struct Moments {
    uint32_t n = 0;
    double mean = 0, m2 = 0;
    void add(double x) {
        ++n;
        double delta = x - mean;
        mean += delta / n;
        m2 += delta * (x - mean);
    }
    float sd() const { return n > 1 ? std::sqrt(m2 / (n - 1)) : 0; }
};

class RelativeDustControl {
public:
    Moments baseline;
    int level = 1;
    float score = 0;
    bool ready() const { return baseline.n >= BASELINE_FRAMES; }
    float scale() const { return std::max(MIN_SCALE_ADC, baseline.sd()); }
    // Initial reference is fixed per boot. It is not assumed to be clean air.
    void update(float adc, bool valid, uint64_t now_ms) {
        if (!valid || !std::isfinite(adc)) {
            level = std::max(level, 4); // Explicit fan fallback on failed dust acquisition.
            score = NAN;
            up_count = 0;
            down_since = 0;
            return;
        }
        if (!ready()) {
            baseline.add(adc);
            level = 1;
            score = 0;
            return;
        }
        score = std::max(0.0f, (adc - static_cast<float>(baseline.mean)) / scale());
        int target = 1;
        for (float threshold : UP_THRESHOLDS) if (score >= threshold) ++target;
        if (target > level) {
            down_since = 0;
            if (++up_count >= 2) { level = target; up_count = 0; }
        } else {
            up_count = 0;
            if (level > 1 && score < UP_THRESHOLDS[level - 2] * 0.8f) {
                if (!down_since) down_since = now_ms;
                if (now_ms - down_since >= DOWN_HOLD_MS) {
                    --level;
                    down_since = 0;
                }
            } else down_since = 0;
        }
    }
private:
    uint32_t up_count = 0;
    uint64_t down_since = 0;
};

// Actuator decisions use BOTH model outputs. Raw control is retained above only
// for the v3.0 historical regression test; it is not used by v3.1 firmware.
class ModelResponseControl {
public:
    Moments pm_baseline, co_baseline;
    int level = 1;
    float score = 0;
    bool ready() const { return pm_baseline.n >= BASELINE_FRAMES; }
    float pm_scale() const { return std::max(MIN_SCALE_PM_MODEL, pm_baseline.sd()); }
    float co_scale() const { return std::max(MIN_SCALE_CO_MODEL, co_baseline.sd()); }
    void update(float pm, float co, bool valid, uint64_t now_ms) {
        if (!valid || !std::isfinite(pm) || !std::isfinite(co) || pm < 0 || co < 0) {
            level = std::max(level, 4);
            score = NAN; up_count = 0; down_since = 0;
            return;
        }
        if (!ready()) {
            pm_baseline.add(pm); co_baseline.add(co);
            score = 0; up_count = 0; down_since = 0;
            // A preceding fault remains at >=L4 until reference acquisition ends.
            return;
        }
        score = std::max(0.0f, std::max(
            (pm - float(pm_baseline.mean)) / pm_scale(),
            (co - float(co_baseline.mean)) / co_scale()));
        int target = 1;
        for (float threshold : UP_THRESHOLDS) if (score >= threshold) ++target;
        if (target > level) {
            down_since = 0;
            if (++up_count >= 2) { level = target; up_count = 0; }
        } else {
            up_count = 0;
            if (level > 1 && score < UP_THRESHOLDS[level - 2] * 0.8f) {
                if (!down_since) down_since = now_ms;
                if (now_ms - down_since >= DOWN_HOLD_MS) { --level; down_since = 0; }
            } else down_since = 0;
        }
    }
private:
    uint32_t up_count = 0;
    uint64_t down_since = 0;
};
} // namespace stuzha
#endif
