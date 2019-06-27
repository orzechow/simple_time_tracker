#!/usr/bin/python3

import time
import os
import subprocess
import argparse


# constants
DATE_FORMAT = "%Y-%m-%d %H:%M"
ALERT_STRING = "alerted"
LUNCH_BREAK_DURATION = 1
INFO_WORKING_DURATION = 7
INFO_MESSAGE = "Time to finish open todos"
ALERT_WORKING_DURATION = 8
ALERT_MESSAGE = "Time to go home :-)"


# parse command line arguments
parser = argparse.ArgumentParser(description='Tracks working time based on your first login time after 5am.')
parser.add_argument('-v', '--verbose', action='store_true', help='print stats')
parser.add_argument('-f', '--force', action='store_true', help='force dialog pop-up')

args = parser.parse_args()


current_timestamp = time.time()
logfolder_name = os.path.expanduser("~") + "/.log/activity"

# day begins at 5 am (to count night sessions into "previous" day)
logfile_name = logfolder_name \
               + "/" \
               + time.strftime("%Y-%m-%d", time.localtime(current_timestamp - 5*60*60)) \
               + ".log"
symlink_name = logfolder_name + "/latest.log"

# create logfolder if it doesn't exist
try:
    os.mkdir(logfolder_name)
except:
    pass

# create "latest" symlink to logfile
try:
    os.remove(symlink_name)
except:
    pass
os.symlink(logfile_name, symlink_name)


last_alert = None
with open(logfile_name, "a+") as logfile:
    # log current time
    locked_screen = str(int(subprocess.check_output("ps -e | grep screenlocker | wc -l", shell=True)))
    new_line = time.strftime(DATE_FORMAT, time.localtime(current_timestamp)) \
               + "; " + locked_screen \
               + os.linesep
    logfile.write(new_line)

    # read start time
    logfile.seek(0)
    log = logfile.readlines()
    start_timestamp = time.mktime(time.strptime(log[0].split("; ")[0], DATE_FORMAT))

    # count alerts
    for logline in log:
        logline_arr = logline[:-1].split("; ")
        if len(logline_arr) > 2 and str(logline_arr[2]) == ALERT_STRING:
            last_alert = time.mktime(time.strptime(logline_arr[0], DATE_FORMAT))



# produce a warning dialog every 30 min, if working longer than 8 hours (assumes cronjob every minute, 1 hour lunch break)
working_time = (current_timestamp - start_timestamp) / (60 * 60)
time_since_last_alert = 9999999999
if last_alert is not None:
    time_since_last_alert = (current_timestamp - last_alert) / (60 * 60)

if args.verbose:
    print(time.strftime("start: " + DATE_FORMAT, time.localtime(start_timestamp)))
    print(time.strftime("current: " + DATE_FORMAT, time.localtime(current_timestamp)))
    print("working time:", working_time - 1., " (plus 1 hour est. lunch break)")
    print("time_since_last_alert:", time_since_last_alert)

if (working_time > min(INFO_WORKING_DURATION, ALERT_WORKING_DURATION) + LUNCH_BREAK_DURATION
    and time_since_last_alert >= 0.5) or args.force:

    dialog_already_open = int(subprocess.check_output("ps -fe | grep cron_callback.py | wc -l", shell=True)) > 3
    if args.verbose:
        print("dialog_already_open: ", dialog_already_open)#, " str:", dialog_already_open_str)

    if not dialog_already_open:
        message = ("You are already working more than %0.1f hours! (plus %0.1f hour est. lunch break)"
                   % (working_time - LUNCH_BREAK_DURATION, LUNCH_BREAK_DURATION))

        if working_time > ALERT_WORKING_DURATION + LUNCH_BREAK_DURATION:
            message += "\n\n" + ALERT_MESSAGE
        elif working_time > INFO_WORKING_DURATION + LUNCH_BREAK_DURATION:
            message += "\n\n" + INFO_MESSAGE

        active_window = str(int(subprocess.check_output("xdotool getwindowfocus", shell=True)))
        subprocess.check_call("kdialog --sorry '%s' --attach %s" % (message, active_window), shell=True)

        with open(logfile_name, "a") as logfile:
            # log the alert
            locked_screen = str(int(subprocess.check_output("ps -e | grep screenlocker | wc -l", shell=True)))
            new_line = time.strftime(DATE_FORMAT, time.localtime(current_timestamp)) \
                       + "; " + locked_screen \
                       + "; " + ALERT_STRING \
                       + os.linesep
            logfile.write(new_line)
