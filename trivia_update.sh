#!/bin/sh
md='03'
next_md='04'
our_md='01'
s='64'

python2 update_sheet.py $s $md $our_md
python2 update_schedule.py $our_md
python2 update_stats.py $s $md
python2 retrieve_questions.py $s $next_md
