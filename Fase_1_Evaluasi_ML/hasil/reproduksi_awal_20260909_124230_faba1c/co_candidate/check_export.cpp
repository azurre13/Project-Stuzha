#include <cstdio>
#include "benchmark_model.h"
int main(){float x[3]; while(scanf("%f %f %f", &x[0], &x[1], &x[2])==3) printf("%.17g\n", benchmark_predict(x));}
