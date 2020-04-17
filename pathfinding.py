import json
import operator
import bisect

class PathFinder:

    class Node:
        def __init__(self, col, row):
            self.eid = None
            self.evaluated = False
            self.g = 0
            self.h = 0
            self.value = 0
            self.col = col
            self.row = row
            self.children = []

        def __lt__(self, other):
            return self.value < other.value

        def __eq__(self, other):
            return self.value == other.value

        def __hash__(self):
            return hash(hash(self.col) + hash(self.row))

        def __repr__(self):
            return "True: {}".format( int(self.value)) if self.evaluated else "False"

    def __init__(self, cols=15, rows=15):
        self.cols = cols
        self.rows = rows
        self.openSet = []
        self.endP = None
        self.G = []

        # Init empty G
        for c in range(self.cols):
            self.G.append([])
            for r in range(self.rows):
                self.G[c].append(PathFinder.Node(c, r))

    def clearGraph(self):
        for c in range(self.cols):
            for r in range(self.rows):
                self.G[c][r].evaluated = False
                self.openSet = []
                # self.G[c][r].g = 0
                # self.G[c][r].h = 0
                # self.G[c][r].value = 0

    def addEntityToG(self, entity):
        sizeDif = entity['size']
        for c in range(sizeDif):
            for r in range(sizeDif):
                self.G[entity['col']+c][entity['row']+r].eid = entity['eid']

    def removeEntityFromG(self, entity):
        sizeDif = entity['size']
        for c in range(sizeDif):
            for r in range(sizeDif):
                self.G[entity['col']+c][entity['row']+r].eid = None

    def getChildren(self, n):
        children = [
            self.evaluate(n.col, n.row-1, n),
            self.evaluate(n.col+1, n.row, n),
            self.evaluate(n.col, n.row+1, n),
            self.evaluate(n.col-1, n.row, n)
        ]
        return filter(None, children)

    def evaluate(self, col, row, n):
        if col < 0 or row < 0 or col >= self.cols or row >= self.rows or (self.G[col][row].eid != None and self.G[col][row].eid != self.endP.eid):
            return
        child = self.G[col][row]
        if child.evaluated:
            if n.g+1 < child.g:
                self.G[child.parent[0]][child.parent[1]].children.remove(child)
                child.parent = [n.col, n.row]
                n.children.append(child)
                
                # child.propogateGChange(self.g+1)

            return

        child.parent = [n.col, n.row]
        child.g = n.g + 0.99
        child.h = abs(col-self.endP.col) + abs(row-self.endP.row)
        child.value = child.g + child.h
        child.evaluated = True
        n.children.append(child)
        return child

    def findShortestPath(self):
        lowest = self.openSet.pop(0)
        # print("{col}, {row}".format(col=lowest.col, row=lowest.row))
        if lowest.eid == self.endP.eid:
            return lowest

        for child in self.getChildren(lowest):
            bisect.insort(self.openSet, child)

    def navigate(self, toEntity, fromEntity):
        # print("Finding: {col}, {row}".format(col=toEntity['col'] ,row=toEntity['row']))
        self.endP = self.G[toEntity['col']][toEntity['row']]
        startNode = self.G[fromEntity['col']][fromEntity['row']]
        startNode.g = 0
        self.openSet.append(startNode)
        startNode.evaluated = True
        rc = None
        while len(self.openSet) != 0 and not rc:
            rc = self.findShortestPath()
        if rc is None:
            self.clearGraph()
            return None
        path = []
        parent = self.G[rc.parent[0]][rc.parent[1]]
        while parent != startNode:
            path.append((parent.col, parent.row))
            parent = self.G[parent.parent[0]][parent.parent[1]]
        self.clearGraph()
        return path
