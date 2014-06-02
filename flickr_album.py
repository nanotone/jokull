import os

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
        print "Saving %s (%d of %d)" % (path, i+1, len(photos))
        photo.save(path)

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
