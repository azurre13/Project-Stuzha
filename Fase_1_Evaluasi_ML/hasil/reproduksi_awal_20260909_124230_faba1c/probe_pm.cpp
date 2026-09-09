#include <cstdio>
#include "C:/Users/daffa/Documents/Project Stuzha/Program/Kode/include/model_pm.h"
int main(){float x[3];while(scanf("%f %f %f",&x[0],&x[1],&x[2])==3)printf("%.9g\n",model_pm_predict(x));}
