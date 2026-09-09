#include "../Program/Kode/include/ispu_control.h"
#include "../Program/Kode/include/rolling_ispu.h"
#include "../Program/Kode/include/experimental_models.h"
#include "../Program/Kode/include/telemetry_v4.h"
#include <cassert>
#include <cstring>
#include <iostream>
using namespace stuzha;
int main() {
    for (int i=0;i<6;++i) {
        assert(std::abs(interpolateIspu(PM_POINTS[i],PM_POINTS)-ISPU_POINTS[i])<0.001);
        assert(std::abs(interpolateIspu(CO_POINTS_UG[i],CO_POINTS_UG)-ISPU_POINTS[i])<0.001);
    }
    assert(std::lround(estimateIspu(31.4f,1.6f).maximum)==70); // Regulation worked example.
    assert(estimateIspu(1,8).critical==2 && estimateIspu(1,8).category==2);
    assert(estimateIspu(55.4f,0).critical==1);
    assert(std::isnan(estimateIspu(NAN,1).maximum));
    assert(estimateIspu(501,0).above_range);
    assert(std::abs(coPpmToMg(coMgToPpm(8))-8)<0.00001);
    assert(categoryCode(50)==1 && categoryCode(51)==2 && categoryCode(101)==3 && categoryCode(201)==4 && categoryCode(301)==5);
    assert(!acquisitionStale(2500,0) && acquisitionStale(2501,0));
    assert(!acquisitionStale(4294969000ULL,4294968000ULL));
    assert(acquisitionStale(4294971001ULL,4294968000ULL));
    assert(acquisitionStale(1000,2000));
    IspuControl spike;
    spike.update(60,true,false,1000);
    spike.update(400,true,false,2000);
    assert(spike.level==2 && !spike.pollution_alarm); // A one-frame L5 spike cannot borrow L2 dwell.
    spike.update(60,true,false,3000); assert(spike.level==2);
    spike.update(400,true,false,4000); spike.update(400,true,false,5000);
    assert(spike.level==5 && spike.pollution_alarm);
    spike.update(NAN,false,false,7501);
    assert(spike.level==5 && !spike.pollution_alarm); // A fault never reduces an already high command.
    IspuControl stopped;
    stopped.update(NAN,false,false,2501); assert(stopped.level==4 && !stopped.pollution_alarm);
    for(uint64_t t=3000;t<=30000;t+=1000) stopped.update(10,true,false,t);
    assert(stopped.level==1);
    IspuControl c;
    c.update(400,true,false,1000); assert(c.level==1);
    c.update(400,true,false,2000); assert(c.level==5 && c.pollution_alarm);
    for(uint64_t t=3000;t<=39000;t+=1000) c.update(10,true,false,t);
    assert(c.level==1 && !c.pollution_alarm); // No 90-second latch.
    c.update(NAN,false,true,40000); assert(c.level==5 && !c.pollution_alarm);
    for(uint64_t t=41000;t<=78000;t+=1000) c.update(10,true,false,t);
    assert(c.level==1 && !c.pollution_alarm);
    c.update(400,true,false,79000);c.update(400,true,false,80000);
    c.update(195,true,false,81000);c.update(195,true,false,82000);
    assert(c.level==5 && !c.pollution_alarm); // Fan hysteresis never latches alarm.
    c.update(10,true,false,83000); c.update(10,true,false,100000);
    assert(c.level==5); // An unobserved gap cannot satisfy dwell.
    IspuControl wrap;
    wrap.update(400,true,false,4294967000ULL);wrap.update(400,true,false,4294968000ULL);
    for(uint64_t t=4294969000ULL;t<=4295006000ULL;t+=1000)wrap.update(10,true,false,t);
    assert(wrap.level==1);
    const auto high=predictExperimental(4001,3000,25,50);
    assert(high.valid()); // >4000 is not automatically a hardware failure.
    assert(estimateIspu(high.pm,high.co).category>=4);
    static RollingIspu r;
    for(uint64_t t=0;t<86400000ULL;t+=1000)r.update(t,31.4f,1.6f,true);
    assert(std::isnan(r.index));
    r.update(86400000ULL,31.4f,1.6f,true);
    assert(std::lround(r.index)==70 && r.coverage>99.99f);
    for(uint64_t t=86401000ULL;t<=7*86400000ULL;t+=1000) r.update(t,31.4f,1.6f,true);
    assert(std::lround(r.index)==70 && r.coverage>99.99f && r.coverage<=100.001f);
    // No fabricated samples when acquisition disappears for a day.
    r.update(8*86400000ULL+60000,31.4f,1.6f,true);
    assert(std::isnan(r.index));
    r.update(8*86400000ULL+120000,31.4f,1.6f,true);
    assert(std::isnan(r.index) && r.coverage<1);
    static RollingIspu sparse;
    for(uint64_t t=0;t<=86400000ULL;t+=1000) sparse.update(t,31.4f,1.6f,t<12*3600000ULL);
    assert(std::isnan(sparse.index) && sparse.coverage<51);
    auto fields=cloudFieldsV4(25,50,31.4f,coMgToPpm(1.6f),70,13,1600,2);
    assert(fields[4]==70 && fields[7]==2 && fields[2]==31.4f);
    StatusV4 meta{"4.0.0","123456789abc","12345678","12345678",691200000,255,5,65535,691200,
        110,110,1000000,34560,34560,34560,34560,327680,4095,4095,500,45,500,100,2};
    char buffer[256];int len=formatStatusV4(buffer,sizeof(buffer),meta);
    assert(len>0 && len<256 && strlen(buffer)==size_t(len));
    char short_buffer[16];assert(formatStatusV4(short_buffer,16,meta)>=16);
    std::cout<<"ISPU tables, gas units, categories, recovery, alarm, gap/rollover, actual RF and seven-day ring passed; status fixture "<<len<<" bytes\n";
}
