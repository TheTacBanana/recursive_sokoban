from tabnanny import check
import pygame
from copy import copy, deepcopy

class Level():
    def __init__(self, leveldict, levelinfo):
        self.originalLevel = deepcopy(leveldict)
        self.originalLevelInfo = deepcopy(levelinfo)
        
        self.leveldict = leveldict
        self.levelinfo = levelinfo

        self.walkabletiles = ["-", "=", "?"]

        self.wallsprite = pygame.image.load("Wall.png")
        self.playersprite = pygame.image.load("Player.png")
        self.blocksprite = pygame.image.load("Block.png")
        self.acceptsprite = pygame.image.load("Acceptor.png")

    def GetStringInfo(self, strin): # Determines Row & Col Count, and if contains other objects
        split = strin.split("/")
        rows = len(split) - 1
        cols = max([len(f) for f in split])
        contains = True in [c in self.leveldict for c in strin]

        return rows, cols, contains

    def DrawBackround(self, res, centeredpos):
        newkey = None
        location = None
        for key in self.leveldict:
            get = self.leveldict[key].replace("/", "").find(self.levelinfo["PlayerIsIn"])
            if get != -1: 
                location = get
                newkey = key
                break

        if newkey != None:
            info = self.GetStringInfo(self.leveldict[newkey])
            pos = (location // info[1], location % info[0])

            surf = self.DrawLevelRecursive(res, newkey, 2)
            scaled = pygame.transform.scale(surf, (res[0] * info[1], res[1] * info[0]))

            drawpos = (centeredpos[0] - (res[0] * pos[1]), centeredpos[1] - (res[1] * pos[0]))

            return scaled, drawpos

        else:
            return None, None

    def DrawFinalLevel(self, targetres, maxdepth):
        surf = self.DrawLevelRecursive(targetres, self.levelinfo["PlayerIsIn"], maxdepth)
        return surf

    def DrawLevelRecursive(self, res, key, depth):
        info = self.GetStringInfo(self.leveldict[key])
        
        tileres = (res[0] // info[0], res[1] // info[1])
        if tileres[0] <= 0: tileres = (1, tileres[1])
        if tileres[1] <= 0: tileres = (tileres[0], 1)

        newres = (tileres[0] * info[0], tileres[1] * info[1])

        surface = pygame.Surface(newres)
        
        grid = self.leveldict[key]
        row, col = 0, -1
        for c in range(len(grid)): 
            if grid[c] == "/":
                row += 1
                col = -1
                continue
            else:
                col += 1

            
            if grid[c] == "#":
                scaled = pygame.transform.scale(self.wallsprite, tileres)
                surface.blit(scaled, (col * tileres[0], row * tileres[1]))

            elif grid[c] == "=" or grid[c] == "?":
                scaled = pygame.transform.scale(self.acceptsprite, tileres)
                surface.blit(scaled, (col * tileres[0], row * tileres[1]))

            elif grid[c] in self.leveldict and depth > 1 :
                if depth > 1 and tileres[0] > 1 and tileres[1] > 1:
                    tempsurf = self.DrawLevelRecursive(tileres, grid[c], depth - 1)
                    surface.blit(tempsurf, (col * tileres[0], row * tileres[1]))
                else:
                    tempsurf = self.DrawLevelRecursive(tileres, grid[c], 0)
                    surface.blit(tempsurf, (col * tileres[0], row * tileres[1]))

            if self.levelinfo["PlayerPos"] == [row, col] and self.levelinfo["PlayerIsIn"] == key:
                scaled = pygame.transform.scale(self.playersprite, tileres)
                surface.blit(scaled, (col * tileres[0], row * tileres[1]))

            if [key, [row, col]] in self.levelinfo["Blocks"] :
                scaled = pygame.transform.scale(self.blocksprite, tileres)
                surface.blit(scaled, (col * tileres[0], row * tileres[1]))
                
        return pygame.transform.scale(surface, res)

    def ResetLevel(self):
        self.leveldict = deepcopy(self.originalLevel)
        self.levelinfo = deepcopy(self.originalLevelInfo)

    def MovePlayer(self, direction):
        ogpos = copy(self.levelinfo["PlayerPos"])
        if direction == 0:   newpos = [ogpos[0] - 1, ogpos[1]]
        elif direction == 1: newpos = [ogpos[0], ogpos[1] + 1]
        elif direction == 2: newpos = [ogpos[0] + 1, ogpos[1]]
        elif direction == 3: newpos = [ogpos[0], ogpos[1] - 1]

        info = self.GetStringInfo(self.leveldict[self.levelinfo["PlayerIsIn"]])
        if (0 <= newpos[0] <= info[0] - 1) and (0 <= newpos[1] <= info[1] - 1): 
            char = self.GetPos(self.levelinfo["PlayerIsIn"], newpos)
            if char in self.walkabletiles:
                if [self.levelinfo["PlayerIsIn"], newpos] in self.levelinfo["Blocks"]:
                    result = self.PushBlock(self.levelinfo["PlayerIsIn"], ogpos, direction)

                    if result:
                        self.levelinfo["PlayerPos"] = newpos
                else:
                    self.levelinfo["PlayerPos"] = newpos
            elif char in self.leveldict:
                flipdir = (2, 3, 0, 1)
                result, pos = self.CheckSideIn(char, flipdir[direction])

                if result:
                    self.levelinfo["PlayerPos"] = pos
                    self.levelinfo["PlayerIsIn"] = char

        else:
            newkey = None
            location = None
            for key in self.leveldict:
                get = self.leveldict[key].replace("/", "").find(self.levelinfo["PlayerIsIn"])
                if get != -1: 
                    location = get
                    newkey = key
                    break
            
            info = self.GetStringInfo(self.leveldict[newkey])
            pos = (location // info[1], location % info[0])

            result, newpos = self.CheckSideOut(newkey, pos, direction)

            if result:
                if [newkey, newpos] in self.levelinfo["Blocks"]:
                    result = self.PushBlock(newkey, self.IncrementDirection(deepcopy(newpos), self.FlipDirection(direction)), direction)

                    if result:
                        self.levelinfo["PlayerPos"] = newpos
                        self.levelinfo["PlayerIsIn"] = newkey
                else:
                    self.levelinfo["PlayerPos"] = newpos
                    self.levelinfo["PlayerIsIn"] = newkey

    def GetPos(self, key, pos):
        lines = self.leveldict[key].split("/")
        return lines[pos[0]][pos[1]]

    def CheckSideIn(self, key, side):
        info = self.GetStringInfo(self.leveldict[key])
        middle = (info[0]//2, info[1]//2)

        if side == 0:   newpos = [0, middle[1]]
        elif side == 1: newpos = [middle[0], info[1] - 1]
        elif side == 2: newpos = [info[0] - 1, middle[1]]
        elif side == 3: newpos = [middle[1], 0]

        if self.GetPos(key, newpos) in self.walkabletiles:
            if [key, newpos] in self.levelinfo["Blocks"]:
                result = self.PushBlock(key, self.IncrementDirection(deepcopy(newpos), side), self.FlipDirection(side))
                return result, newpos
            else:
                return True, newpos
        else:
            return False, None

    def CheckSideOut(self, key, pos, direction):
        if direction == 0:   newpos = [pos[0] - 1, pos[1]]
        elif direction == 1: newpos = [pos[0], pos[1] + 1]
        elif direction == 2: newpos = [pos[0] + 1, pos[1]]
        elif direction == 3: newpos = [pos[0], pos[1] - 1]

        if self.GetPos(key, newpos) in self.walkabletiles:
            return True, newpos
        else:
            return False, None

    def PushBlock(self, key, pos, direction):
        ogpos = deepcopy(pos)
        newpos = self.IncrementDirection(pos, direction)

        info = self.GetStringInfo(self.leveldict[key])

        if (0 <= newpos[0] <= info[0] - 1) and (0 <= newpos[1] <= info[1] - 1):
            char = self.GetPos(key, newpos)

            if char in self.walkabletiles:
                if [key, newpos] in self.levelinfo["Blocks"]:
                    result = self.PushBlock(deepcopy(key), newpos, direction)
                    if result:
                        if [key, newpos] in self.levelinfo["Blocks"]:
                            index = self.levelinfo["Blocks"].index([key, newpos])
                            self.levelinfo["Blocks"][index] = [key, self.IncrementDirection(newpos, direction)]
                        return True
                    else: 
                        return False
                else:
                    return True

            elif char in self.leveldict:
                checkside, newdimpos = self.CheckSideIn(char, self.FlipDirection(direction))

                if checkside:
                    result = self.PushBlock(char, self.IncrementDirection(deepcopy(newdimpos), self.FlipDirection(direction)), direction)
                    if result:
                        index = self.levelinfo["Blocks"].index([key, ogpos])
                        self.levelinfo["Blocks"][index] = [char, newdimpos]

                        return True
                    else:
                        return False
                else:
                    return False

        else:
            newkey = None
            location = None
            for k in self.leveldict:
                get = self.leveldict[k].replace("/", "").find(key)
                if get != -1: 
                    location = get
                    newkey = k
                    break
            
            info = self.GetStringInfo(self.leveldict[newkey])
            newdimpos = (location // info[1], location % info[0])

            checkside, outpos = self.CheckSideOut(newkey, newdimpos, direction)

            if checkside:
                result = self.PushBlock(newkey, self.IncrementDirection(outpos, self.FlipDirection(direction)), direction)

                if result:
                    index = self.levelinfo["Blocks"].index([key, pos])
                    self.levelinfo["Blocks"][index] = [newkey, outpos]

                    return True
                else:
                    return False
            
            else:   
                return False

    def IncrementDirection(self, pos, direction):
        if direction == 0:   newpos = [pos[0] - 1, pos[1]]
        elif direction == 1: newpos = [pos[0], pos[1] + 1]
        elif direction == 2: newpos = [pos[0] + 1, pos[1]]
        elif direction == 3: newpos = [pos[0], pos[1] - 1]

        return newpos

    def FlipDirection(self, direction):
        flipdir = (2, 3, 0, 1)
        return flipdir[direction]