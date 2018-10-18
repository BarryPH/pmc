#!/usr/bin/python

import sys
import argparse
import os
import re

def padLeft(string, x):
	return str(string).zfill(x)

def removeExcessDots(filename):
	lastDotPos = filename.rfind('.')
	base = filename[:lastDotPos]
	extension = filename[lastDotPos:]

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

		longhand = string[numberStartPos:numberEndPos]
		return longhand, pos, numberEndPos

def extractShortHand(search, string):
	pos = re.search(r'(?i){}\d+'.format(search), string)

	if pos != None:
		number = string[pos.start() + len(search):pos.end()]
		# Converting to int removes possible leading '0'
		return int(number), pos.start(), pos.end()

def extractSeasonNumber(string):
	return extractLongHand('season', string) \
		or extractShortHand('S', string)

def extractEpisodeNumber(string):
	return extractLongHand('episode', string) \
		or extractShortHand('E', string) #\
		#or extractShortHand('', string)

def findEpisodes(path):
	dir, subdirs, files = next(os.walk(path))
	files = sorted(files)

	for file in files:
		cleanFolderName = removeExcessDots(file)
		episodeNumberData = extractEpisodeNumber(cleanFolderName)

		if episodeNumberData == None:
			continue

		episodeNumber, _, _ = episodeNumberData
		print('\t\t|- EP {}: {}'.format(padLeft(episodeNumber, 2), cleanFolderName))

def findSeasons(path):
	folders = getSubDirs(path)

	for folder in folders:
		cleanFolderName = removeExcessDots(folder)
		seasonNumberData = extractSeasonNumber(cleanFolderName)

		if seasonNumberData == None:
			continue

		seasonNumber = seasonNumberData[0]
		print('\t|- Season {}:'.format(padLeft(seasonNumber, 2)))
		findEpisodes('{}/{}'.format(path, folder))

def findSeries(path):
	folders = getSubDirs(path)

	for folder in folders:
		cleanFolderName = removeExcessDots(folder)
		seasonNumberData = extractSeasonNumber(cleanFolderName)
		seasonPath = '{}/{}'.format(path, folder)

		if seasonNumberData != None:
			# Assume is folder of a season
			seasonNumber, seasonNumberStartPos, _ = seasonNumberData
			seriesName = cleanFolderName[:seasonNumberStartPos - 1]
			print('{}:'.format(seriesName))
			print('\t|- Season {}:'.format(padLeft(seasonNumber, 2)))
			findEpisodes(seasonPath)
			continue

		print('{}:'.format(cleanFolderName))
		findSeasons(seasonPath)

def main():
	findSeries(directory)

parser = argparse.ArgumentParser(description='Clean up your media files names and structure')
parser.add_argument('root')
args = parser.parse_args()

directory = sys.argv[1] if len(sys.argv) >= 2 else '.'

if not os.path.exists(directory):
	print('Folder or file "{}" does not exist'.format(directory))
	sys.exit(0)

main()
