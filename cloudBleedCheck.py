#!/usr/bin/python3

"""
Website comparison parser
Takes a csv dump as argument
Compares to a master list of sites affected by cloudbleed
and outputs matching sites from the lastpass dump

Can also check against any other password csv, so long as urls are in
the leftmost column
"""
import sys
import csv
import os
import re
import urllib.request
import zipfile

AFFECTED = 'https://github.com/pirate/sites-using-cloudflare/archive/master.zip'
AFFECTED_ZIP = 'sorted_unique.zip'
AFFECTED_TXT = 'sites-using-cloudflare-master' + os.sep + 'sorted_unique_cf.txt'
REGEX = '(?:https?:\/\/)?(?:\w*\.)?([a-z0-9\-]+\.[a-z\.]+)(?:[\/]?).*'

def main(lastpassFile):
	#parse lastpass dump
	print("Parsing your sites....")
	sites = open(lastpassFile, newline='')
	parser = csv.reader(sites, delimiter=',')
	scrubbedSites = []
	for row in parser:
		raw = str(row[0])
		# print("'" + raw + "'")
		matches = re.search(REGEX, raw)
		try:
			match = matches.group(1)
			scrubbedSites += [match]
		except:	pass

	if len(scrubbedSites) == 0:
		print("Huh, you don't have any sites in your csv file. Maybe you have them formatted incorrectly.")
		return

	#Download list of all known affected sites thus far
	print("Downloading affected sites list....")
	httpData = urllib.request.urlopen(AFFECTED)
	compressedList = open(AFFECTED_ZIP, 'wb')
	compressedList.write(httpData.read())
	print("Downloaded.\n")

	#unpack list
	print("Unzipping...")
	with zipfile.ZipFile(AFFECTED_ZIP) as someZip:
		someZip.extractall()
	print("Unzipped\n")

	print("Testing...")
	affectedSites = set()

	for j in open(AFFECTED_TXT):
		affectedSites.add(j[:-1])

	affectedSites = frozenset(affectedSites)

	#compare scrubbed list of lastpass sites with affected sites
	failed = open('failed.txt', 'w')
	for i in scrubbedSites:
		status = 'clear'

		if i in affectedSites:
			status = 'AFFECTED'
			failed.write(i + '\n')
		print("{0} : {1}".format(i, status))

	failed.close()
	print("DONE. Failed sites written to failed.txt")

if __name__ == '__main__':
	if(len(sys.argv) != 2):
		print("Please enter the filename for your lastpass dump as an arg")
	else:
		main(sys.argv[1])
