#!/usr/bin/python

import sys
import argparse
import os
import re
import json

def padLeft(string, x):
	return str(string).zfill(x)

def removeExcessDots(filename):
	base, extension = os.path.splitext(filename)
	dotlessBase = base.replace('.', ' ')
	return dotlessBase + extension

def getSubDirs(path):
	dir, subdirs, files = next(os.walk(path))
	return sorted(subdirs)

def getFiles(path):
	dir, subdirs, files = next(os.walk(path))
	return sorted(files)

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

def extractSeasonInfo(string):
	return extractLongHand('season', string) \
		or extractShortHand('S', string)

def extractEpisodeInfo(string):
	return extractLongHand('episode', string) \
		or extractShortHand('E', string) #\
		#or extractShortHand('', string)

def findEpisodes(path):
	episodes = []
	files = getFiles(path)

	for file in files:
		cleanFileName = removeExcessDots(file)
		episodeInfo = extractEpisodeInfo(cleanFileName)

		if episodeInfo == None:
			continue

		episodeNumber, _, _ = episodeInfo
		episodes.append({
			'number': episodeNumber,
			'raw': file,
			'clean': cleanFileName,
		})

	return episodes

def findSeasons(path):
	seasons = []
	folders = getSubDirs(path)

	for folder in folders:
		cleanFolderName = removeExcessDots(folder)
		seasonInfo = extractSeasonInfo(cleanFolderName)

		if seasonInfo == None:
			continue

		seasonNumber = seasonInfo[0]
		episodes = findEpisodes('{}/{}'.format(path, folder))
		seasons.append({
			'number': seasonNumber,
			'raw': folder,
			'clean': cleanFolderName,
			'episodes': episodes,
		})

	return seasons

def findSeries(path):
	series = []
	folders = getSubDirs(path)

	for folder in folders:
		cleanFolderName = removeExcessDots(folder)
		seasonInfo = extractSeasonInfo(cleanFolderName)
		seasonPath = '{}/{}'.format(path, folder)

		seriesData = {
			'raw': folder,
			'clean': cleanFolderName,
		}

		if seasonInfo != None:
			# Assume is folder of a season
			seasonNumber, seasonNumberStartPos, _ = seasonInfo
			seriesName = cleanFolderName[:seasonNumberStartPos - 1]
			episodes = findEpisodes(seasonPath)

			seriesData['seasons'] = [{
				'number': seasonNumber,
				'raw': '',
				'clean': cleanFolderName,
				'episodes': episodes,
			}]
			series.append(seriesData)
			continue

		seasons = findSeasons(seasonPath)

		if len(seasons):
			seriesData['seasons'] = seasons
			series.append(seriesData)

	return series

def main():
	series = findSeries(rootPath)
	#print(json.dumps(series, indent=2))

parser = argparse.ArgumentParser(description='Clean up your media files names and structure')
parser.add_argument('root')
args = parser.parse_args()

rootPath = sys.argv[1] if len(sys.argv) >= 2 else '.'

if not os.path.exists(rootPath):
	print('Folder or file "{}" does not exist'.format(rootPath))
	sys.exit(0)

main()
