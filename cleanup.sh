#!/bin/bash

# Check if an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

# Check if the file exists
if [ ! -f "$1" ]; then
    echo "Error: File '$1' not found!"
    exit 2
fi

# Use the sed command to strip timestamps,
# uniq it,
# and output to terminal
sed -E 's/\[.*\]   //g' "$1" | uniq
