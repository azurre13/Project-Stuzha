# Arsip firmware sebelum v3

Firmware aktif berada di [main.cpp](../src/main.cpp). Folder ini tidak termasuk sumber build PlatformIO.

- kode_program_lama.cpp: implementasi historis dengan MQ2/eCO2; bukan identitas sensor yang terpasang sekarang.
- ispu_calc_v2.h: tabel/perhitungan sesaat v2, termasuk satuan CO yang tidak konsisten. Dipertahankan sebagai arsip; tidak dipakai atau dinyatakan sesuai pelaporan ISPU.

Sensor aktif yang dikonfirmasi pemilik adalah MQ7 dan MQ135. Keduanya dicatat sebagai respons analog pada v3. Header RF historis tetap berada di include; pada v4 sub-indeks dari keluaran model nominal mengendalikan PWM dan ditampilkan bersama raw. Ini tidak memvalidasi konsentrasi atau kategori kesehatan. Riwayat kode v2 sebelum revisi tersedia di Git, bukan bukti versi fisik yang terpasang.

Perhitungan aktif yang diperbaiki berada di ../include/ispu_calc.h. File ispu_calc_v2.h di folder ini tetap arsip tabel CO lama yang berbeda dari regulasi; jangan menggunakannya kembali.
