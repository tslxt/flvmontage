import json
import socket
import time
import os
from os import makedirs
import duration_flv
from shutil import copy
import logging
from flvlib.scripts import cut_flv
from flvlib.scripts import retimestamp_flv
from flvlib.scripts import index_flv

config = {}
#course_id = ''
#start_time = end_time = time.time()

logger = logging.getLogger('flvmongtage')
logger.setLevel(logging.DEBUG)

def main():
	if(readconfig()):
		initLogger()
		logger.debug("init config pass")
		startService()
	else:
		logger.error('loadconfig error!')


def readconfig():
	f = open("config.json", "r")

	if f.mode == "r":
		configfile = f.read()

		global config

		config = json.loads(configfile)

		return True
	else :
		return False

def initLogger():

	fh = logging.FileHandler(config['log'])
	fh.setLevel(logging.DEBUG)

	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)

	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)


	logger.addHandler(fh)
	logger.addHandler(ch)

def startService():

	s = socket.socket()
	# host = socket.gethostbyaddr(config['host'])
	port = config['port']

	s.bind((config['host'], port))

	s.listen(5)

	while True:
		client, addr = s.accept()
		print 'Got connection from', addr, client 
		# client.send('Thank you for connection')
		if addr[0] == config['allow_server']:
		    clientdata = json.loads(client.recv(1024))

		    if(clientdata['action'] == 'montage') :
				# global course_id, start_time, end_time
			    course_id = clientdata['data']['course_id']
			    start_time = clientdata['data']['start_time']
			    end_time = clientdata['data']['end_time']
			    montagemp3 = montage_mp3(course_id, start_time, end_time)
			    if not montagemp3:
				    client.send('montage flv false')
			    else:
				    client.send(str(montagemp3))
			    montagerecord = montage_record(course_id, start_time, end_time)
			    if not montagerecord:
				    client.send('montage record false')
			    else:
				    client.send(str(montagerecord))
			    transport_file  = transportFilesByCourseId(course_id)
			    if transport_file == 0:
				    client.send('sync success')
			    else:
				    client.send('sync falsed')
		else:
			logger.debug("access not allow")
			client.send('access not allow')
			
		client.close()

def transportFilesByCourseId(course_id):
    src = config['dest_path'] + '/' + course_id
    dest = config['sync_path']
    server_address = config['sync_server']
    return os.system('scp -r %s %s:%s' % (src, server_address, dest))

def montage_record(course_id, start_time, end_time):
	recordlist = getRecordListByCourseId(course_id)
	print recordlist
	if len(recordlist) > 0:
		copyRecord(recordlist, course_id)
		return recordlist
	else:
		return False
		

def copyRecord(recordlist, course_id):
	for record in recordlist:
		src = config['recordpath'] + '/' + course_id + '/' + record
		dest = config['dest_path'] + '/' + course_id + '/' + record
		copy(src, dest)

def montage_mp3(course_id, start_time, end_time):
	print course_id, start_time, end_time

	flvlist = getFlvListByCourseId(course_id)
	print flvlist
	if len(flvlist) > 0:
		print flvlist

		flvlistdetail = getFlvsDuration(flvlist)

		for i in flvlistdetail:
			print i[0],i[1],i[2], type(i[0]),type(i[1]),type(i[2])


		preflylist = []
		preflylist = verifytime(flvlistdetail,start_time,end_time)
		print preflylist
		cuted_flvs = cutflvs(preflylist, course_id, start_time, end_time)
    		if not cuted_flvs:
			return False	
		duration = count_duration(cuted_flvs)
		replay_config = { 'duration' : duration, 'flvs' : cuted_flvs, 'course_id' : str(course_id), 'start_time' : start_time, 'end_time' : end_time}
		save_config(replay_config, course_id)
		return replay_config
	else:
		return False
def getRecordListByCourseId(course_id):
    global config
    recordlist = []
    recordlist = os.listdir(config['recordpath'] + '/' + course_id)
    return recordlist

def getFlvListByCourseId(course_id):
	global config
	allfiles = os.listdir(config['flvpath'])
	flvlist = []
	for flv in allfiles:
		if course_id in flv:
			if len(flv) == len(course_id) + 15:
				flvlist.append(flv)
	if len(flvlist) > 0:
		flvlist.sort()
	return flvlist

