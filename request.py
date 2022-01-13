import json
from status_codes import STATUS_CODES


class Request:
    def __init__(self, socket_request):
        data = socket_request.recv(1024).strip()
        # https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
        http_request: str = data.decode('utf-8')
        self.__request = socket_request

        http_headers = http_request.split('\r\n\r\n')[0]

        headers_split = http_headers.split('\r\n')
        request_line = headers_split[0]
        self.headers = headers_split[1:]

        method, uri, http_version = request_line.split(' ')

        self.method = method
        self.uri = uri
        self.http_version = http_version

        self.__validate()

    def __validate(self):
        pass

    def status_line(self, status_code: int) -> str:
        http_version = 'HTTP/1.1'
        reason_phrase = STATUS_CODES[status_code]
        return f'{http_version} {status_code} {reason_phrase}'

    def respond_with_json(self, obj: dict, status_code: int = 200):
        # https://www.geeksforgeeks.org/how-to-convert-python-dictionary-to-json/
        payload = json.dumps(obj)
        entity_headers = '\r\n'.join([
            f'Content-Length: {len(payload)}',
            f'Content-Type: {len(payload)}'
        ])

        self.__request.sendall(bytearray('\r\n'.join([
            self.status_line(status_code),
            entity_headers,
            f'\r\n{payload}'
        ]), 'utf-8'))

    def respond_with_raw(self, raw_data, status_code: int = 200):
        self.__request.sendall(bytearray(raw_data, 'utf-8'))
