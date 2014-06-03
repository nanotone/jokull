import os
import urllib2

import flickr_api

user_photosets = None

def get_photosets():
    global user_photosets
    if user_photosets is None:
        user = flickr_api.test.login()
        print "Retrieving user's albums..."
        user_photosets = user.getPhotosets()
    return user_photosets

def get_photoset_by_title(title):
    try:
        return [ps for ps in get_photosets() if ps.title == title][0]
    except IndexError:
        raise KeyError("Album '%s' not found" % title)

def save_photoset(photoset):
    os.mkdir(photoset.title)
    photos = photoset.getPhotos()
    for (i, photo) in enumerate(photos):
        path = '%s/%s.jpg' % (photoset.title, photo.title)
        for retry in range(3):
            verb = "Saving" if not retry else "Retrying"
            print "%s %s (%d of %d)" % (verb, path, i+1, len(photos))
            try:
                photo.save(path)
                break
            except urllib2.HTTPError as e:
                if e.getcode() != 504:
                    raise
            except urllib2.URLError as e:
                if e.reason.errno != 110:  # connection timed out
                    raise

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('tokenfile')
    parser.add_argument('command')
    parser.add_argument('--albumtitle')
    args = parser.parse_args()
    flickr_api.set_auth_handler(args.tokenfile)
    if args.command == 'list':
        for photoset in get_photosets():
            print photoset.title
    elif args.command == 'save':
        if not args.albumtitle:
            raise RuntimeError("--albumtitle is required with 'save' command")
        photoset = get_photoset_by_title(args.albumtitle)
        save_photoset(photoset)
