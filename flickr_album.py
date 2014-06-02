import os
import sys

import flickr_api

args = sys.argv[1:]
flickr_api.set_auth_handler(args[0])

user = flickr_api.test.login()
photosets = user.getPhotosets()
if args[1] == 'list':
    for photoset in photosets:
        print photoset.title
elif args[1] == 'save':
    albumtitle = args[2]
    photoset = [ps for ps in photosets if ps.title == albumtitle][0]
    os.mkdir(albumtitle)
    photos = photoset.getPhotos()
    for (i, photo) in enumerate(photos):
        path = '%s/%s.jpg' % (albumtitle, photo.title)
        print "Saving %s (%d of %d)" % (path, i+1, len(photos))
        photo.save(path)
        
    
#photos = photosets[0].getPhotos()
#print dir(photos[0])
#print photos[0].getInfo()
#print photos[0].getStats()
#print photos[0].title

#photos[0].save('test.jpg')