def getFlvsDuration(flvlist):
	flvlistdetail = []
	for flv in flvlist:
		flvdetail = []
		flvdetail.append(str(flv))
		flvdetail.append(int(getStartTime(flv)))
		flvdetail.append(getFlvDuration(flv))

		flvlistdetail.append(flvdetail)
	return flvlistdetail

def getStartTime(flv):
	return flv[flv.index("-") + 1:flv.index(".flv")]

def getFlvDuration(flv):
	return duration_flv.duration_flv(config['flvpath'] + '/' +flv)


def verifytime(flvlistdetail, start_time, end_time):
	verifiedlist = []
	for flv in flvlistdetail:
		if (flv[1] >= start_time):
			if (flv[1] < end_time):
				if ((flv[1] + flv[2]) > end_time):
					flv.append('cut_tail')
					flv.append(flv[1])
					flv.append( end_time - flv[1])
					verifiedlist.append(flv)
				else :
					flv.append('pass')
					verifiedlist.append(flv)
		elif ((flv[1] + flv[2]) > start_time):
			if ((flv[1] + flv[2]) > end_time):
				flv.append('cut')
				flv.append(start_time)
				flv.append(end_time - start_time)
				flv.append(start_time - flv[1])
				flv.append(end_time - flv[1])
				verifiedlist.append(flv)
			else :
				flv.append('cut_head')
				flv.append(start_time)
				flv.append(start_time - flv[1])
				verifiedlist.append(flv)

	return verifiedlist

def cutflvs(preflylist, course_id, start_time, end_time):
	try:
		dest_path = config['dest_path'] + '/'+ str(course_id) + '/flv'
		makedirs(dest_path)
	except Exception, e:
		logger.error("mkdir error! course_id is %s , code is %s", course_id, e)
	
	cuted_flvs = []
	if len(preflylist) > 0:
		for flv in preflylist:
			new_flv = []
			src = config['flvpath'] + '/' + str(flv[0])
			if flv[3] == 'pass':
				new_flv.append(flv[0])
				new_flv.append(flv[1])
				new_flv.append(flv[2])
				cuted_flvs.append(new_flv)
				dest = dest_path + '/' + str(flv[0])
				copy(src, dest)
				retimestamp_flv.retimestamp_file_inplace(dest)
				index_flv.index_file(dest)
			elif flv[3] == 'cut_head':
				new_flv.append(course_id + '-' + str(flv[4]) + '.flv')
				new_flv.append(flv[4])
				new_flv.append(flv[2] - flv[5])
				cuted_flvs.append(new_flv)
				dest = dest_path + '/' + new_flv[0]
				if not cut_flv.cut_file(src, dest, flv[5] * 1000, None):
					logger.error('cut False at %s', str(course_id))
				else :
					retimestamp_flv.retimestamp_file_inplace(dest)
					index_flv.index_file(dest)
			elif flv[3] == 'cut_tail':
				new_flv.append(flv[0])
				new_flv.append(flv[1])
				new_flv.append(flv[5])
				cuted_flvs.append(new_flv)
				dest = dest_path + '/' + new_flv[0]
				if not cut_flv.cut_file(src, dest, None, flv[5] * 1000):
					logger.error('cut False at %s', str(course_id))
				else :
					retimestamp_flv.retimestamp_file_inplace(dest)
					index_flv.index_file(dest)
			elif flv[3] == 'cut':
				new_flv.append(course_id + '-' + str(flv[4]) + '.flv')
				new_flv.append(flv[4])
				new_flv.append(end_time - start_time)
				cuted_flvs.append(new_flv)
				dest = dest_path + '/' + new_flv[0]
				if not cut_flv.cut_file(src, dest, flv[6] * 1000, flv[7] * 1000):
					logger.error('cut False at %s', str(course_id))
				else :
					retimestamp_flv.retimestamp_file_inplace(dest)
					index_flv.index_file(dest)


		return cuted_flvs
	else :
		return False

def count_duration(cuted_flvs):
	if len(cuted_flvs) == 0 :
		return 0.0
	elif len(cuted_flvs) == 1:
		return cuted_flvs[0][2]
	else :
		return cuted_flvs[len(cuted_flvs) -1][1] - cuted_flvs[0][1] + cuted_flvs[len(cuted_flvs) - 1][2]

def save_config(replay_config, course_id):
	dest_path = config['dest_path'] + '/'+ str(course_id)
	f_name = dest_path + '/' + 'replay.config'
	f = open( f_name, 'w+')
	f.write(json.dumps(replay_config))
	f.close

if __name__ == '__main__':
	main()
