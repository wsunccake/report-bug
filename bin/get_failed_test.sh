#!/usr/bin/env sh

if [ -z $REPORT_BUG_HOME ]; then
#    echo "please setup environment variable REPORT_BUG_HOME"
#    exit 1
  REPORT_BUG_HOME=$(cd $(dirname "$0")/.. && pwd -P)
  CMD=${0##*/}
fi

export PYTHONPATH=$REPORT_BUG_HOME/lib:$PYTHONPATH

#echo "get_failed_test.py $@"
${REPORT_BUG_HOME}/bin/get_failed_test.py "$@"
