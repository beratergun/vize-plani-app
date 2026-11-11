#!/bin/bash
# Tüm otomatik testler: ./run_all.sh chromium|webkit   (önce 10_Website'te: py -m http.server 8765 --bind 127.0.0.1)
export PYTHONIOENCODING=utf-8
B=${1:-chromium}
cd "$(dirname "$0")"
py e2e_core.py $B
VTESTS=main,errors,resources py e2e_viewer.py $B
TESTS=search,backup,import py e2e_features.py $B
FREEZE=2026-11-09T12:00:00+03:00 TESTS=planner py e2e_features.py $B
