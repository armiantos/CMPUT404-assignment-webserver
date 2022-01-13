from content_types import CONTENT_TYPES
from request import Request


class FileServer:
    def __init__(self, base_path: str, directory_path: str):
        self.base_path = base_path
        self.directory_path = directory_path

    def handle(self, request: Request) -> bool:
        if not request.uri.startswith(self.base_path):
            return False

        requested_file_path = f'{self.directory_path}{request.uri}'
        if requested_file_path.endswith('/'):
            requested_file_path += 'index.html'
        print(requested_file_path)

        self.__send_http_response(request, requested_file_path)

        return True

    def __send_http_response(self, request: Request, file_path: str) -> str:
        # https://www.w3schools.com/python/python_file_open.asp
        try:
            file = open(file_path, encoding='utf-8')
        except FileNotFoundError as err:
            return request.respond_with_json({
                'err': err.strerror
            })
        else:
            payload = file.read()
            extension = file_path.split('.')[-1]

            entity_headers = '\r\n'.join([
                f'Content-Type: {CONTENT_TYPES[extension]}',
                f'Content-Length: {len(payload)}'
            ])

            request.respond_with_raw(
                '\r\n'.join([
                    request.status_line(200),
                    entity_headers,
                    f'\r\n{payload}'
                ]),
                200
            )
