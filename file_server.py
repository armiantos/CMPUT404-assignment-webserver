from constants import CONTENT_TYPES
from helpers import is_path_under_directory, remove_prefix
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
            request.reply(
                message_body={},
                content_type=CONTENT_TYPES['json'],
                status_code=405
            )
            return True

        # https://www.geeksforgeeks.org/python-os-path-join-method/
        file_path = os.path.join(
            self.directory_path, remove_prefix(request.uri, self.base_path))
        if os.path.isdir(file_path) and not file_path.endswith('/'):
            request.reply_json({'msg': f'Redirecting you to {request.uri}/'},
                               status_code=301, extra_headers=f'Location: {request.uri}/')
            return
        if file_path.endswith('/'):
            file_path = os.path.join(
                file_path, 'index.html')
        if not is_path_under_directory(file_path, self.directory_path):
            request.reply_json(
                {'err': FileNotFoundError().strerror}, status_code=404)
            return True

        # https://www.w3schools.com/python/python_file_open.asp
        try:
            file = open(file_path, encoding='utf-8')

        except FileNotFoundError as err:
            request.reply_json({'err': err.strerror}, status_code=404)
            return True
        except:
            request.reply_json(
                {'err': 'Unknown error occured'}, status_code=500)
            return True

        payload = file.read()
        extension = file_path.split('.')[-1]

        request.reply(
            message_body=payload,
            content_type=CONTENT_TYPES[extension] if extension in CONTENT_TYPES else None,
            status_code=200
        )

        file.close()

        return True
