#!/bin/bash
SCRIPTPATH=$(cd $(dirname $0); pwd -P)
DISPLAY=:0 "$SCRIPTPATH/cron_callback.py" "$@"
