#!/bin/bash
i=$(($1+1))
if [ $1 ]; then
    ./orakel.py $1 2010 --results > results
    ./orakel.py $i 2010 --pairs > input
    ./main.py --verify $1 < results
    ./main.py --predict $i < input 
else
    echo "usage: ./makeitso.sh <spieltag>"
fi