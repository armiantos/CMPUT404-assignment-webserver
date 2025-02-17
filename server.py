# coding: utf-8
import socketserver
from constants import DEFAULT_ENCODING
from file_server import FileServer
from request import Request

# Copyright 2022 Armianto Sumitro
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

file_server = FileServer('/', './www')


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        request = Request(self.request)
        if not request.valid:
            request.reply_bytearray(bytearray("Request doesn't follow HTTP/1.1 protocol", DEFAULT_ENCODING))
            return

        if file_server.handle(request):
            return

        request.reply_json({'err': 'No matching route'}, status_code=404)


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
