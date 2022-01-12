# coding: utf-8
import socketserver
import json

from status_codes import STATUS_CODES
from content_types import CONTENT_TYPES

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


def status_line(status_code: int) -> str:
    http_version = 'HTTP/1.1'
    reason_phrase = STATUS_CODES[status_code]
    return f'{http_version} {status_code} {reason_phrase}'


def respond_with_file(file_path: str) -> str:
    # https://www.w3schools.com/python/python_file_open.asp
    try:
        file = open(file_path)
    except FileNotFoundError as err:
        # https://www.geeksforgeeks.org/how-to-convert-python-dictionary-to-json/
        payload = json.dumps({
            'err': err.strerror
        })
        entity_headers = '\r\n'.join([
            f'Content-Length: {len(payload)}',
            f'Content-Type: {len(payload)}'
        ])

        return '\r\n'.join([
            status_line(404),
            entity_headers,
            f'\r\n{payload}'
        ])
    else:
        payload = file.read()
        extension = file_path.split('.')[-1]

        entity_headers = '\r\n'.join([
            f'Content-Type: {CONTENT_TYPES[extension]}',
            f'Content-Length: {len(payload)}'
        ])

        return '\r\n'.join([
            status_line(200),
            entity_headers,
            f'\r\n{payload}'
        ])


class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
        request = self.data.decode("utf-8")

        # TODO: Verify if HTTP request

        request_line = request.split('\r\n')[0]
        method, path, http_version = request_line.split(' ')

        if path == '/':
            path = '/index.html'

        path = f'./www/{path}'

        self.request.sendall(bytearray(respond_with_file(path), 'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
