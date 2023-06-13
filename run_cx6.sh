#!/bin/bash

cecho(){  # source: https://stackoverflow.com/a/53463162/2886168
    RED="\033[0;31m"
    GREEN="\033[0;32m"
    YELLOW="\033[0;33m"
    # ... ADD MORE COLORS
    NC="\033[0m" # No Color

    printf "${!1}${2} ${NC}\n"
}

if [ $# -ne 1 ];then
	cecho "YELLOW" "Usage: $0 <tx/rx>"
	exit 1
fi

mode=$1 # either "tx" or "rx"

ulimit -s unlimited

if [ "$mode" = "rx"  ]; then
    cecho "GREEN" "Run CX6 Server forever"
    while true
    do
    ./bin/rdma_server -a 10.2.2.2
    done
elif [ "$mode" = "tx" ]; then
	cecho "GREEN" "Run CX6 Client forever"
    while true
    do
    ./bin/rdma_client -a 10.2.2.2 -f /src/24387B.txt -l /log/test.txt -n 1
    exit
    done
else
	cecho "RED" "Invalid command: ${mode}"
	exit 1
fi
