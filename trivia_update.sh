#!/bin/sh
md='03'
next_md='04'
s='64'

python2 update_sheet.py s md
sleep 1m
python2 update_schedule.py md
sleep 1m
python2 update_stats.py s md
sleep 1m
python2 retrieve_questions.py s next_md
