#!/bin/bash

PROJECT_ROOT=$(dirname $0)
cd $PROJECT_ROOT

# remove logs
if [ -d $PROJECT_ROOT/scrappers/logs/ ]; then
    rm -r $PROJECT_ROOT/scrappers/logs/
    echo "logs removed"
fi

# remove generated files. Add more patterns when new test cases added.
cd tests/
files=$(ls | grep -v -E "(utils|__init__)")
if [ ${#files} != 0 ];then
    echo $files | xargs rm -r
fi
