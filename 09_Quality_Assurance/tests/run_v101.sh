#!/bin/bash
cd "$(dirname "$0")"; export PYTHONIOENCODING=utf-8; T=/c/Users/berat/AppData/Local/Temp; rm -f $T/v101_done.flag
py e2e_v101.py chromium > $T/v101_chromium.log 2>&1
py e2e_v101.py webkit > $T/v101_webkit.log 2>&1
py e2e_studio.py chromium all > $T/v101_studio_chromium.log 2>&1
py e2e_studio.py webkit > $T/v101_studio_webkit.log 2>&1
py e2e_slide.py chromium all > $T/v101_slide_chromium.log 2>&1
py e2e_slide.py webkit > $T/v101_slide_webkit.log 2>&1
./run_all.sh chromium > $T/v101_chromium_all.log 2>&1
py e2e_local.py chromium http://127.0.0.1:8790/ > $T/v101_local_chromium.log 2>&1
py e2e_prep453.py chromium http://127.0.0.1:8790/ > $T/v101_prep_chromium.log 2>&1
./run_all.sh webkit > $T/v101_webkit_all.log 2>&1
py e2e_local.py webkit http://127.0.0.1:8790/ > $T/v101_local_webkit.log 2>&1
py e2e_csp.py chromium > $T/v101_csp_chromium.log 2>&1
echo done > $T/v101_done.flag
