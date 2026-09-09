#include "../Program/Kode/include/monitoring_core.h"
#include <cassert>
#include <iostream>
using namespace stuzha;
RelativeDustControl ready() {
    RelativeDustControl c;
    for (uint32_t i = 0; i < BASELINE_FRAMES; ++i) c.update(500, true, (i + 1) * 1000);
    assert(c.ready() && c.level == 1 && c.scale() == MIN_SCALE_ADC);
    return c;
}
int main() {
    // Exact rising boundaries at every level; isolated spikes do not switch.
    for (int i = 0; i < 4; ++i) {
        auto c = ready();
        float adc = 500 + UP_THRESHOLDS[i] * MIN_SCALE_ADC;
        c.update(adc, true, 121000); assert(c.level == 1);
        c.update(adc, true, 122000); assert(c.level == i + 2);
        assert(c.baseline.mean == 500); // Frozen reference, not an adaptive clean-air assumption.
    }
    auto c = ready();
    c.update(750, true, 121000); c.update(750, true, 122000);
    assert(c.level == 5);
    // No descent inside hysteresis band; then only one step after full dwell.
    c.update(700, true, 123000); c.update(700, true, 160000); assert(c.level == 5);
    c.update(500, true, 161000); c.update(500, true, 190999); assert(c.level == 5);
    c.update(500, true, 191000); assert(c.level == 4);
    c.update(NAN, false, 192000); assert(c.level >= 4 && std::isnan(c.score));
    auto fresh = RelativeDustControl();
    fresh.update(4095, false, 1000); assert(fresh.baseline.n == 0 && fresh.level == 4);
    // 64-bit clock beyond millis() wrap; dwell still works.
    auto wrapped = ready();
    wrapped.update(750, true, 4294967200ULL); wrapped.update(750, true, 4294968200ULL);
    wrapped.update(500, true, 4294969200ULL); wrapped.update(500, true, 4294999200ULL);
    assert(wrapped.level == 4);
    std::cout << "Control: all boundaries, spike rejection, dwell, fault and clock checks passed\n";
}
