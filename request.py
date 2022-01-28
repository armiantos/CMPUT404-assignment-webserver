import json
from socket import SHUT_WR, SocketType
from constants import DEFAULT_ENCODING, HTTP_METHODS, STATUS_CODES, TEXT_CONTENT_TYPES
from helpers import to_bytearray

BUFFER_SIZE = 1024


class Request:
    """
    Wrapper class for HTTP requests that can be used to read and reply to requests
    """

    def __init__(self, request_socket: SocketType):
        """
        Create a new HTTP request wrapper from a TCP socket request
        """
        self.headers = None
        self.body = None

        self.__request = request_socket

        try:
            self.__parse_request(request_socket)
            self.valid = self.__validate()
        except Exception:
            self.valid = False

    def __parse_request(self, socket: SocketType) -> bytes:
        """
        Parses the entire request and populates the following `self` fields: `method`, `uri`, `http_version`, `headers`, `body`
        """
        raw_payload = b''
        while True:
            chunk = socket.recv(BUFFER_SIZE)
            raw_payload += chunk

            if raw_payload.find(b'\r\n\r\n') == -1:
                # Haven't seen end of HTTP header, keep reading
                continue

            # https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
            payload = raw_payload.decode(DEFAULT_ENCODING)

            if self.headers == None:
                headers_and_body = payload.split('\r\n\r\n')
                self.__initialize_headers(headers_and_body[0])

            if 'Content-Length' not in self.headers:
                return

            body = headers_and_body[1]
            if len(body) == int(self.headers['Content-Length']):
                self.body = body
                return

    def __initialize_headers(self, headers: str):
        """
        Takes a string holding all the characters up to the final CLRF just before the HTTP message body
        and populates the corresponding fields in the Request object.
        """
        self.headers = {}
        headers_split = headers.split('\r\n')

        self.__parse_status_line(headers_split[0])
        self.__parse_headers(headers_split[1:])

    def __parse_status_line(self, status_line: str):
        """
        Parses through the given status line to fill in `self.method`, `self.uri`, `self.http_version`
        """
        method, uri, http_version = status_line.split(' ')
        self.method = method
        self.uri = uri
        self.http_version = http_version

    def __parse_headers(self, headers: list[str]):
        """
        Parses through the given array of HTTP headers to fill in the dictionary `self.headers`
        """
        for header in headers:
            key, value = header.split(': ')
            self.headers[key] = value

    def __validate(self) -> bool:
        """
        Helper function to ensure the TCP payload is HTTP/1.1 compliant

        Returns:
        True if the request is HTTP/1.1 compliant, False otherwise
        """
        if self.method not in HTTP_METHODS:
            return False
        if self.http_version != 'HTTP/1.1':
            return False

        return True

    def __status_line(self, status_code: int) -> str:
        """
        Helper function to generate the [status line](https://datatracker.ietf.org/doc/html/rfc2616#section-6.1)
        field in a HTTP/1.1 header

        Params:
        - `status_code` - A valid HTTP/1.1 status code

        Returns:
        A single line string representing the HTTP status line
        """
        http_version = 'HTTP/1.1'
        reason_phrase = STATUS_CODES[status_code]
        return f'{http_version} {status_code} {reason_phrase}'

    def __close_connection(self):
        """
        Closes socket connection associated with request.
        """
        self.__request.shutdown(SHUT_WR)
        self.__request.close()

    def reply_json(self, obj: dict, status_code: int, extra_headers: str = None):
        """
        Respond to a HTTP request with a json object

        Params:
        - `obj` - the dictionary representation of the json object
        - `status_code` - the HTTP response that should be sent to the client
        - `extra_headers` - additional headers that should be attached (use `'\r\n'.join`
           if you have multiple headers that need to be attached)
        """
        # https://www.geeksforgeeks.org/how-to-convert-python-dictionary-to-json/
        self.reply(status_code,
                   message_body=to_bytearray(json.dumps(obj)),
                   content_type=TEXT_CONTENT_TYPES['json'],
                   extra_headers=extra_headers)

    def reply(self, status_code: int, message_body: bytearray, content_type: str, extra_headers: str = None):
        """
        Respond to a HTTP request with a text encoded message_body

        Params:
        - `status_code` - the HTTP response that should be sent to the client
        - `message_body` - a bytearray representing the encoded text or binary contents of a file
        - `content_type` - the value to be used in the 'Content-Type' field of the HTTP header (possibly including character encoding)
        - `extra_headers` - additional headers that should be attached (use `'\r\n'.join`
           if you have multiple headers that need to be attached)
        """
        entity_headers = [
            f'Content-Length: {len(message_body)}',
            'Server: sumitro-server/1.0',
            'Connection: close'
        ]

        if content_type != None:
            entity_headers.append(f'Content-Type: {content_type}')

        if extra_headers != None:
            entity_headers.append(extra_headers)

        try:
            self.__request.sendall(
                bytearray('\r\n'.join([self.__status_line(status_code), '\r\n'.join(entity_headers), f'\r\n']),
                        DEFAULT_ENCODING) + message_body)
            self.__close_connection()
        except OSError:
            # Connection already closed
            return

    def reply_bytearray(self, byte_array: bytearray):
        """
        Respond to the socket request with a bytearray representation of the payload

        Params:
        - `byte_array` - bytearray representation of the TCP payload
        """
        self.__request.sendall(byte_array)
        self.__close_connection()
