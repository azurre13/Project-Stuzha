#include "../Program/Kode/include/monitoring_core.h"
#include "../Program/Kode/include/experimental_models.h"
#include "../Program/Kode/include/telemetry_contract.h"
#include <cassert>
#include <iostream>
#include <cstring>
using namespace stuzha;
ModelResponseControl readyModels() {
    ModelResponseControl c;
    for (unsigned i = 0; i < BASELINE_FRAMES; ++i) c.update(10, 1, true, (i+1)*1000);
    assert(c.ready());
    return c;
}
int main() {
    for (int i = 0; i < 4; ++i) {
        auto pm = readyModels(), co = readyModels();
        // Only the model output changes; no raw ADC argument can drive this controller.
        const float raised_pm = 10 + UP_THRESHOLDS[i]*MIN_SCALE_PM_MODEL;
        const float raised_co = 1 + UP_THRESHOLDS[i]*MIN_SCALE_CO_MODEL + 0.00001f;
        pm.update(raised_pm, 1, true, 121000); assert(pm.level == 1);
        pm.update(raised_pm, 1, true, 122000); assert(pm.level == i+2);
        co.update(10, raised_co, true, 121000); assert(co.level == 1);
        co.update(10, raised_co, true, 122000); assert(co.level == i+2);
        assert(pm.pm_baseline.mean == 10 && co.co_baseline.mean == 1);
    }
    auto c = readyModels();
    c.update(140, 1, true, 121000); c.update(140, 1, true, 122000);
    c.update(110, 1, true, 123000); c.update(110, 1, true, 180000); assert(c.level == 5);
    c.update(10, 1, true, 181000); c.update(10, 1, true, 210999); assert(c.level == 5);
    c.update(10, 1, true, 211000); assert(c.level == 4);
    c.update(NAN, 1, true, 212000); assert(c.level == 4 && std::isnan(c.score));
    auto fresh = ModelResponseControl();
    fresh.update(10, NAN, false, 1000); assert(fresh.pm_baseline.n == 0 && fresh.level == 4);
    fresh.update(10, 1, true, 2000); assert(fresh.level == 4 && !fresh.ready());
    auto wrapped = readyModels();
    wrapped.update(140, 1, true, 4294967200ULL); wrapped.update(140, 1, true, 4294968200ULL);
    wrapped.update(10, 1, true, 4294969200ULL); wrapped.update(10, 1, true, 4294999200ULL);
    assert(wrapped.level == 4);
    // Run the actual retained headers through the exact firmware preprocessing.
    const auto base = predictExperimental(900, 1000, 25, 50);
    const auto high = predictExperimental(3000, 3000, 25, 50);
    assert(base.valid() && high.valid());
    ModelResponseControl integrated;
    for (unsigned i=0; i<BASELINE_FRAMES; ++i) integrated.update(base.pm, base.co, base.valid(), (i+1)*1000);
    integrated.update(high.pm, high.co, high.valid(), 121000);
    integrated.update(high.pm, high.co, high.valid(), 122000);
    assert(integrated.level > 1);
    assert(!predictExperimental(900, 1000, NAN, 50).valid());
    assert(!predictExperimental(4095, 1000, 25, 50).valid());
    const auto fields = cloudFields(25, 50, base.pm, base.co, 900, 12.94f, 1600, 1000);
    assert(fields[2] == base.pm && fields[3] == base.co && fields[4] == 900 && fields[7] == 1000);
    CloudStatus s{"3.1.0", "123456789abc", "12345678", "12345678", 691200000ULL,
        255, 5, 4095, 691200, 999.9f, 500, 500, 12, 12, 110, 110, 4095,
        1000000, 34560, 34560, 34560, 34560, 327680};
    char status[256];
    int length = formatStatus(status, sizeof(status), s);
    assert(length > 0 && length < 256 && strlen(status) == size_t(length));
    assert(strstr(status, "STZ31|") == status && strstr(status, "|f=4095|s=691200|"));
    char small[16]; assert(formatStatus(small, sizeof(small), s) >= int(sizeof(small)));
    std::cout << "Actual header integration: PM " << base.pm << " -> " << high.pm
              << "; CO " << base.co << " -> " << high.co << "; level " << integrated.level
              << ". Eight-day status envelope " << length << " bytes. All checks passed.\n";
}
