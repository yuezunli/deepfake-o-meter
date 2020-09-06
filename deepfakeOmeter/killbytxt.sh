#!/bin/bash

for line in `cat $1`
do
    echo $line
    PID=$(netstat -nlp | grep ":$line" | awk '{print $7}' | awk -F '[ / ]' '{print $1}')

    if [ $? = 0 ]; then
            echo "process id is:${PID}"
    else
            echo "process $line no exit"
            exit 0
    fi

    kill -9 ${PID}

    if [ $? = 0 ]; then
            echo "kill $line success"
    else
            echo "kill $line fail"
    fi

done

