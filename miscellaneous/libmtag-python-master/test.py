import libmtag
import sys

myfile = libmtag.File(sys.argv[1])

print "%s - %s" % (myfile.tag().get("artist"), myfile.tag().get("title"))

myfile.tag().set("artist", "foo")

print "%s - %s" % (myfile.tag().get("artist"), myfile.tag().get("title"))

print myfile.tag("id3v2").get_all ()

# myfile.save()
