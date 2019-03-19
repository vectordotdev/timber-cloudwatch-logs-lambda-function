import base64
from datetime import datetime
import json
import os
import urllib
from urllib.request import Request
import zlib

version = 'unknown'

version_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'VERSION')
if os.path.exists(version_file):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'VERSION')) as version_file:
        version = version_file.read().strip()

API_KEY = os.environ['TIMBER_API_KEY']
SOURCE_ID = os.environ['TIMBER_SOURCE_ID']
HOST = os.getenv('TIMBER_HOST', 'https://logs.timber.io')
HEADERS_PROTOTYPE = {
    'Content-Type': 'application/ndjson',
    'User-Agent': f'Timber Cloudwatch Lambda Function/{version} (python)'
}
DEBUG = os.getenv('TIMBER_DEBUG', '')

urlhandler = urllib.request.HTTPSHandler()
if DEBUG:
    urlhandler.set_http_debuglevel(9)
urlopener = urllib.request.build_opener(urlhandler)


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
    gzipped_data = base64.b64decode(base64_gzipped_data)
    json_data = zlib.decompress(gzipped_data, 15+32)

    data = json.loads(json_data)

    return data


def transform_to_log_line(log_event):
    """
    Transforms the CloudWatch log events into string log lines suitable
    for consumption by the Timber API.
    """
    timestamp = log_event['timestamp']
    dt = datetime.utcfromtimestamp(timestamp / 1000.0)
    datetime_iso8601 = dt.isoformat() + 'Z'
    message = log_event['message']
    log_line = {'dt': datetime_iso8601, 'message': message}
    json_log_line = json.dumps(log_line)
    return json_log_line


def deliver(log_lines):
    """
    Delivers the list of string log lines to the Timber API.
    """
    body_str = '\n'.join([log_line for log_line in log_lines if log_line != ''])
    body_bytes = body_str.encode()

    headers = HEADERS_PROTOTYPE.copy()
    headers['Authorization'] = 'Bearer ' + API_KEY
    headers['Content-Length'] = len(body_bytes)

    url = str(HOST) + '/sources/' + str(SOURCE_ID) + '/frames'
    request = Request(url, data=body_bytes, headers=headers)

    code = urlopener.open(request).read()

    log('Received status ' + str(code))


def log(message):
    print(message)


# useful for testing locally
if __name__ == "__main__":
    import fileinput
    import time

    context = []
    for i, line in enumerate(fileinput.input()):
        event = []

        log_message = {
            'messageType': 'DATA_MESSAGE',
            'owner': '123456789123',
            'logGroup': 'testLogGroup',
            'logStream': 'testLogStream',
            'subscriptionFilters': [
                'testFilter'
            ],
            'logEvents': [
                {
                    'id': f'eventId{i}',
                    'timestamp': int(time.time() * 1000),
                    'message': line,
                },
            ]
        }

        log_data = base64.b64encode(
            zlib.compress(
                str.encode(
                    json.dumps(log_message)
                )
            )
        )

        event = {
            "awslogs": {
                "data": log_data.decode()
            }
        }

        lambda_handler(event, context)
