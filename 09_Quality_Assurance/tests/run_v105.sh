#!/bin/bash
cd "$(dirname "$0")"; export PYTHONIOENCODING=utf-8; T=/c/Users/berat/AppData/Local/Temp; rm -f $T/v105_done.flag
(cd ../../08_Scripts && rm -rf $T/vp_pwa && mkdir -p $T/vp_pwa && py build_repo.py "C:/Users/berat/AppData/Local/Temp/vp_pwa" > $T/v105_repo.log 2>&1)
for B in chromium webkit; do
 py e2e_v105.py "C:/Users/berat/AppData/Local/Temp/vp_pwa" $B > $T/v105_v105_$B.log 2>&1
 py e2e_v104.py "C:/Users/berat/AppData/Local/Temp/vp_pwa" $B > $T/v105_v104_$B.log 2>&1
 py e2e_v103.py $B > $T/v105_v103_$B.log 2>&1
 py e2e_v102.py $B > $T/v105_v102_$B.log 2>&1
 py e2e_v101.py $B > $T/v105_v101_$B.log 2>&1
 if [ $B = chromium ]; then py e2e_studio.py $B all > $T/v105_studio_$B.log 2>&1; py e2e_slide.py $B all > $T/v105_slide_$B.log 2>&1; else py e2e_studio.py $B > $T/v105_studio_$B.log 2>&1; py e2e_slide.py $B > $T/v105_slide_$B.log 2>&1; fi
 ./run_all.sh $B > $T/v105_all_$B.log 2>&1
 py e2e_local.py $B http://127.0.0.1:8790/ > $T/v105_local_$B.log 2>&1
 py e2e_csp.py $B > $T/v105_csp_$B.log 2>&1
 py e2e_pwa.py "C:/Users/berat/AppData/Local/Temp/vp_pwa" $B > $T/v105_pwa_$B.log 2>&1
 [ $B = chromium ] && py e2e_prep453.py $B http://127.0.0.1:8790/ > $T/v105_prep_$B.log 2>&1
done
echo done > $T/v105_done.flag
