#pragma once
#include <array>
#include <cstdio>
#include <cstdint>
#include <cstddef>
namespace stuzha {
inline std::array<float, 8> cloudFields(float temp, float rh, float pm, float co,
                                       float gp, float pwm, float mq135, float mq7) {
    return {{temp, rh, pm, co, gp, pwm, mq135, mq7}};
}
struct CloudStatus {
    const char *version, *build, *models, *boot;
    uint64_t uptime_ms;
    uint32_t reset, level, flags, sequence;
    float score, pm_base, pm_scale, co_base, co_scale;
    uint32_t samples, timing_bad, gp_max, infer_us, attempts, failures, skipped, slot, heap;
};
inline int formatStatus(char *buffer, size_t size, const CloudStatus &s) {
    return snprintf(buffer, size,
        "STZ31|v=%s|h=%s|m=%s|b=%s|u=%llu|r=%lu|l=%lu|f=%lu|s=%lu|z=%.3g|a=%.4g,%.4g,%.4g,%.4g|n=%lu|j=%lu|x=%lu|i=%lu|e=%lu,%lu,%lu|q=%lu|k=%lu",
        s.version, s.build, s.models, s.boot, (unsigned long long)s.uptime_ms,
        (unsigned long)s.reset, (unsigned long)s.level, (unsigned long)s.flags,
        (unsigned long)s.sequence, s.score, s.pm_base, s.pm_scale, s.co_base, s.co_scale,
        (unsigned long)s.samples, (unsigned long)s.timing_bad, (unsigned long)s.gp_max,
        (unsigned long)s.infer_us, (unsigned long)s.attempts, (unsigned long)s.failures,
        (unsigned long)s.skipped, (unsigned long)s.slot, (unsigned long)s.heap);
}
}
