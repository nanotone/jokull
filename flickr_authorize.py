import os
import sys

import flickr_api

path = sys.argv[1]
if os.path.exists(path):
    print "Please delete or move the existing file at", path
    sys.exit(0)

with open(path, 'w') as fd: pass  # check writability

handler = flickr_api.auth.AuthHandler()
print "Please authorize Jokull at", handler.get_authorization_url('read')

verifier = ''
while not verifier.strip():
    verifier = raw_input("Paste the verifier code you received: ")

handler.set_verifier(verifier)
flickr_api.set_auth_handler(handler)

handler.save(path)
