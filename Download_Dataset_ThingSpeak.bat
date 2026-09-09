@echo off
title Download snapshot ThingSpeak - Project Stuzha
python "%~dp0Program\download_thingspeak_dataset.py" %*
if errorlevel 1 (
  echo Download belum selesai. Arsip lama tetap dipertahankan.
) else (
  echo Snapshot baru disimpan pada lokasi yang tercetak di atas.
)
pause
