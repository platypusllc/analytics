import sys
import csv
from csv import DictWriter, DictReader
from dateutil import parser
import datetime
import os
import glob
import append_csvs

def get_poses(filename_poses, pose_offset):
    poses = []
    with open(filename_poses) as csvfile:
        reader = DictReader(csvfile)
        print "pose offset: " + str(pose_offset)
        last_row = {"time": 0, "latitude": 0, "longitude": 0}
        for row in reader:
            dt = parser.parse(row["time"]) + datetime.timedelta(hours = pose_offset)
            if (last_row["latitude"] == row["latitude"] and last_row["longitude"] == row["longitude"] and abs(last_row["time"] - dt) < datetime.timedelta(seconds = 1)):
                continue
            row["time"] = dt
            poses.append(row)
            last_row = row

        print "first point: " + str(poses[0]) +"\nLast point: "+ str(poses[-1])+"\nnum points: "+str(len(poses))+"\n\n"
    return poses

def fix_insitu_csv(filename_insitu, poses, output_filename):
    with open(filename_insitu) as csvfile:
        reader = DictReader(csvfile)

        with open(output_filename, 'w') as csvoutfile:
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(csvoutfile, fieldnames=fieldnames)
            writer.writeheader()
            print "insitu data: "
            for row in reader:
                # print(row)
                insitu_date = parser.parse(row['Date Time'])
                latest_time_diff = 0
                min_val = min(poses, key=lambda x:abs(x["time"]-insitu_date))
                # for x in poses:
                #     pose_date = x["time"]
                #     if (pose_date > insitu_date):
                #         print "found a pose after " + str(pose_date) + " for insitu data point: " + str(insitu_date) + " - diff = " + str(abs(insitu_date -pose_date))
                diff_time = abs(insitu_date - min_val["time"])
                if (diff_time > datetime.timedelta(seconds = 1)):
                    print "found the closest pose (" + str(min_val) + ") for insitu data point: " + str(insitu_date) + " - diff = " + str(diff_time)

                row['Date Time'] = min_val["time"]
                row['Latitude'] = min_val["latitude"]
                row['Longitude'] = min_val["longitude"]
                writer.writerow(row)

if __name__ == '__main__':
    filename_poses = sys.argv[1]
    pose_offset = int(sys.argv[2])
    filename_insitu = sys.argv[3]
    if (os.path.exists(filename_insitu) == False):
        print("file doesn't exist: "+filename_insitu)

    "filename of poses: ", filename_poses
    dict_poses = get_poses(filename_poses, pose_offset)
    
    if (os.path.isdir(filename_insitu)):
        files_in_folder = glob.glob(filename_insitu+'/VuSitu_*.csv')
    else:
        files_in_folder = [filename_insitu]


    files_output = []

    for x in files_in_folder:
        print "filename of insitu data: ", x
        fix_insitu_csv(x, dict_poses, x+".fixed")
        files_output.append(x + ".fixed")

    if os.path.isdir(filename_insitu):
        append_csvs(files = files_output, output_filename = filename_insitu + "/combined.csv")