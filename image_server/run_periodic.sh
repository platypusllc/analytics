#!/bin/bash
while [ 1 ]
do
    python data_processor.py ~/mount_nas/ -1 5000 1000000 5 12
    sleep 60
done
