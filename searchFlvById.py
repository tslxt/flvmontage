import sys
import os
import time

from optparse import OptionParser


def search_flv(direction, courseid, date_time, display=False):
	allfiles = []
	try:
		allfiles = os.listdir(direction)
	except Exception, (errno, strerror):
		if display:
			print errno, strerror
		return (errno, strerror)
	
	# print allfiles
	# print len(allfiles)

	flvlist = []
	for flv in allfiles:
		if courseid in flv:
			if len(flv) == len(courseid) + 15:
				if not date_time:
					flvlist.append(flv)
				else:
					ctime = float(flv[flv.index("-") + 1:flv.index(".flv")])
					if time.strftime("%Y-%m-%d", time.localtime(ctime)) == str(date_time):
						flvlist.append(flv)
	if len(flvlist) == 0:
		if display:
			print 101, "No such flv files by given courseid"
		return (101, "No such flv files by given courseid")

	flvlist.sort()

	if display:
		for flv in flvlist:
			print flv
	# print len(flvlist)
	return (0, flvlist)


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
    parser.add_option("-t", "--datetime", help="search by datetime")
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
	if(options.datetime):
		return search_flv(options.direction, options.courseid, options.datetime, True)
	else:
		return search_flv(options.direction, options.courseid, None, True)

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