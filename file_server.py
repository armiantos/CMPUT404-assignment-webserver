import json
from constants import CONTENT_TYPES, DEFAULT_ENCODING
from helpers import is_path_under_directory, remove_prefix, to_bytearray
from request import Request
import os


class FileServer:
    """Serves files in directory using HTTP"""

    def __init__(self, base_path: str, directory_path: str):
        """
        Creates a new file server that can serve files under directory_path
        through HTTP routes with prefix base_path

        Params:
        - `base_path` - HTTP URI prefix to listen to (e.g. `/www/`)
        - `directory_path` - Relative path to directory to serve files from
        """
        self.base_path = base_path
        self.directory_path = directory_path

    def handle(self, request: Request) -> bool:
        """
        Attempt to handle an HTTP request using this file server

        Params:
        - `request` - the HTTP request object

        Returns:
        True if the request was handled, False otherwise        
        """
        # Match route
        if not request.uri.startswith(self.base_path):
            return False

        if request.method != 'GET':
            request.reply_json({'err': 'File server only supports HTTP GET'}, status_code=405)
            return True

        # https://www.geeksforgeeks.org/python-os-path-join-method/
        file_path = os.path.join(self.directory_path, remove_prefix(request.uri, self.base_path))
        if os.path.isdir(file_path) and not file_path.endswith('/'):
            request.reply_json({'msg': f'Redirecting you to {request.uri}/'},
                               status_code=301,
                               extra_headers=f'Location: {request.uri}/')
            return
        if file_path.endswith('/'):
            file_path = os.path.join(file_path, 'index.html')
        if not is_path_under_directory(file_path, self.directory_path):
            request.reply_json({'err': FileNotFoundError().strerror}, status_code=404)
            return True

        extension = file_path.split('.')[-1] if len(file_path.split('.')) > 0 else None

        if extension is None or extension not in CONTENT_TYPES:
            self.__send_binary(request, file_path)
            return True

        self.__send_text_file(request, file_path, extension)
        return True

    def __send_binary(self, request: Request, file_path: str):
        try:
            file = open(file_path, 'br')
            payload = file.read()
            file.close()

            request.reply(message_body=payload, content_type='application/octet-stream', status_code=200)
        except FileNotFoundError as err:
            request.reply_json({'err': err.strerror}, status_code=404)
        except Exception as err:
            request.reply_json({'err': str(err)}, status_code=500)

    def __send_text_file(self, request: Request, file_path: str, extension: str):
        try:
            # https://www.w3schools.com/python/python_file_open.asp
            file = open(file_path, 'r', encoding=DEFAULT_ENCODING)
            payload = file.read()
            file.close()

            content_type = None
            if extension in CONTENT_TYPES:
                content_type = f'{CONTENT_TYPES[extension]}; charset={DEFAULT_ENCODING}'

            request.reply(message_body=to_bytearray(payload), content_type=content_type, status_code=200)
        except FileNotFoundError as err:
            request.reply_json({'err': err.strerror}, status_code=404)
        except Exception as err:
            request.reply_json({'err': str(err)}, status_code=500)
