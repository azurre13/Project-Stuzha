#pragma once
#include <cmath>
#include <algorithm>
#include <cstdint>
namespace stuzha {
// Permen LHK P.14/2020 Lampiran I: BOTH pollutant tables use ug/m3, 24 h.
// Calling these functions on an instantaneous estimate produces a diagnostic
// index, NOT a compliant 24-hour ambient-air measurement.
constexpr float ISPU_POINTS[] = {0, 50, 100, 200, 300, 500};
constexpr float PM_POINTS[] = {0, 15.5f, 55.4f, 150.4f, 250.4f, 500};
constexpr float CO_POINTS_UG[] = {0, 4000, 8000, 15000, 30000, 45000};
inline float interpolateIspu(float concentration, const float *points) {
    if (!std::isfinite(concentration) || concentration < 0) return NAN;
    for (int i=1; i<6; ++i) if (concentration <= points[i])
        return ISPU_POINTS[i-1] + (concentration-points[i-1]) *
            (ISPU_POINTS[i]-ISPU_POINTS[i-1])/(points[i]-points[i-1]);
    return 500; // Caller MUST preserve above-range diagnostic separately.
}
inline int categoryCode(float index) {
    if (!std::isfinite(index) || index < 0) return 0;
    int rounded = int(std::lround(index));
    return rounded<=50 ? 1 : rounded<=100 ? 2 : rounded<=200 ? 3 : rounded<=300 ? 4 : 5;
}
inline const char *categoryName(int category) {
    static const char *names[] = {"Tidak tersedia", "Baik", "Sedang", "Tidak Sehat", "Sangat Tidak Sehat", "Berbahaya"};
    return category>=0 && category<=5 ? names[category] : names[0];
}
// Ideal-gas conversion at declared fixed reference conditions: 25 C, 1 atm.
// Do not silently change reporting units with the room's DHT temperature.
constexpr float CO_MG_PER_PPM = 28.01f * 101325.0f / (8.314462618f * 298.15f) / 1000.0f;
inline float coMgToPpm(float mg) { return mg / CO_MG_PER_PPM; }
inline float coPpmToMg(float ppm) { return ppm * CO_MG_PER_PPM; }
struct IspuResult {
    float pm = NAN, co = NAN, maximum = NAN;
    int category = 0, critical = 0; // 1 PM, 2 CO, 3 tied, 0 unavailable
    bool above_range = false;
};
inline IspuResult estimateIspu(float pm_ug, float co_mg) {
    IspuResult r;
    r.pm = interpolateIspu(pm_ug, PM_POINTS);
    r.co = interpolateIspu(co_mg*1000.0f, CO_POINTS_UG);
    // A final two-pollutant index requires both channels. Never call missing CO zero.
    if (std::isfinite(r.pm) && std::isfinite(r.co)) {
        r.maximum = std::max(r.pm,r.co); r.category = categoryCode(r.maximum);
        r.critical = r.pm==r.co ? 3 : r.pm>r.co ? 1 : 2;
        r.above_range = pm_ug>PM_POINTS[5] || co_mg*1000.0f>CO_POINTS_UG[5];
    }
    return r;
}
}
