#!/bin/bash



#echo $pids

pid=$1
time=$2
result=$3

while true 
do  
      
     
    pids=`ps -ax | awk '{print $1}'`
    #echo $pids
    
    if echo "$pids" | grep -q "$pid" 
        then
        cat /proc/$pid/status |grep VmPeak >>$result
        sleep $time
    else
        break
    fi
    
    
done
