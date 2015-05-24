# Scripts for log analysis

loganalytics.py calculates 95th percentile for request time and shows top 10 requests ID with max send time to customers.

granalytics.py shows number of partially merged requests and gives complete statistics of connections/errors for each backend groups

## Start example:
Make scripts executable with 'chmod +x' and then run them

    ./loganalytics.py /path-to-log/input.txt > /path-to-some-dir/output.txt
    ./granalytics.py /path-to-log/input.txt >> /path-to-some-dir/output.txt

If you do not set path to log, then default location will be used (/home/bi4o4ek/yaTest/input.txt)

## TODO
Add some multiprocessing
