#!/usr/bin/python3

import sys
import os
import re
from datetime import datetime

freqMap = { 
	'1': '160m',
	'2': '160m',
	'3': '80m',
	'4': '80m',
	'7': '40m',
	'10': '30m',
	'14': '20m',
	'18': '17m',
	'21': '15m',
	'24': '12m',
	'28': '10m',
	'29': '10m',
	'50': '6m'
}

DEF_LOG_PGM="IngeniiLogger"
DEF_QSL_MSG="Thanks for QSO"

##################
##  M A I N 
##################

def main(args):
	global callRegex
	global cqRegex
	global QSOs
	global gridMap
	global station
	global txPower
	global loggerId
	station = args[1]
	fileList = args[2:]
	QSOs = { }
	gridMap = {}
	txPower = '%i' % (os.environ['TXPWR'] if 'TXPWR' in os.environ else 35)
	loggerId = os.environ['LOG_PGM'] if 'LOG_PGM' in os.environ else DEF_LOG_PGM

	# compile the regex to extract messages for <callsign>
	# message example:  210426_022845     7.074 Tx FT8      0  0.0 1321 KP4DQC KI5GFU EL09
	callRegex = re.compile('.*\\b'+station+'\\b.*',re.IGNORECASE)
	# define cq match to extract my current gridsquare
	# std:			CQ KP4DQC FK67
	# contest: 	CQ POTA KG4WZZ EM74
	cqRegex = re.compile('.*CQ\s.*\\b([A-Z0-9]+)\s+([A-Z]{2}[0-9]{2})$',re.IGNORECASE)

	# process each file
	for fileName in fileList:
		getCallRecords(station,fileName)


def getCallRecords(callsign,fileName):
	callHits = []
	qsoList = []
	qsoLogged = {}
	print("\n***** ",fileName," *****\n\tGet ",callsign," conversations")
	with open(fileName) as inFile:
		for record in inFile:

			# check for CQ calls
			cqMatch = cqRegex.match(record)
			if cqMatch:
				gridMap[cqMatch.group(1)] = cqMatch.group(2)
				
			else:
				# check for all callsign matching records
				callMatch = callRegex.match(record)
				if callMatch:
					message = parseRecord(record)
					if message:
						QSL = ""
						if "Rx" in message["direction"]:
							# 210426_022730     7.074 Rx FT8     23  0.0 2481 CQ NT6X DM13
							QSL = mergeRecieved(message)
						else:
							# 21042_0023045     7.074 Tx FT8      0  0.0 1321 VE2DFY KI5GFU EL09
							QSL = mergeTransmission(message)

						if rrrFinal(message["message"]):
						    key = ('%s_%s' % (QSL , QSOs[QSL]['time_on']))
						    if key not in qsoLogged:
						        qsoLogged[key] = True
						        callHits.append(genAdifRecord(QSOs[QSL]))

	if len(callHits) > 0:
		writeQsoLog(callHits)


def mergeRecieved(record):
	QSL = record["call_from"]
	initSQO(QSL,record)
	return QSL
	

def mergeTransmission(record):
	QSL = record["call_to"]
	initSQO(QSL,record)
	return QSL


def initSQO(callsign,message):
	if callsign in QSOs:
		QSOs[callsign]["time_off"] = message["qso_time"]
		QSOs[callsign]["qso_date_off"] = message["qso_date"]
		if "rst_sent" in message:
			QSOs[callsign]["rst_sent"] = message["rst_sent"]
		if "rst_rcvd" in message:
			QSOs[callsign]["rst_rcvd"] = message["rst_rcvd"]
		if callsign in gridMap:
			QSOs[callsign]["gridsquare"] = gridMap[callsign]
		if station in gridMap:
			QSOs[callsign]["my_gridsquare"] = gridMap[station]
	else:
		QSOs[callsign] = {
		    'call' : callsign,
		    'mode' : message["mode"],
		    'band' : message["band"],
		    'freq' : message["freq"],
		    'rst_sent' : "",
		    'rst_rcvd' : "",
		    'time_on' : message["qso_time"],
		    'time_off' : message["qso_time"],
		    'qso_date' : message["qso_date"],
		    'qso_date_off' : message["qso_date"],
		    'station_callsign' : station,
		    'operator' : station,
		    'gridsquare' : "",
		    'my_gridsquare' : ""
		}

