#!/bin/bash
while [ 1 ]
do
    cp -n -r ~/mount_nas/ERM/phone\ \#2/ ~/backup_ERM
    cp -n -r ~/mount_nas/ERM/phone\ \#1/ ~/backup_ERM
    cp -n ~/mount_nas/ERM/*txt* ~/backup_ERM
    
    rm -r ~/process_ERM/
    mkdir -p ~/process_ERM/
    cp -n ~/mount_nas/ERM/phone\ \#2/* ~/process_ERM/
    cp -n ~/mount_nas/ERM/phone\ \#1/* ~/process_ERM/
    cp -n ~/mount_nas/ERM/*txt* ~/process_ERM/

    for filename in ~/process_ERM/*; do
        if [[ $(find "$filename" -mtime +10 -print) ]]; then
            echo "skipping old file: $filename"
	 #   sleep 0.5
        #    continue
	fi        
        for ((i=0; i<=3; i++)); do
            python data_processor.py "$filename" "$i" 5000 1000000 6 10.5
	done

    done
    echo "Done for now"
    sleep 3600
done
