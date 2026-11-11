#!/bin/bash
cd "$(dirname "$0")"; export PYTHONIOENCODING=utf-8; T=/c/Users/berat/AppData/Local/Temp
./run_all.sh chromium > $T/v8_chromium.log 2>&1
py e2e_local.py chromium http://127.0.0.1:8790/ > $T/v8_local_chromium.log 2>&1
py e2e_local.py webkit http://127.0.0.1:8790/ > $T/v8_local_webkit.log 2>&1
./run_all.sh webkit > $T/v8_webkit.log 2>&1
echo done > $T/v8_done.flag
