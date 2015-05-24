#!/usr/bin/python
# -*- coding: utf-8 -*-
# This script calculates 95th percentile for request time and shows top 10 requests ID with max send time to customers
#
# Start example:
# ./loganalytics.py /path-to-log/input.txt > /path-to-some-dir/output.txt
# then you can complete analysis by running 2nd script
# ./granalytics.py /path-to-log/input.txt >> /path-to-some-dir/output.txt
#
# If you do not set path to log, then default location will be used (default_log_path)

import sys
import math
import heapq

__author__ = 'Vladimir Bykanov'
default_log_path = '/home/bi4o4ek/yaTest/input.txt'

# Pure python func for percentile calculation
# http://code.activestate.com/recipes/511478-finding-the-percentile-of-the-values/
def percentile(N, percent, key=lambda x: x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return None
    k = (len(N) - 1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c - k)
    d1 = key(N[int(c)]) * (k - f)
    return d0 + d1

# Dict with id:timestamp of type StartRequest
start_stamps = {}
# Dict with id:timestamp of type StartSendResult
send_stamps = {}
# Dict with id:timestamp of type FinishRequest
finish_stamps = {}
# List with send time of each request
send_times = {}
# List with full time of each request
req_times = []

# Read log path from 1st script parameter
if len(sys.argv) > 1:
    log_path = sys.argv[1]
else:
    log_path = default_log_path

# Parse log and harvest info into start_stamps, send_stamps and finish_stamps
with open(log_path) as log_handler:
    for line in log_handler:
        line_elements = line.split()
        req_stamp, req_id, req_type = line_elements[:3]

        if req_type == 'StartRequest':
            start_stamps[req_id] = int(req_stamp)

        elif req_type == 'StartSendResult':
            send_stamps[req_id] = int(req_stamp)

        elif req_type == 'FinishRequest':
            finish_stamps[req_id] = int(req_stamp)

# Numbers of StartRequest, StartSendResult and FinishRequest must be equal
if len(start_stamps) != len(finish_stamps) or len(finish_stamps) != len(send_stamps) :
    print 'Numbers of StartRequest, StartSendResult and FinishRequest are not equal each other'
    exit(3)

# Compute full times of requests and send times to customer
for req_id in start_stamps:
    # Full times
    req_time = int(finish_stamps[req_id]) - int(start_stamps[req_id])
    req_times.append(req_time)

    # Send times
    send_time = int(finish_stamps[req_id]) - int(send_stamps[req_id])
    send_times[req_id] = send_time


req_times.sort()
print "95-й перцентиль времени работы:", percentile(req_times, 0.95)

send_times_top10 = heapq.nlargest(10, send_times, key = send_times.get)
print "Идентификаторы запросов с самой долгой фазой отправки результатов пользователю:"
print '    ', ', '.join(map(str, send_times_top10))
