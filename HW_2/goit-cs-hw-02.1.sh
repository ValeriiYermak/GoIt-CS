#!/bin/bash

#The list of websites for checking

websites=("https://google.com" "https://facebook.com" "https://twitter.com" "https://www.ukr.net" "https://www.yahoo.com")

# The file for logging

log_file="website_status.log"

# Cleaning the log file before starting

> "$log_file"

# The loop for each site

for website in "${websites[@]}"; do
    # Do curl for checking availability ofsite
    http_response=$(curl -s -L -o /dev/null -w "%{http_code}" "$website")
    echo "Response code for $website: $http_response"

    if [ "$http_response" -eq 200 ]; then
        # If status_cod 200, sait is available
        echo "$website is UP" >> "$log_file"
    else
    # if status_cod not 200 the site is not available
        echo "$website is DOWN" >> "$log_file"
    fi
done

# the announcement about finishing the script
echo "The results of checking have been saved to the log file: $log_file"


