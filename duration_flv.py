import os
import sys
import shutil
import tempfile

from optparse import OptionParser

from flvlib.constants import TAG_TYPE_AUDIO, TAG_TYPE_VIDEO, TAG_TYPE_SCRIPT
from flvlib.constants import FRAME_TYPE_KEYFRAME
from flvlib.astypes import MalformedFLV, FLVObject
from flvlib.tags import FLV, EndOfFile, AudioTag, VideoTag, ScriptTag
from flvlib.tags import create_script_tag, create_flv_header
from flvlib.helpers import force_remove

class IndexingAudioTag(AudioTag):

    SEEKPOINT_DENSITY = 10

    def __init__(self, parent_flv, f):
        AudioTag.__init__(self, parent_flv, f)

    def parse(self):
        parent = self.parent_flv
        AudioTag.parse(self)

        if not parent.first_media_tag_offset:
            parent.first_media_tag_offset = self.offset


        # If the FLV has video, we're done. No need to store audio seekpoint
        # information anymore.
        if not parent.no_video:
            return

        # We haven't seen any video tag yet. Store every SEEKPOINT_DENSITY tag
        # offset and timestamp.
        parent.audio_tag_number += 1
        if (parent.audio_tag_number % self.SEEKPOINT_DENSITY == 0):
            parent.audio_seekpoints.filepositions.append(self.offset)
            parent.audio_seekpoints.times.append(self.timestamp / 1000.0)


class IndexingVideoTag(VideoTag):

    def parse(self):
        parent = self.parent_flv
        VideoTag.parse(self)

        parent.no_video = False

        if not parent.first_media_tag_offset:
            parent.first_media_tag_offset = self.offset

        if self.frame_type == FRAME_TYPE_KEYFRAME:
            parent.keyframes.filepositions.append(self.offset)
            parent.keyframes.times.append(self.timestamp / 1000.0)


class IndexingScriptTag(ScriptTag):

    def parse(self):
        parent = self.parent_flv
        ScriptTag.parse(self)

        if self.name == 'onMetaData':
            parent.metadata = self.variable
            parent.metadata_tag_start = self.offset
            parent.metadata_tag_end = self.f.tell()


tag_to_class = {
    TAG_TYPE_AUDIO: IndexingAudioTag,
    TAG_TYPE_VIDEO: IndexingVideoTag,
    TAG_TYPE_SCRIPT: IndexingScriptTag
}


class IndexingFLV(FLV):

    def __init__(self, f):
        FLV.__init__(self, f)
        self.metadata = None
        self.keyframes = FLVObject()
        self.keyframes.filepositions = []
        self.keyframes.times = []
        self.no_video = True

        # If the FLV file has no video, there are no keyframes. We want to put
        # some info in the metadata anyway -- Flash players use keyframe
        # information as a seek table. In audio-only FLV files you can usually
        # seek to the beginning of any tag (this is not entirely true for AAC).
        # Most players still work if you just provide "keyframe" info that's
        # really a table of every Nth audio tag, even with AAC.
        # Because of that, until we see a video tag we make every Nth
        # IndexingAudioTag store its offset and timestamp.
        self.audio_tag_number = 0
        self.audio_seekpoints = FLVObject()
        self.audio_seekpoints.filepositions = []
        self.audio_seekpoints.times = []

        self.metadata_tag_start = None
        self.metadata_tag_end = None
        self.first_media_tag_offset = None

    def tag_type_to_class(self, tag_type):
        try:
            return tag_to_class[tag_type]
        except KeyError:
            raise MalformedFLV("Invalid tag type: %d", tag_type)


def duration_flv(inpath):

	try:
		f = open(inpath, 'rb')
	except IOError, (errno, strerror):
		print ("Failed to open `%s': %s", inpath, strerror)
		return False

	flv = IndexingFLV(f)
	tag_iterator = flv.iter_tags()
	last_tag = None

	try:
		while True:
			tag = tag_iterator.next()
			if tag.timestamp != 0:
				last_tag = tag
	except MalformedFLV, e:
		message = e[0] % e[1:]
		print ("The file `%s' is not a valid FLV file: %s", inpath, message)
		return False
	except EndOfFile:
		print ("Unexpected end of file on file `%s'", inpath)
		return False
	except StopIteration:
		pass

	if not flv.first_media_tag_offset:
		print ("The file `%s' does not have any media content", inpath)
		return False

	if not last_tag:
		print ("The file `%s' does not have any content with a non-zero timestamp", inpath)
		return False
		
	return last_tag.timestamp / 1000.0

if __name__ == '__main__':
	duration_flv('/Applications/MAMP/htdocs/video/108_977-1438271327.flv')








