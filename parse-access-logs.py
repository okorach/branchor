#!/usr/local/bin/python3

import sys
import datetime
import re

tasks = {}
date_grouping = datetime.timedelta(minutes=15)
show_zeroes = False

def get_std_data(line):
    (d, t, level, foo) = line.split(' | ')[0].split(' ', maxsplit=3)
    return { 'datetime': d + 'T' + t, 'level': level }

def get_value(key, line):
    d = parse_fields(line)
    return d.get(key, None)

def parse_fields(line):
    d = {}
    for field in line.split(' | '):
        if not re.search('=', field):
            continue
        (k, v) = field.split('=', maxsplit=2)
        d[k] = v
    return d

def parse_api(line):
    #print(line, end='')
    log = {}
    log['logType'] = 'API_CALL'
    (std, request, codes, _, _, log['client'], _, log['taskId'], _) = line.split('"')
    (log['ip'], _, _, dt, tz) = std.split(" ", maxsplit=4)
    #dt += ' ' + tz
    dt = dt[1:]
    dt_obj = datetime.datetime.strptime(dt, '%d/%b/%Y:%H:%M:%S') # %z')
    log['datetime'] = dt_obj
    log['http_code'] = int(codes.strip().split(' ', maxsplit=2)[0])
    log['bytes'] = codes.strip().split(' ', maxsplit=2)[1]
    (log['method'], request, _) = request.split(' ', maxsplit=3)
    log['object'] = '-'
    if re.search('\?', request):
        (log['api'], params) = request.split("?", maxsplit=2)
        if params.strip() != '':
            for p in params.split('&'):
                (pname, pvalue) = p.split('=', maxsplit=1)
                if pname in ('component', 'project', 'componentKey', 'projectKey'):
                    log['object'] = pvalue
    else:
        log['api'] = request
    return log

api_fields = ('logType', 'ip', 'datetime', 'method', 'api', 'object', 'taskId', 'http_code', 'bytes', 'client')

print("# ", end='')
for key in api_fields:
    if key == 'logType':
        print("{}".format('API_CALL'), end='')
        continue
    print(",{}".format(key), end='')
    if key == 'datetime':
        print(",{}".format('hour'), end='')
    elif key == 'duration_ms':
        print(",{}".format('duration_s'), end='')
        print(",{}".format('duration_min'), end='')
        print(",{}".format('duration_h'), end='')
print("")

sys.argv.pop(0)
next_date = datetime.datetime(2019, 1, 1, 0, 0, 0)
cur_date = next_date
is_first_date = True
logcount = {}
errcount = {}
x = 1
for file_arg in sys.argv:
    f = open(file_arg, "r")
    line = f.readline()

    while line:
        #print("Line = %s" % line)
        if not re.search('(GET|POST|DELETE) \/api\/', line):
            line = f.readline()
            continue
        log = parse_api(line)
        if re.search("(protobuf|css|js|png|htc|ico|gif|txt|html|README|jpg|xml|vmd)$", log['api']):
            log['api'] = 'static'
        is_first = True
        c = ''
        while next_date < log['datetime']:
            for api in logcount:
                print("{},{},{},{}".format(str(cur_date),api, logcount[api], errcount[api]))
            cur_date = next_date
            next_date += date_grouping
            is_first_date = False
            if show_zeroes:
                for api in logcount:
                    logcount[api] = 0
                    errcount[api] = 0
            else:
                logcount = {}
                errcount = {}

        if log['api'] not in logcount:
            logcount[log['api']] = 0
        if log['api'] not in errcount:
            errcount[log['api']] = 0

        logcount[log['api']] += 1
        #print("Code = %d".format(log['http_code']))
        if log['http_code'] != 200:
            errcount[log['api']] += 1

        # for key in api_fields:
        #     s = log.get(key, '')
        #     print("{}{}".format(c, s), end='')
        #     c = ','
        #     if key == 'datetime':
        #         print("{}{}".format(c, s[:13]), end='')
        #     elif key == 'duration_ms':
        #         print("{}{}".format(c, s/1000), end='')
        #         print("{}{}".format(c, s/1000/60), end='')
        #         print("{}{}".format(c, s/1000/60/60), end='')
        # print("")
        line = f.readline()