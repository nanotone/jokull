import os

API_KEY = os.environ['FLICKR_ACCESS']
API_SECRET = os.environ['FLICKR_SECRET']

if not API_KEY:
    raise RuntimeError("$FLICKR_ACCESS is not set!")
if not API_SECRET:
    raise RuntimeError("$FLICKR_SECRET is not set!")

print "Importing API_KEY and API_SECRET in flickr_keys.py"
