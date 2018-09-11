#!/bin/bash
while [ 1 ]
do
    # python data_processor.py ~/mount_nas/ -1 5000 1000000 5 12

    for filename in ~/mount_nas/*.txt; do
        for ((i=0; i<=3; i++)); do
            python data_processor.py "$filename" "$i" 5000 1000000 6 10.5
        done
    done

    for filename in "~/mount_nas/phone 2/*.txt"; do
        for ((i=0; i<=3; i++)); do
            python data_processor.py "$filename" "$i" 5000 1000000 6 10.5
        done
    done

    sleep 3600
done
