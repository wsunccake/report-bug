#!/usr/bin/env sh

if [ -z $REPORT_BUG_HOME ]; then
  REPORT_BUG_HOME=$(cd $(dirname "$0")/.. && pwd -P)
  CMD=${0##*/}
fi

export PYTHONPATH=$REPORT_BUG_HOME/lib:$PYTHONPATH

echo "${REPORT_BUG_HOME}/bin/$@"
${REPORT_BUG_HOME}/bin/$@
