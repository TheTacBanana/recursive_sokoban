from os import listdir
from os.path import isfile, join
from typing import DefaultDict
import json

from level import Level

class Loader():
    def __init__(self):
        pass

    def LoadSettings(self):
        json_data = open("settings.json")
        return json.load(json_data)

    def LoadDirectory(self, dir):
        directoryList = listdir(dir)

        validFiles = [f for f in directoryList if isfile(join(dir, f)) and f[-4:] == ".lvl"]

        return validFiles

    def GetLevel(self, filedir):
        file = open(f"Levels/{filedir}", "r")

        loadedLevel = DefaultDict(str)
        levelInfo = DefaultDict(str)
        levelInfo["BlockSpawns"] = []
        levelInfo["BlockEnds"] = []
        levelInfo["Blocks"] = []

        openStack = []

        row = 0
        for line in [f.strip() for f in file.readlines()]:
            if line[0] == "<" and line[-1] == ">": # Tags
                if line[1] == "/": # Close Tags
                    tagName = line[2:-1]
                    if len(openStack) > 0 and openStack[-1] == tagName:
                        openStack.pop()
                    else:
                        print("Error loading Level, tags not aligned")
                        quit()
                else: # Open Tags
                    tagName = line[1:-1]
                    if len(openStack) > 0 and openStack[-1] == tagName:
                        print("Error loading Level, tags not aligned")
                        quit()
                    else:
                        openStack.append(tagName)
                        row = 0
            else:
                for c in range(len(line)):
                    char = line[c]

                    if char == ".":
                        levelInfo["PlayerPos"] = [row, c]
                        levelInfo["PlayerSpawn"] = (row, c)
                        levelInfo["PlayerSpawnsIn"] = openStack[-1]
                        levelInfo["PlayerIsIn"] = openStack[-1]

                        loadedLevel[openStack[-1]] += "-"
                        
                    elif char == "?":
                        levelInfo["PlayerEnd"] = (row, c)
                        levelInfo["PlayerEndsIn"] = openStack[-1]

                        loadedLevel[openStack[-1]] += "?"

                    elif char == "+":
                        levelInfo["BlockSpawns"].append([openStack[-1], [row, c]])
                        levelInfo["Blocks"].append([openStack[-1], [row, c]])

                        loadedLevel[openStack[-1]] += "-"

                    elif char == "=":
                        levelInfo["BlockEnds"].append([openStack[-1], [row, c]])

                        loadedLevel[openStack[-1]] += "="

                    else:
                        loadedLevel[openStack[-1]] += char
                row += 1

        createdLevel = Level(loadedLevel, levelInfo)

        return createdLevel
