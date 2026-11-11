#!/bin/bash
cd "$(dirname "$0")"; export PYTHONIOENCODING=utf-8; T=/c/Users/berat/AppData/Local/Temp; rm -f $T/v102_done.flag
for B in chromium webkit; do
 py e2e_v101.py $B > $T/v102_v101_$B.log 2>&1
 if [ $B = chromium ]; then py e2e_studio.py $B all > $T/v102_studio_$B.log 2>&1; py e2e_slide.py $B all > $T/v102_slide_$B.log 2>&1; else py e2e_studio.py $B > $T/v102_studio_$B.log 2>&1; py e2e_slide.py $B > $T/v102_slide_$B.log 2>&1; fi
 ./run_all.sh $B > $T/v102_all_$B.log 2>&1
 py e2e_local.py $B http://127.0.0.1:8790/ > $T/v102_local_$B.log 2>&1
 py e2e_csp.py $B > $T/v102_csp_$B.log 2>&1
 [ $B = chromium ] && py e2e_prep453.py $B http://127.0.0.1:8790/ > $T/v102_prep_$B.log 2>&1
done
echo done > $T/v102_done.flag
