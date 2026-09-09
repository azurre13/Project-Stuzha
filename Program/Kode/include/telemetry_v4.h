#pragma once
#include <array>
#include <cstdio>
#include <cstdint>
#include <cstddef>
namespace stuzha {
inline std::array<float,8> cloudFieldsV4(float t,float rh,float pm,float co_ppm,
                                       float index,float pwm,float mq135,int category) {
    return {{t,rh,pm,co_ppm,index,pwm,mq135,float(category)}};
}
struct StatusV4 {
    const char *version,*build,*models,*boot;
    uint64_t uptime;
    uint32_t reset,level,flags,seq,n,j,infer,attempts,failed,skipped,slot,heap;
    float gp,mq7,pm24,co24,index24,coverage;
    int critical;
};
inline int formatStatusV4(char *buffer,size_t size,const StatusV4 &s) {
    return snprintf(buffer,size,
        "STZ4|v=%s|h=%s|m=%s|b=%s|u=%llu|r=%lu|l=%lu|f=%lu|s=%lu|n=%lu|j=%lu|i=%lu|e=%lu,%lu,%lu|q=%lu|k=%lu|a=%.2f,%.2f|d=%.3g,%.3g,%.3g,%.3g|c=%d",
        s.version,s.build,s.models,s.boot,(unsigned long long)s.uptime,
        (unsigned long)s.reset,(unsigned long)s.level,(unsigned long)s.flags,(unsigned long)s.seq,
        (unsigned long)s.n,(unsigned long)s.j,(unsigned long)s.infer,(unsigned long)s.attempts,
        (unsigned long)s.failed,(unsigned long)s.skipped,(unsigned long)s.slot,(unsigned long)s.heap,
        s.gp,s.mq7,s.pm24,s.co24,s.index24,s.coverage,s.critical);
}
}
