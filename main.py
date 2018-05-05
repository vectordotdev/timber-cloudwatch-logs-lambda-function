import base64
import re
import binascii
from datetime import datetime
import gzip
from io import StringIO
import json
import os
from urllib.request import Request, urlopen
import zlib

UUID_GROUP = '(?P<request_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
START_REGEX = re.compile('START RequestId: ' + UUID_GROUP + ' Version:\s(?P<version>.+)')
END_REGEX = re.compile('END RequestId: ' + UUID_GROUP)
REPORT_REGEX = re.compile('REPORT RequestId: ' + UUID_GROUP +
                          '\s+Duration: (?P<duration>[\d.]+) ms'
                          '\s+Billed Duration: (?P<billed_duration>\d+) ms' +
                          '\s+Memory Size: (?P<total_memory>\d+) MB' +
                          '\s+Max Memory Used: (?P<used_memory>\d+) MB')
TIMEOUT_REGEX = re.compile(UUID_GROUP + ' Task timed out after (?P<duration>[\d.]+) seconds')
JSON_SCHEMA_URL = 'https://raw.githubusercontent.com/timberio/log-event-json-schema/v3.1.3/schema.json'

API_KEY = os.environ['TIMBER_API_KEY']
URL = os.getenv('TIMBER_URL', 'https://logs.timber.io/frames')
HEADERS_PROTOTYPE = {
    'content-type': 'text/plain',
    'user-agent': 'Timber Cloudwatch Lambda Function/1.0.0 (python)'
}


def lambda_handler(event, _context):
    """
    Main entry point for the lambda handler.
    """
    event_data = decode_event_data(event)

    log_lines = []
    for log_event in event_data['logEvents']:
        log_line = transform_to_log_line(log_event)
        log_lines.append(log_line)

    deliver(log_lines)


def decode_event_data(event):
    """
    Decodes the raw Cloudwatch lambda payload into a dictionary
    representing the JSON structure.
    """
    base64_gzipped_data = str(event['awslogs']['data'])
    gzipped_data = binascii.a2b_base64(base64_gzipped_data)
    json_data = zlib.decompress(gzipped_data, 15+32)
    data = json.loads(json_data)
    return data


def lambda_context(request_id):
    return {
        'custom': {
            'lambda': {
                'request_id': request_id
            }
        }
    }


def timeout_meta(match):
    groups = match.groupdict()
    return {
        '$schema': JSON_SCHEMA_URL,
        'context': lambda_context(groups['request_id']),
        'level': 'error',
        'event': {
            'custom': {
                'lambda_timeout': {
                    'duration_s': float(groups['duration']),
                }
            }
        }
    }


def start_meta(match):
    groups = match.groupdict()
    request_id = groups['request_id']
    return {
        '$schema': JSON_SCHEMA_URL,
        'context': lambda_context(request_id),
        'level': 'info',
        'event': {
            'custom': {
                'lambda_start': {
                    'request_id': request_id,
                    'version': groups['version'],
                }
            }
        }
    }


def end_meta(match):
    groups = match.groupdict()
    request_id = groups['request_id']
    return {
        '$schema': JSON_SCHEMA_URL,
        'context': lambda_context(request_id),
        'level': 'info',
        'event': {
            'custom': {
                'lambda_end': {
                    'request_id': request_id
                }
            }
        }
    }


def report_meta(match):
    groups = match.groupdict()
    return {
        '$schema': JSON_SCHEMA_URL,
        'context': lambda_context(groups['request_id']),
        'level': 'info',
        'event': {
            'custom': {
                'lambda_report': {
                    'duration_ms': float(groups['duration']),
                    'billed_duration_ms': float(groups['billed_duration']),
                    'total_memory': int(groups['total_memory']),
                    'used_memory': int(groups['used_memory']),
                }
            }
        }

    }


def log_line(timestamp, message, meta):
    dt = datetime.utcfromtimestamp(timestamp / 1000.0)
    datetime_iso8601 = dt.isoformat() + 'Z'
    line = datetime_iso8601 + ": " + message
    if meta:
        line += ' @metadata ' + json.dumps(meta, separators=(',', ':'))
    return line


def transform_to_log_line(log_event):
    """
    Transforms the CloudWatch log events into string log lines suitable
    for consumption by the Timber API.
    """
    message = log_event['message'].rstrip()
    timestamp = log_event['timestamp']

    start_match = START_REGEX.match(message)
    if start_match:
        return log_line(timestamp, message, start_meta(start_match))

    end_match = END_REGEX.match(message)
    if end_match:
        return log_line(timestamp, message, end_meta(end_match))

    report_match = REPORT_REGEX.match(message)
    if report_match:
        return log_line(timestamp, message, report_meta(report_match))

    timeout_match = TIMEOUT_REGEX.match(message)
    if timeout_match:
        return log_line(timestamp, message, timeout_meta(timeout_match))

    return log_line(timestamp, message, None)

def deliver(log_lines):
    """
    Delivers the list of string log lines to the Timber API.
    """
    body_str = '\n'.join([log_line for log_line in log_lines])
    body_bytes = body_str.encode()
    authorization_token = base64.b64encode(API_KEY.encode()).decode()
    headers = HEADERS_PROTOTYPE.copy()
    headers['authorization'] = 'Basic ' + authorization_token
    headers['content-length'] = len(body_bytes)
    request = Request(URL, data=body_bytes, headers=headers)
    code = urlopen(request).getcode()
    log('Received status ' + str(code))

def log(message):
    print(message)
