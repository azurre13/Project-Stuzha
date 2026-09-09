#ifndef ISPU_CALC_H
#define ISPU_CALC_H

#include <Arduino.h>

// ============================================================
// STANDAR ISPU INDONESIA (Permen LHK No. 14 Tahun 2020)
// ============================================================
// Rumus Interpolasi Linear:
// I = ((Ia - Ib) / (Xa - Xb)) * (Xx - Xb) + Ib
//
// Di mana:
// I  = ISPU terhitung
// Ia = ISPU batas atas
// Ib = ISPU batas bawah
// Xa = Konsentrasi batas atas (breakpoint)
// Xb = Konsentrasi batas bawah (breakpoint)
// Xx = Konsentrasi polutan terukur (terkalibrasi ML)
// ============================================================

struct Breakpoint {
    float Xb; // Konsentrasi batas bawah
    float Xa; // Konsentrasi batas atas
    int   Ib; // ISPU batas bawah
    int   Ia; // ISPU batas atas
};

// Breakpoint PM2.5 (24 Jam) — Satuan: µg/m³
// Kategori:
// 0 - 50   : 0.0 - 15.5 µg/m³ (Baik)
// 51 - 100 : 15.6 - 55.4 µg/m³ (Sedang)
// 101 - 200: 55.5 - 150.4 µg/m³ (Tidak Sehat)
// 201 - 300: 150.5 - 250.4 µg/m³ (Sangat Tidak Sehat)
// > 300    : >= 250.5 µg/m³ (Berbahaya)
static const Breakpoint BP_PM25[] = {
    {0.0f,   15.5f,   0,   50},
    {15.6f,  55.4f,  51,  100},
    {55.5f, 150.4f, 101,  200},
    {150.5f, 250.4f, 201, 300},
    {250.5f, 500.0f, 301, 500}
};

// Breakpoint CO (8 Jam) — Satuan: ppm (atau mg/m³ konversi standar)
// Kategori:
// 0 - 50   : 0.0 - 4.4 ppm
// 51 - 100 : 4.5 - 9.4 ppm
// 101 - 200: 9.5 - 15.4 ppm
// 201 - 300: 15.5 - 30.4 ppm
// > 300    : >= 30.5 ppm
static const Breakpoint BP_CO[] = {
    {0.0f,   4.4f,   0,   50},
    {4.5f,   9.4f,  51,  100},
    {9.5f,  15.4f, 101,  200},
    {15.5f, 30.4f, 201, 300},
    {30.5f, 50.0f, 301, 500}
};

inline int hitung_sub_ispu(float konsentrasi, const Breakpoint *bp, int n_bp) {
    if (konsentrasi <= 0.0f) return 0;

    for (int i = 0; i < n_bp; i++) {
        if (konsentrasi <= bp[i].Xa || i == n_bp - 1) {
            float Xb = bp[i].Xb;
            float Xa = bp[i].Xa;
            float Ib = (float)bp[i].Ib;
            float Ia = (float)bp[i].Ia;

            float ispu = ((Ia - Ib) / (Xa - Xb)) * (konsentrasi - Xb) + Ib;
            if (ispu < 0.0f) ispu = 0.0f;
            if (ispu > 500.0f) ispu = 500.0f;
            return (int)round(ispu);
        }
    }
    return 500;
}

inline int hitung_ispu_pm25(float pm25_ug) {
    return hitung_sub_ispu(pm25_ug, BP_PM25, sizeof(BP_PM25)/sizeof(BP_PM25[0]));
}

inline int hitung_ispu_co(float co_ppm) {
    return hitung_sub_ispu(co_ppm, BP_CO, sizeof(BP_CO)/sizeof(BP_CO[0]));
}

inline const char* get_kategori_ispu(int ispu) {
    if (ispu <= 50)  return "Baik";
    if (ispu <= 100) return "Sedang";
    if (ispu <= 200) return "Tidak Sehat";
    if (ispu <= 300) return "Sangat Tidak Sehat";
    return "Berbahaya";
}

#endif // ISPU_CALC_H
