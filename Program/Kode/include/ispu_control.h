#pragma once
#include "ispu_calc.h"
#include <algorithm>
#include <cstdint>
namespace stuzha {
// Check elapsed acquisition age even when no new frame reaches the main loop.
inline bool acquisitionStale(uint64_t now, uint64_t frame_time) {
    return now < frame_time || now - frame_time > 2500;
}
// No boot-relative baseline. Decisions remain on the same nominal index scale.
class IspuControl {
public:
    int level=1;
    bool pollution_alarm=false;
    void update(float index, bool valid, bool optical_saturated, uint64_t now) {
        const bool contiguous = last && now>last && now-last<=2500;
        if (!contiguous) { rising_since=0; down_since=0; }
        last=now;
        if (optical_saturated || !valid || !std::isfinite(index)) {
            level=optical_saturated ? 5 : std::max(level,4);
            pollution_alarm=false; // Acquisition fault/obstruction is not proven pollution.
            rising_since=down_since=0;
            return;
        }
        const int target=categoryCode(index);
        if (target>level) {
            down_since=0;
            if (!rising_since) { rising_since=now; rising_level=target; }
            // A new higher spike cannot borrow a lower category's dwell time.
            rising_level=std::min(rising_level,target);
            if (now-rising_since>=1000) { level=rising_level; rising_since=0; }
        } else {
            rising_since=0;
            const float thresholds[]={0,50,100,200,300};
            if (level>1 && index<thresholds[level-1]*0.95f) {
                if (!down_since) down_since=now;
                if (now-down_since>=8000) { --level; down_since=0; }
            } else down_since=0;
        }
        // Alarm follows CURRENT valid index, not the delayed descending fan level.
        pollution_alarm=target>=4 && level>=4;
    }
private:
    uint64_t rising_since=0,down_since=0,last=0;
    int rising_level=1;
};
}