def rrrFinal(message):
	if message == "RRR":
		return True

	if message == "RR73":
		return True

	if message == "73":
		return True

	return False
		
def computeBand(freq):
	parts = freq.split('.')
	return freqMap[parts[0]]


def parseRecord(record):
	message = {}

	# parse record for known components
	# ex:  210426_022945     7.074 Tx FT8      0  0.0 1321 N1UMJ KI5GFU EL09
	messageRegEx = re.compile('^([0-9]{6})_([0-9]{6})\s+([\d\.]+)\s([rt]x)\s+([a-z0-9]{3,5}).*\s(\d{2,5})\s+([a-z0-9]{4,7})\s+([a-z0-9]{4,7})\s+([a-z0-9\-\+]+).?',re.IGNORECASE);
	match = messageRegEx.match(record)
	if match:
		message = {
			'qso_date': '20'+match.group(1),
			'qso_time': match.group(2),
			'freq': match.group(3),
			'band': computeBand(match.group(3)),
			'direction': match.group(4),
			'mode': match.group(5),
			'offset': match.group(6),
			'call_to': match.group(7),
			'call_from': match.group(8),
			'message': match.group(9)
		}
	
		comment = match.group(9).lstrip();	

		if comment.startswith('+') or comment.startswith('-'):
			message["rst_rcvd"] = comment
		if comment.startswith('R+') or comment.startswith('R-'):
			message["rst_sent"] = comment
		
		return message

	return message


def genAdifRecord(QSO):
	# <call:6>WD5BFH <gridsquare:4>EM26 <mode:3>FT8 <rst_sent:3>-12 <rst_rcvd:3>-19 <qso_date:8>20210515 <time_on:6>165230 <qso_date_off:8>20210515 <time_off:6>165315 <band:3>20m <freq:9>14.076320 <station_callsign:6>KI5GFU <my_gridsquare:4>EL09 <tx_pwr:2>75 <comment:25>FT8  Sent: -12  Rcvd: -19 <operator:6>KI5GFU <eor>
	# use env or def settings from some extra ADIF fields
	QSL_MSG = os.environ['QSL_MSG'] if 'QSL_MSG' in os.environ else DEF_QSL_MSG
	# assemble record
	return '%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s <eor>' % ( 
		addRecord("call",QSO["call"] ), 
		addRecord("gridsquare",QSO["gridsquare"] ), 
		addRecord("mode",QSO["mode"] ), 
		addRecord("rst_sent",QSO["rst_sent"] ), 
		addRecord("rst_rcvd",QSO["rst_rcvd"] ), 
		addRecord("qso_date",QSO["qso_date"] ), 
		addRecord("time_on",QSO["time_on"] ), 
		addRecord("qso_date_off",QSO["qso_date_off"] ), 
		addRecord("time_off",QSO["time_off"] ), 
		addRecord("band",QSO["band"] ), 
		addRecord("freq",QSO["freq"] ), 
		addRecord("log_pgm",loggerId),
		addRecord("qslmsg",QSL_MSG),
		addRecord("station_callsign",QSO["station_callsign"] ), 
		addRecord("my_gridsquare",QSO["my_gridsquare"] ), 
		addRecord("tx_pwr",txPower), 
		addRecord("comment",('%s Sent: %s  Rcvd: %s' % (QSO["mode"],QSO["rst_sent"],QSO["rst_rcvd"])) ), 
		addRecord("operator",QSO["operator"] ), 
	)

def writeQsoLog(logEntries):

	timestamp = datetime.now().strftime("%y%m%d-%H")
	fname = "./ALL_"+timestamp+".ADI"
	print("\t* Writing ",len(logEntries)," QSOs to ",fname)
	f = open(fname, "w")
	f.write(getAdifHeader())
	f.write("\n".join(logEntries))
	f.close()


def getAdifHeader():
    datestamp = datetime.now().strftime("%Y%m%d")
    template = """ADIF Export
<adif_ver:5>3.1.1
<created_timestamp:15>%s 000001
<programid:%i>%s
<programversion:5>1.0.0
<eoh>
"""
    return (template % ( datestamp, len(loggerId), loggerId ))


def addRecord(name,value):
	return ('<%s:%i>%s ' % ( name, len(value), value))

######################
#  START 
######################

main(sys.argv)

exit()
