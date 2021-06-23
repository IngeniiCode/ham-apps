#!/usr/bin/python3

import sys

wantedGrids = {
	#'HI': ['BL01','BL11','BL10','BL20','BL19','BL29'],
	'ME': ['FN57','FN56','FN54','FN64','FN65','FN66','FN46','FN45','FN44','FN43']
	#'NJ': ['FM29','FN20','FN30'],
	#'VT': ['FN32','FN33','FN34','FN44']
}
foundQSO = { }


def main(wGrids):
	print('Starting Python3 Grid Parser')
	# show file pattern
	processFilePattern(sys.argv[1:],wGrids)
	writeHitsToAdif(foundQSO)
	print("\nAll files processed\n\n")

def processFilePattern(fpat,grids):
	for fName in fpat:
		#print("\tWant to process ",fName)
		with open(fName) as inFile:
			checkForWantedGrids(grids,inFile.readlines())

def checkForWantedGrids(grids,fLines):
	for state in grids:
		stateGrids = grids[state]
		if foundQSO.get(state) is None:
			foundQSO[state] = []
		#print("\t\tGrid Members ",state,stateGrids);
		for line in fLines:
			for grid in stateGrids:
				if grid in line:
					foundQSO[state].append(line.rstrip())
				
def writeHitsToAdif(hits):
	for state in hits:
		uniqueStateHits = list(set(hits[state]))	
		print("\n------ ",state,"  - hits: ",len(uniqueStateHits))
		if len(uniqueStateHits) > 0:
			print("\n".join(uniqueStateHits))
			writeQsoLog(state,uniqueStateHits)

def writeQsoLog(state,uniqueStateHits):
	fname = "./"+state+".ADI"
	print("\t* Writing ",len(uniqueStateHits)," QSOs to ",fname)
	f = open(fname, "w")
	f.write(getAdifHeader())
	f.write("\n".join(uniqueStateHits))
	f.close()
	
def getAdifHeader():
	return """ADIF Export
<adif_ver:5>3.1.1
<created_timestamp:15>20210401 000001
<programid:6>WSJT-X
<programversion:5>2.3.1
<eoh>
""" 


# Start operations
main(wantedGrids)

# Complete operations
exit()
