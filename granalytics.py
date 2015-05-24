#!/usr/bin/python
# -*- coding: utf-8 -*-
# This script shows number of partially merged requests
# and gives complete statistics of connections/errors for each backend groups
#
# Start example:
# ./loganalytics.py /path-to-log/input.txt > /path-to-some-dir/output.txt
# then you can complete analysis by running 2nd script
# ./granalytics.py /path-to-log/input.txt >> /path-to-some-dir/output.txt
#
# If you do not set path to log, then default location will be used (default_log_path)

import sys
from urlparse import urlparse
from collections import defaultdict

__author__ = 'Vladimir Bykanov'
default_log_path = '/home/bi4o4ek/yaTest/input.txt'

# Some dark magic to enable deep nested dicts
nested_dict = lambda: defaultdict(nested_dict)

# Dict with id1: { gr1: backend1 }
# It is necessary for backend tracking, because BackendError does not give us the backend name
backend_track = nested_dict()

# Dict with gr1:
#              { backend1:
#                   { connections: 4,
#                     { 'I/O Error': 3,
#                       'Connection error': 6,
#                     }
#                   }
#               }
# It is designed for error/connection count of backends
gr_backend_errors = nested_dict()

# Dict with id1:[gr1,gr2] for tracking of not merged groups
partially_merged = defaultdict(set)

# Read log path from 1st script parameter
if len(sys.argv) > 1:
    log_path = sys.argv[1]
else:
    log_path = default_log_path

with open(log_path) as log_handler:
    for line in log_handler:
        line_elements = line.split()
        req_stamp, req_id, req_type = line_elements[:3]

        if req_type == 'BackendConnect':
            req_gr, req_backend = line_elements[3:5]
            req_backend = urlparse(req_backend).netloc

            # Add id:{gr:backend} to backend_track.
            backend_track[req_id][req_gr] = req_backend

            # Increment backend connections in gr_backend_errors
            gr_backend_errors[req_gr][req_backend].setdefault('connections',0)
            gr_backend_errors[req_gr][req_backend]['connections'] += 1

            # Add gr to partially_merged
            partially_merged[req_id].add(req_gr)

        elif req_type == 'BackendError':
            req_gr = line_elements[3]
            req_error = ' '.join(line_elements[4:])

            # Put error info about backend to gr_backend_errors
            req_backend = backend_track[req_id][req_gr]
            gr_backend_errors[req_gr][req_backend].setdefault(req_error,0)
            gr_backend_errors[req_gr][req_backend][req_error] += 1

            # Remove backend name from backend_track
            del backend_track[req_id][req_gr]

        elif req_type == 'BackendOk':
            req_gr = line_elements[3]

            # Remove backend name from backend_track
            del backend_track[req_id][req_gr]

            # Remove gr from partially_merged
            partially_merged[req_id].remove(req_gr)
            if not len(partially_merged[req_id]):
                del partially_merged[req_id]

# Show results
print 'Запросов с неполным набором ответивших ГР:', len(partially_merged)

for gr in sorted(gr_backend_errors, key=int):
    print 'ГР', gr + ':'
    for backend in sorted(gr_backend_errors[gr]):
        print '    ', backend
        print '        Обращения:', gr_backend_errors[gr][backend]['connections']

        # Do we need to print errors?
        if len(gr_backend_errors[gr][backend]) == 1:
            continue

        print '        Ошибки:'
        for error in sorted(gr_backend_errors[gr][backend]):
            if error == 'connections':
                continue
            print '            ', error + ':', gr_backend_errors[gr][backend][error]
