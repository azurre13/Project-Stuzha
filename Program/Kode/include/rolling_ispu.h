#pragma once
#include "ispu_calc.h"
#include <cstdint>
namespace stuzha {
// Time-weighted, minute-aligned completed 24-hour window; volatile per boot.
// Missing intervals >1.5 s are not backfilled. Wi-Fi is independent of this ring.
class RollingIspu {
    struct Bin { double pm=0,co=0; uint32_t valid_ms=0; };
    Bin bins[1440]{};
    uint64_t active_minute=0,previous=0;
    float previous_pm=NAN,previous_co=NAN;
    bool initialized=false,previous_valid=false;
    void advance(uint64_t minute) {
        if (minute-active_minute>=1440) {
            for (auto &b:bins) b=Bin{};
            active_minute=minute;
        } else while (active_minute<minute) { ++active_minute; bins[active_minute%1440]=Bin{}; }
    }
public:
    float pm_mean=NAN,co_mean=NAN,coverage=0,index=NAN;
    uint64_t window_end_ms=0;
    void update(uint64_t now,float pm,float co,bool valid) {
        if (!initialized) { initialized=true; active_minute=now/60000; previous=now; }
        if (now<previous) return;
        // Publish before evicting oldest minute at each boundary.
        if (now/60000>active_minute) {
            if (now-previous<=1500 && previous_valid) {
                const uint64_t end=(active_minute+1)*60000;
                if (previous<end) add(previous_pm,previous_co,uint32_t(end-previous));
            }
            if (now/60000==active_minute+1) summarize((active_minute+1)*60000);
            else { index=pm_mean=co_mean=NAN; coverage=0; }
            advance(now/60000);
            if (now-previous<=1500 && previous_valid)
                add(previous_pm,previous_co,uint32_t(now-active_minute*60000));
        } else if (now>previous && now-previous<=1500 && previous_valid)
            add(previous_pm,previous_co,uint32_t(now-previous));
        previous=now; previous_pm=pm; previous_co=co;
        previous_valid=valid && std::isfinite(pm) && std::isfinite(co) && pm>=0 && co>=0;
    }
private:
    void add(float pm,float co,uint32_t ms) {
        auto &b=bins[active_minute%1440];b.pm+=double(pm)*ms;b.co+=double(co)*ms;b.valid_ms+=ms;
    }
    void summarize(uint64_t end) {
        double p=0,c=0;uint64_t ms=0;
        for (const auto &b:bins) {p+=b.pm;c+=b.co;ms+=b.valid_ms;}
        coverage=100.0*ms/86400000.0; window_end_ms=end;
        pm_mean=co_mean=index=NAN;
        if (end>=86400000ULL && ms>=64800000ULL) {
            pm_mean=p/ms;co_mean=c/ms;index=estimateIspu(pm_mean,co_mean).maximum;
        }
    }
};
}
