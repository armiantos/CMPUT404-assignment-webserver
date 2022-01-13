from content_types import CONTENT_TYPES
from request import Request


class FileServer:
    def __init__(self, base_path: str, directory_path: str):
        self.base_path = base_path
        self.directory_path = directory_path

    def handle(self, request: Request) -> bool:
        # Match route
        if not request.uri.startswith(self.base_path):
            return False

        # TODO: Test with flask to see if this is the desired behavior
        if request.method != 'GET':
            request.respond_with_raw(
                message_body={},
                content_type=CONTENT_TYPES['json'],
                status_code=405
            )
            return False

        requested_file_path = f'{self.directory_path}{request.uri}'
        if requested_file_path.endswith('/'):
            requested_file_path += 'index.html'

        # https://www.w3schools.com/python/python_file_open.asp
        try:
            file = open(requested_file_path, encoding='utf-8')

        except FileNotFoundError as err:
            request.respond_with_json({'err': err.strerror}, status_code=404)
            return False
        except:
            request.respond_with_json(
                {'err': 'Unknown error occured'}, status_code=500)
            return False

        payload = file.read()
        extension = requested_file_path.split('.')[-1]
        print(f'{extension}: {CONTENT_TYPES[extension]}')

        request.respond_with_raw(
            message_body=payload,
            content_type=CONTENT_TYPES[extension],
            status_code=200
        )

        file.close()

        return True
