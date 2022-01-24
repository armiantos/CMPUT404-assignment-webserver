# CMPUT404-assignment-webserver

CMPUT404-assignment-webserver

See requirements.org (plain-text) for a description of the project.

Make a simple webserver.

# Contributors / Licensing

Generally everything is LICENSE'D under the Apache 2 license by Abram Hindle.

server.py contains contributions from:

- Abram Hindle
- Eddie Antonio Santos
- Jackson Z Chang
- Mandy Meindersma
- Armianto Sumitro

But the server.py example is derived from the python documentation
examples thus some of the code is Copyright © 2001-2013 Python
Software Foundation; All Rights Reserved under the PSF license (GPL
compatible) http://docs.python.org/2/library/socketserver.html

# External references used

- Status codes and their reasoning phrases obtained from [rfc2616 - Section 6.1.1](https://datatracker.ietf.org/doc/html/rfc2616#section-6.1.1)
- Content types obtained from [iana - Media Types](https://www.iana.org/assignments/media-types/media-types.xhtml)
- How to safely join file paths adapted from [GeeksforGeeks - Python | os.path.join() method](https://www.geeksforgeeks.org/python-os-path-join-method/)
- How to open a file adapted from [w3schools - Python File Open](https://www.w3schools.com/python/python_file_open.asp)
- Implementation of `str.removeprefix` from [Built-in Types — Python 3.10.1 documentation](https://docs.python.org/3/library/stdtypes.html#str.removeprefix)
- How to convert a bytes like object to string adapted from [StackOverFlow - Convert bytes to a string](https://stackoverflow.com/questions/606191/convert-bytes-to-a-string)
- How to convert a dictionary to JSON adapted from [GeeksForGeeks - How To Convert Python Dictionary To JSON?](https://www.geeksforgeeks.org/how-to-convert-python-dictionary-to-json/)
- Reading multiple chunks from the same socket using non blocking sockets [recv(2) - the flags argument](https://manpages.debian.org/bullseye/manpages-dev/recv.2.en.html#The_flags_argument)
