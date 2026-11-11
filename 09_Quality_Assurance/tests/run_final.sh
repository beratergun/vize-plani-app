#!/bin/bash
cd "$(dirname "$0")"; export PYTHONIOENCODING=utf-8; T=/c/Users/berat/AppData/Local/Temp
./run_all.sh chromium > $T/fin_chromium.log 2>&1
py e2e_local.py chromium http://127.0.0.1:8790/ > $T/fin_local_chromium.log 2>&1
py e2e_local.py webkit http://127.0.0.1:8790/ > $T/fin_local_webkit.log 2>&1
py e2e_prep453.py chromium http://127.0.0.1:8790/ > $T/fin_prep_chromium.log 2>&1
py e2e_prep453.py webkit http://127.0.0.1:8790/ > $T/fin_prep_webkit.log 2>&1
py e2e_core.py webkit > $T/fin_core_webkit.log 2>&1
echo done > $T/fin_done.flag
