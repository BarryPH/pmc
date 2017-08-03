#!/usr/bin/python

import sys
import argparse
import os
import re

def removeExcessDots(filename):
	lastDotPosition = filename.rfind('.')
	base = filename[:lastDotPosition]
	extension = filename[lastDotPosition:]

	if extension.find(' '):
		base = base + extension
		extension = ''

	# Replace all instances of "." not followed by a space
	base = re.sub(r'\.(?! )', ' ', base)
	return base + extension

def getSubDirs(directory):
	dir, subdirs, files = next(os.walk(directory))
	return sorted(subdirs)

def extractLongHand(search, string):
	pos = string.lower().find(search.lower())

	if pos != -1:
		numberStartPos = pos + len(search) + 1
		numberEndPos = string.find(' ', numberStartPos)

		if numberEndPos == -1:
			numberEndPos = len(string)

		return string[numberStartPos:numberEndPos]

def extractShortHand(search, string):
	pos = re.search(r'(?i){}\d+'.format(search), string)

	if pos != None:
		number = string[pos.start() + 1:pos.end()]
		# Converting to int removes possible leading '0'
		return int(number)


def extractSeasonNumber(string):
	return extractLongHand('season', string) \
		or extractShortHand('S', string)

def extractEpisodeNumber(string):
	return extractLongHand('episode', string) \
		or extractShortHand('E', string)

def main():
	directory = sys.argv[1] if len(sys.argv) >= 2 else '.'

	if not os.path.exists(directory):
		print('Folder or file "{}" does not exist'.format(directory))
		sys.exit(0)

	seriesFolders = getSubDirs(directory)

	for seriesFolder in seriesFolders:
		seriesName = seriesFolder
		seasonFolders = getSubDirs('{}/{}'.format(directory, seriesFolder))

		if not len(seasonFolders):
			continue

		for seasonFolder in seasonFolders:
			cleanSeasonFolder = removeExcessDots(seasonFolder)
			seasonNumber = extractSeasonNumber(cleanSeasonFolder)
			seasonNumber = None

			dir, subdirs, files = next(os.walk('{}/{}/{}'.format(directory, seriesFolder, seasonFolder)))
			episodeFiles = sorted(files)

			for episode in episodeFiles:
				cleanEpisodeName = removeExcessDots(episode)
				episodeNumber = extractEpisodeNumber(cleanEpisodeName)
				episodeNumber = None

parser = argparse.ArgumentParser(description='Clean up your media files names and structure')
parser.add_argument('root')
args = parser.parse_args()

main()
