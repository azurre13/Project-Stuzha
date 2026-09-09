#pragma once
#include <algorithm>
#include <cmath>
#include "model_pm.h"
#include "model_co.h"

namespace stuzha {
// Keep the two inference bodies separate; platformio.ini places Xtensa literals
// next to their functions at -O3 to keep references in reach.
// Do not change the retained tree headers to work around linker layout.
__attribute__((noinline)) inline float runExperimentalPM(float *features) { return model_pm_predict(features); }
__attribute__((noinline)) inline float runExperimentalCO(float *features) { return model_co_predict(features); }
struct ModelOutput {
    float pm = NAN, co = NAN;
    bool valid() const { return std::isfinite(pm) && std::isfinite(co) && pm >= 0 && co >= 0; }
};
// Preserve historical preprocessing and header identity for this deployment.
// PM: nominal legacy scale (physical units unresolved).
// CO: nominal UCI target mg/m3; transfer from PT08 to MQ7 is NOT validated.
inline ModelOutput predictExperimental(float gp_adc, float mq7_adc, float temp, float rh) {
    ModelOutput out;
    if (!std::isfinite(gp_adc) || !std::isfinite(mq7_adc) || !std::isfinite(temp) ||
        !std::isfinite(rh) || gp_adc <= 1 || gp_adc >= 4094 || mq7_adc <= 1 ||
        mq7_adc >= 4094 || temp < -40 || temp > 80 || rh < 0 || rh > 100) return out;
    float pm_features[] = {std::max(0.0f, (0.17f * gp_adc * 3.3f / 4095.0f - 0.1f) * 1000.0f), temp, rh};
    float co_features[] = {mq7_adc, temp, rh};
    out.pm = runExperimentalPM(pm_features);
    out.co = runExperimentalCO(co_features);
    if (!out.valid()) return ModelOutput{};
    return out;
}
}
