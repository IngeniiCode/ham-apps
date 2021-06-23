#!/usr/bin/python3

import sys
import re

countryPrefixes = {
  'Argentina': [ 'L[O-W]','LU' ],
  'Aruba': [ 'P4' ],
  'Bolivia': [ 'CP' ],
  'Bonaire': [ 'PJ4' ],
  'Brazil': [ 'P[P-Y]' ],
  'Chile': [ 'C[A-C]' ],
  'Colombia': [ 'H[J-K]' ],
  'Curacao': [ 'PJ2' ],
  'Easter_Island': [ 'CE0Y' ],
  'Ecuador': [ 'H[CD]' ],
  'Falkland_Islands': [ 'VP8' ],
  'Fernando_de_Noronha': [ 'P[P-Y]0', 'PY0F' ],
  'French_Guiana': [ 'FY' ],
  'Galapagos_Islands': [ 'H[CD]8' ],
  'Guyana': [ '8R' ],
  'Juan_Fernandez_Islands': [ 'CE0Z' ],
  'Malpelo_Island': [ 'HK0' ],
  'Paraguay': [ 'ZP' ],
  'Peru': [ 'O[A-C]' ],
  'San_Felix': [ 'CE0X' ],
  'South_Georgia_Islands': [ 'LU\\Z' 'VP8' ],
  'South_Orkney_Islands': [ 'LU\\Z' 'VP8' ],
  'South_Sandwich_Islands': [ 'LU\\Z' 'VP8' ],
  'South_Shetland_Islands': ['LU\\Z' 'VP8' 'RI1' ],
  'St_Peter_&amp;_St_Paul_Rocks': [ 'P[P-Y]0', 'PY0S' ],
  'Suriname': [ 'PZ' ],
  'Trindade_and_Martim_Vaz_Island': [ 'P[P-Y]0', 'PY0T' ],
  'Trinidad_and_Tobago': [ '9[Y-Z]' ],
  'Uruguay': [ 'C[V-X]' ],
  'Venezuela': [ 'Y[V-Y]' ],
  'ITU_Geneva': [ '4U', '4U[0-9]ITU','4U1WRC' ],
  'United_Nations': [ '4U','4U[0-9]UN' ],
}


foundQSO = {  }

def main(wantedPrefixes):
	print('Starting South American ITU Prefix Parser')
	# show file pattern
	processFilePattern(sys.argv[1:],wantedPrefixes)
	writeHitsToAdif(foundQSO)
	print("\nAll files processed\n\n")

def processFilePattern(fpat,prefixes):
	for fName in fpat:
		print("\tWant to process ",fName)
		with open(fName) as inFile:
			try:
				checkForWantedPrefixes(prefixes,inFile.readlines())
			except:
				print("\t** ",fName," skipped")

def checkForWantedPrefixes(prefixes,fLines):

	for country in prefixes:
		for callPrefix in prefixes[country]:
			if callPrefix:
				patStr = "^<call:\d+>"+callPrefix+"[A-Z0-9]+\\b"
				callPattern = re.compile(patStr)
				for line in fLines:
					match = callPattern.match(line)
					if match:
						if foundQSO.get(country) is None:
							foundQSO[country] = []
						foundQSO[country].append(line.rstrip())	

				
def writeHitsToAdif(hits):
	allSouthAmerica = []
	for country in hits:
		uniqueCountryHits = list(set(hits[country]))
		allSouthAmerica += list(set(hits[country]))
		if len(uniqueCountryHits) > 0:
			print("\n------ ",country,"  - hits: ",len(uniqueCountryHits))
			#print("\n".join(uniqueCountryHits))
			writeQsoLog(country,uniqueCountryHits)
	if len(allSouthAmerica) > 0:
		print("\n------ All South America  hits: ",len(allSouthAmerica))
		writeQsoLog('ALL-COUNTRIES',allSouthAmerica)

def writeQsoLog(country,uniqueCountryHits):
	fname = "./SA_"+country+".ADI"
	print("\t* Writing ",len(uniqueCountryHits)," QSOs to ",fname)
	f = open(fname, "w")
	f.write(getAdifHeader())
	f.write("\n".join(uniqueCountryHits))
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
main(countryPrefixes)

# Complete operations
exit()
