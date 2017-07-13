import base64
import binascii
from datetime import datetime
import gzip
from io import StringIO
import json
import os
from urllib.request import Request, urlopen
import zlib

API_KEY = os.environ['TIMBER_API_KEY']
URL = os.environ['TIMBER_URL'] || 'https://logs.timber.io/frames'
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
    #gzipped_data = base64.b64decode(base64_gzipped_data).decode()
    json_data = zlib.decompress(gzipped_data, 15+32)
    data = json.loads(json_data)
    return data

def transform_to_log_line(log_event):
    """
    Transforms the CloudWatch log events into string log lines suitable
    for consumption by the Timber API.
    """
    timestamp = log_event['timestamp']
    dt = datetime.fromtimestamp(timestamp / 1000.0)
    datetime_iso8601 = dt.isoformat()
    message = log_event['message']
    line = datetime_iso8601 + ": " + message
    return line

def deliver(log_lines):
    """
    Delivers the list of string log lines to the Timber API.
    """
    body = '\n'.join([log_line for log_line in log_lines]).encode()
    authorization_token = base64.b64encode(API_KEY.encode()).decode()
    headers = HEADERS_PROTOTYPE.copy()
    headers['authorization'] = 'Basic ' + authorization_token
    headers['content-length'] = len(body)
    request = Request(URL, data=body, headers=headers)
    code = urlopen(request).getcode()
    log('Received status ' + str(code))

def log(message):
    print(message)
