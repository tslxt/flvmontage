import sys
import os

from optparse import OptionParser


def search_flv(direction, courseid):
	errorMessage = []
	allfiles = []
	try:
		allfiles = os.listdir(direction)
	except Exception, (errno, strerror):
		errorMessage.append([errno, strerror])
		print errorMessage
		return (0, errorMessage)
	
	# print allfiles
	# print len(allfiles)

	flvlist = []
	for flv in allfiles:
		if courseid in flv:
			if len(flv) == len(courseid) + 15:
				flvlist.append(flv)

	if len(flvlist) == 0:
		errorMessage.append([101, "No such flv files by given courseid"])

	if len(errorMessage):
		print errorMessage
		return (0, errorMessage)

	for flv in flvlist:
		print flv
	# print len(flvlist)
	return (1, flvlist)


def process_options():
    usage = "%prog do a job for seach all flv files by courseID"
    description = ("Search flv files in given direction by courseid. "
                   "path will be used for range in direction. "
                   "courseid will be needed. ")
    # version = "%%prog flvlib %s" % __versionstr__
    version = "Test"
    parser = OptionParser(usage=usage, description=description,
                          version=version)
    parser.add_option("-d", "--direction", help="path of range")
    parser.add_option("-i", "--courseid", help="courseid of condition")
    # parser.add_option("-v", "--verbose", action="count",
    #                   default=0, dest="verbosity",
    #                   help="be more verbose, each -v increases verbosity")
    options, args = parser.parse_args(sys.argv)

    if not options.direction:
    	parser.error("You need to provide a path for searching")

    if not options.courseid:
    	parser.error("You need to provide a courseid for searching")

    # if not options.direction or not options.courseid:
    #     parser.error("You need to provide a path and "
    #                  "one courseid for searching ")
	
	# if not options.direction:
	# 	parser.error("You need to provide a path for searching")

	
    # if options.verbosity > 3:
    #     options.verbosity = 3

    # log.setLevel({0: logging.ERROR, 1: logging.WARNING,
    #               2: logging.INFO, 3: logging.DEBUG}[options.verbosity])

    return options, args

def search_flvs():
	options, args = process_options()
	return search_flv(options.direction, options.courseid)

def main():
    try:
        outcome = search_flvs()
    except KeyboardInterrupt:
        # give the right exit status, 128 + signal number
        # signal.SIGINT = 2
        sys.exit(128 + 2)
    except EnvironmentError, (errno, strerror):
        try:
            print >> sys.stderr, strerror
        except StandardError:
            pass
        sys.exit(2)

    if outcome:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()