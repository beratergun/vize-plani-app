#!/bin/bash
cd "$(dirname "$0")"; export PYTHONIOENCODING=utf-8; T=/c/Users/berat/AppData/Local/Temp; rm -f $T/v103_done.flag
(cd ../../08_Scripts && rm -rf $T/vp_pwa && mkdir -p $T/vp_pwa && py build_repo.py "C:/Users/berat/AppData/Local/Temp/vp_pwa" > $T/v103_repo.log 2>&1)
for B in chromium webkit; do
 py e2e_v103.py $B > $T/v103_v103_$B.log 2>&1
 py e2e_v102.py $B > $T/v103_v102_$B.log 2>&1
 py e2e_v101.py $B > $T/v103_v101_$B.log 2>&1
 if [ $B = chromium ]; then py e2e_studio.py $B all > $T/v103_studio_$B.log 2>&1; py e2e_slide.py $B all > $T/v103_slide_$B.log 2>&1; else py e2e_studio.py $B > $T/v103_studio_$B.log 2>&1; py e2e_slide.py $B > $T/v103_slide_$B.log 2>&1; fi
 ./run_all.sh $B > $T/v103_all_$B.log 2>&1
 py e2e_local.py $B http://127.0.0.1:8790/ > $T/v103_local_$B.log 2>&1
 py e2e_csp.py $B > $T/v103_csp_$B.log 2>&1
 py e2e_pwa.py "C:/Users/berat/AppData/Local/Temp/vp_pwa" $B > $T/v103_pwa_$B.log 2>&1
 [ $B = chromium ] && py e2e_prep453.py $B http://127.0.0.1:8790/ > $T/v103_prep_$B.log 2>&1
done
echo done > $T/v103_done.flag
