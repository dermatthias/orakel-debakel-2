#!/bin/bash
for i in `seq 1 34`; do ./orakel.py $i $1 --results > judge-data/$1/result$i; done
for i in `seq 1 34`; do ./orakel.py $i $1 --pairs > judge-data/$1/round$i; done