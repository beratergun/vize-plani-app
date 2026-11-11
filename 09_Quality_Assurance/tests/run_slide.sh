#!/bin/bash
cd "$(dirname "$0")"; export PYTHONIOENCODING=utf-8; T=/c/Users/berat/AppData/Local/Temp
py e2e_slide.py chromium all > $T/sl_slide_chromium.log 2>&1
py e2e_slide.py webkit > $T/sl_slide_webkit.log 2>&1
./run_all.sh chromium > $T/sl_chromium.log 2>&1
py e2e_local.py chromium http://127.0.0.1:8790/ > $T/sl_local_chromium.log 2>&1
py e2e_prep453.py chromium http://127.0.0.1:8790/ > $T/sl_prep_chromium.log 2>&1
./run_all.sh webkit > $T/sl_webkit.log 2>&1
py e2e_local.py webkit http://127.0.0.1:8790/ > $T/sl_local_webkit.log 2>&1
echo done > $T/sl_done.flag
