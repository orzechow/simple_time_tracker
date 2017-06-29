#!/usr/bin/python3

import time
import os
import subprocess
import argparse


# parse command line arguments
parser = argparse.ArgumentParser(description='Tracks working time based on your first login time after 5am.')
parser.add_argument('-v', '--verbose', action='store_true', help='print stats')

args = parser.parse_args()


current_timestamp = time.time()
logfolder_name = os.path.expanduser("~") + "/.log/activity"

# day begins at 5 am (to count night sessions into "previous" day)
logfile_name = logfolder_name \
               + "/" \
               + time.strftime("%Y-%m-%d", time.localtime(current_timestamp - 5*60*60)) \
               + ".log"

try:
    os.mkdir(logfolder_name)
except:
    pass

with open(logfile_name, "a+") as logfile:
    locked_screen = str(int(subprocess.check_output("ps -e | grep screenlocker | wc -l", shell=True)))
    new_line = time.strftime("%Y-%m-%d %H:%M", time.localtime(current_timestamp)) \
               + "; " + locked_screen \
               + os.linesep
    logfile.write(new_line)

    logfile.seek(0)
    first_line = logfile.readline()
    start_timestamp = time.mktime(time.strptime(first_line.split("; ")[0], "%Y-%m-%d %H:%M"))


# produce a warning dialog every 30 min, if working longer than 8 hours (assumes cronjob every minute, 1 hour lunch break)
working_time = (current_timestamp - start_timestamp) / (60 * 60)

if args.verbose:
    print(time.strftime("start: %Y-%m-%d %H:%M", time.localtime(start_timestamp)),
          time.strftime("start: %Y-%m-%d %H:%M", time.localtime(current_timestamp)),
          "working time:",
          working_time,
          " (incl. lunch break)")

#print(start_timestamp, current_timestamp, working_time)

if working_time > 8 + 1 and working_time % 0.5 == 0.0:
    active_window = subprocess.check_output("xdotool getwindowfocus", shell=True)
    subprocess.check_call("kdialog --sorry 'You are already working more than "
                          + ("%0.1f" % working_time)
                          + " hours!\n\nTime to go home :-)' --attach "
                          + active_window
                          , shell=True)
