#!/bin/bash 
#awk -F '\t' '{arr[$1]+=$2} END {for (i in arr) {print i,arr[i]}}' beers.txt | awk '{print $NF,$0}' |  sort -nr | cut -f2- -d' ' | head -n 10

## The first one counts the total score per beer, it is fun, but its not what required,
## but it was too good to be just forgotten

# Here's the pipeline for counting top 10 most reviewed beers
cut -f 1 beers.txt | sort | uniq -c | sort -g -k1 -r | head -n 10

