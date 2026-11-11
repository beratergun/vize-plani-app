#!/bin/bash
cd "$(dirname "$0")"; export PYTHONIOENCODING=utf-8
T=/c/Users/berat/AppData/Local/Temp
./run_all.sh chromium > $T/final_chromium.log 2>&1
./run_all.sh webkit > $T/final_webkit.log 2>&1
py csp_server.py 8766 & SP=$!
sleep 2
VTESTS=main,errors py e2e_viewer.py chromium http://127.0.0.1:8766/index.html > $T/final_csp.log 2>&1
kill $SP
echo done > $T/final_done.flag
