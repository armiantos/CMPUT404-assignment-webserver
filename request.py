import json
from socket import MSG_DONTWAIT, SHUT_WR, SocketType
from constants import HTTP_METHODS, STATUS_CODES, CONTENT_TYPES

BUFFER_SIZE = 1024


class Request:
    """
    Wrapper class for HTTP requests that can be used to read and reply to requests
    """

    def __init__(self, socket_request: SocketType):
        """
        Create a new HTTP request wrapper from a TCP socket request
        """
        tcp_payload = self.__read_full_request(socket_request)

        # https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
        http_request: str = tcp_payload.decode('utf-8')
        self.__request = socket_request

        try:
            http_headers = http_request.split('\r\n\r\n')[0]

            headers_split = http_headers.split('\r\n')
            request_line = headers_split[0]
            self.headers = headers_split[1:]

            method, uri, http_version = request_line.split(' ')

            self.method = method
            self.uri = uri
            self.http_version = http_version

            self.valid = self.__validate()
        except:
            self.valid = False

    def __read_full_request(self, socket: SocketType) -> bytes:
        """
        Reads the entire TCP payload from the socket by unblocking the socket and
        read the payload in chunks until it is finished
        """
        tcp_payload = b''
        while True:
            try:
                # https://manpages.debian.org/bullseye/manpages-dev/recv.2.en.html#The_flags_argument
                data = socket.recv(BUFFER_SIZE, MSG_DONTWAIT)
                tcp_payload += data
            except BlockingIOError as err:
                break
        return tcp_payload

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
        Closes the socket connection to finish the request gracefully
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
        self.reply(
            status_code,
            message_body=json.dumps(obj),
            content_type=CONTENT_TYPES['json'],
            extra_headers=extra_headers
        )
        self.__close_connection()

    def reply(self,
              status_code: int,
              message_body: str,
              content_type: str,
              extra_headers: str = None):
        """
        Respond to a HTTP request with a text encoded message_body

        Params:
        - `status_code` - the HTTP response that should be sent to the client
        - `message_body` - a string representation of the message body
        - `content_type` - the value to be used in the 'Content-Type' field of the HTTP header (possibly including character encoding)
        - `extra_headers` - additional headers that should be attached (use `'\r\n'.join`
           if you have multiple headers that need to be attached)
        """
        entity_headers = [
            f'Content-Length: {len(message_body)}',
        ]

        if content_type != None:
            entity_headers.append(f'Content-Type: {content_type}')

        if extra_headers != None:
            entity_headers.append(extra_headers)

        self.__request.sendall(
            bytearray('\r\n'.join([
                self.__status_line(status_code),
                '\r\n'.join(entity_headers),
                f'\r\n{message_body}'
            ]), 'utf-8'))
        self.__close_connection()

    def reply_bytearray(self, byte_array: bytearray):
        """
        Respond to the socket request with a bytearray representation of the payload

        Params:
        - `byte_array` - bytearray representation of the TCP payload
        """
        self.__request.sendall(byte_array)
        self.__close_connection()
