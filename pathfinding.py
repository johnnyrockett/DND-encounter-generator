import json
import operator
import bisect

map = None
knight = None
knightPos = None
spriteSize = 40
spriteOffset = spriteSize/2
playerPath = []
playerQuest = None
playerVel = 3

castle = None
tar_pit = None
tavern = None
tree = None
cave = None
forge = None
star = None

G = None
knightCol = None
knightRow = None
colNum = 0
rowNum = 0
stepAmount = 3*PI

openSet = []
endP = []

def vectorFor(col, row):
    x = (col - knightCol) * stepAmount + map['knight_start'][0]
    y = (row - knightRow) * stepAmount + map['knight_start'][1]
    return [x, y]

def leftOrRight(p, a, b):
    return (b[0] - a[0]) * (p[1] - b[1]) - (b[1] - a[1]) * (p[0] - b[0]) > 0

def isNotObstructed(a1, a2):
    for obstacle in map['obstacles'].values():
        for i in range(len(obstacle)):
            secondPoint = (i+1)%len(obstacle)
            a = obstacle[i]
            b = obstacle[secondPoint]
            
            if (leftOrRight(a1, a, b) != leftOrRight(a2, a, b)) and (leftOrRight(a, a1, a2) != leftOrRight(b, a1, a2)):
                # print(a1, a2, a, b)
                return False
    return True

class Node:
    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.evaluated = False
        self.children = []
        self.value = 0
        global G
        G[col][row] = self
        
    def propogate(self):
        children = [
            self.grow(self.col, self.row-1),
            self.grow(self.col+1, self.row),
            self.grow(self.col, self.row+1),
            self.grow(self.col-1, self.row)
        ]
        
        return filter(None, children)
        
    def grow(self, col, row):
        global G
        if col < 0 or row < 0 or col >= colNum or row >= rowNum or G[col][row] != None:
            return
        
        # Find points for line this is creating
        a1 = vectorFor(self.col, self.row)
        a2 = vectorFor(col, row)
        
        if isNotObstructed(a1, a2):
            return Node(col, row)
        
    def getChildren(self, endPos):
        
        children = [
            self.evaluate(self.col, self.row-1, endPos),
            self.evaluate(self.col+1, self.row, endPos),
            self.evaluate(self.col, self.row+1, endPos),
            self.evaluate(self.col-1, self.row, endPos)
        ]
        return filter(None, children)
    
    def propogateGChange(self, g):
        if g < self.g:
            self.g = g
            self.value = self.g + self.h
            if self in openSet:
                openSet.remove(self)
                bisect.insort(openSet, self)
            for child in self.children:
                child.propogateGChange(self.g+0.99)
    
    def evaluate(self, col, row, endPos):
        global G
        if col < 0 or row < 0 or col >= colNum or row >= rowNum or G[col][row] is None:
            return
        child = G[col][row]
        if child.evaluated:
            if self.g+1 < child.g:
                G[child.parent[0]][child.parent[1]].children.remove(child)
                child.parent = [self.col, self.row]
                self.children.append(child)
                
                child.propogateGChange(self.g+1)
            
            return
        
        child.parent = [self.col, self.row]
        child.g = self.g + 0.99
        child.h = abs(col-endPos[0]) + abs(row-endPos[1])
        child.value = child.g + child.h
        child.evaluated = True
        self.children.append(child)
        return child
    
    def __lt__(self, other):
        return self.value < other.value
    
    def __eq__(self, other):
        return self.value == other.value
    
    def __hash__(self):
        return hash(hash(self.col) + hash(self.row))

def createGraph():
    global G
    # G = ([None] * height/stepCount)* width/stepCount
    global knightCol
    global knightRow
    global colNum
    global rowNum
    
    fakePos = map['knight_start'][0]
    while fakePos > 0:
        colNum +=1
        fakePos -= stepAmount
    knightCol = colNum
    fakePos = map['knight_start'][0]
    while fakePos < width:
        colNum += 1
        fakePos += stepAmount
        
    fakePos = map['knight_start'][1]
    while fakePos > 0:
        rowNum +=1
        fakePos -= stepAmount
    knightRow = rowNum
    fakePos = map['knight_start'][1]
    while fakePos < height:
        rowNum += 1
        fakePos += stepAmount
        
    # print(colNum, rowNum, knightCol, knightRow)
    
    G = [None] * colNum
    for i in range(colNum):
        G[i] = [None] * rowNum
    
    nextGen = [Node(knightCol, knightRow)]
    
    while len(nextGen) > 0:
        nextGen = reduce(operator.add, [ node.propogate() for node in nextGen ])
        
def clearGraph():
    for col in range(colNum):
        for row in range(rowNum):
            if G[col][row]:
                node = G[col][row]
                node.evaluated = False
                node.g = 0
                node.h = 0
                node.value = 0
                node.children = []
                node.parent = None
    global openSet    
    openSet = []

def posForNode(node):
    x = (node.col - knightCol) * stepAmount + map['knight_start'][0]
    y = (node.row - knightRow) * stepAmount + map['knight_start'][1]
    return PVector(x, y)

def nodeForPos(x, y, closest=True):
    colDif = int(round((x - map['knight_start'][0])/stepAmount))
    rowDif = int(round((y - map['knight_start'][1])/stepAmount))
    
    col = knightCol + colDif
    row = knightRow + rowDif
    
    # I should search in the surrounding area to find the closest valid node...
    node = G[col][row]
    if not node and closest:
        minNode = None
        minDist = width+height
        pos = PVector(x, y)
        for col in range(colNum):
            for row in range(rowNum):
                if G[col][row]:
                    n = posForNode(G[col][row])
                    m = PVector.sub(n, pos).mag()
                    if m < minDist:
                        minDist = m
                        minNode = G[col][row]
                        
        return minNode

    return node

# Starts with existing recipes
craftingRecipes = {
    'Wood': [{
        'npc': 'Tree Spirit',
        'ingredients': [
            'Axe'
        ],
        'killsTree': True
    }],
    'Cheap Sword': [{
        'npc': None,
        'ingredients': [
            'Blade',
            'Wood'
        ]
    }],
    'Poisoned Sword': [{
        'npc': None,
        'ingredients': [
            'Cheap Sword',
            'Wolfsbane'
        ]
    }],
    'Poisoned Fenrir': [{
        'npc': None,
        'ingredients': [
            'Fenrir',
            'Wolfsbane'
        ]
    }],
    "Rameses' head": [
        {
            'npc': 'Rameses',
            'ingredients': [
                'Poisoned Sword'
            ]
        },
        {
            'npc': 'Rameses',
            'ingredients': [
                'Fenrir'
            ]
        },
        {
            'npc': 'Rameses',
            'ingredients': [
                'Poisoned Fenrir'
            ]
        },
        {
            'npc': 'Rameses',
            'ingredients': [
                'Fire'
            ]
        }
    ],
    'Fire': [{
            'npc': None,
            'ingredients': [
                'Ale',
                'Wood'
            ]
    }]
}
NPCs = {
    'King': {
        'loc': 'castle',
        'has': []
    },
    'Rameses': {
        'loc': 'tar_pit',
        'has': []
    },
    'Lady Lupa': {
        'loc': 'cave',
        'has': []
    },
    'Blacksmith': {
        'loc': 'forge',
        'has': []
    },
    'Tree Spirit': {
        'loc': 'tree',
        'has': []
    },
    'Innkeeper': {
        'loc': 'tavern',
        'has': []
    }
}

class ActionNode:
    
    def __init__(self, npc, message, goals):
        self.npc = npc
        self.message = message
        self.goals = goals
        self.treeAlive = False


def questFor(goal):
    gen = [ActionNode('Rameses', '', [goal])]
    generationCount = 0
    while len(gen) > 0:
        generationCount += 1
        newGen = []
        for action in gen:
            stagnantPath = True
            for item in action.goals:
                if item in craftingRecipes:
                    stagnantPath = False
                    for recipe in craftingRecipes[item]:
                        
                        if 'killsTree' in recipe and action.treeAlive:
                            continue
                        
                        newGoals = action.goals[:]
                        newGoals.remove(item)
                        
                        for ingredient in recipe['ingredients']:
                            newGoals.append(ingredient)
                        
                        if len(recipe['ingredients']) is 2:
                            message = ' and '.join(recipe['ingredients']) + ' were '
                        elif len(recipe['ingredients']) > 2:
                            message = ', '.join(recipe['ingredients'][:-1]) + ', and ' + recipe['ingredients'][len(recipe['ingredients'])-1] + ' were '
                        else:
                            message = recipe['ingredients'][0] + ' was '
                            
                        message += 'used to obtain ' + item
                        
                        if recipe['npc'] and recipe['npc'] != 'Rameses':
                            message += ' through ' + recipe['npc']
                            
                        n = ActionNode(recipe['npc'], message, newGoals)
                        n.parent = action
                        n.treeAlive = n.parent.treeAlive
                        # if recipe['npc'] == 'Tree Spirit':
                        #     n.treeAlive = True
                        
                        if 'killsTree' in recipe and recipe['killsTree']:
                            n.treeAlive = False
                        
                        justGold = True
                        for goal in newGoals:
                            if goal != '1gold':
                                justGold = False
                        if justGold and len(newGoals) <= map['greet_king'] and 'King' in NPCs:
                            return n
                        
                        newGen.append(n)
            if stagnantPath:
                newGen = gen[:]
                newGen.remove(action)
                break
        gen = newGen

def setup():
    size(640, 480)
    # frameRate(1)
    global map
    with open('map.json') as f:
        map = json.load(f)
    
    global knight
    knight = loadImage("knight.png")
    knight.resize(spriteSize, spriteSize)
    global castle
    castle = loadImage("castle.png")
    castle.resize(spriteSize, spriteSize)
    global tar_pit
    tar_pit = loadImage("tar_pit.png")
    tar_pit.resize(spriteSize, spriteSize)
    global tavern
    tavern = loadImage("tavern.png")
    tavern.resize(spriteSize, spriteSize)
    global tree
    tree = loadImage("tree.png")
    tree.resize(spriteSize, spriteSize)
    global cave
    cave = loadImage("cave.png")
    cave.resize(spriteSize, spriteSize)
    global forge
    forge = loadImage("forge.png")
    forge.resize(spriteSize, spriteSize)
    global star
    star = loadImage("star.png")
    star.resize(spriteSize, spriteSize)
    
    global knightPos
    knight_start = map['knight_start']
    knightPos = PVector(knight_start[0], knight_start[1])
    
    createGraph()
    if 'state_of_world' in map:
        for has in map['state_of_world']['Has']:
            has[0] = str(has[0]) # This is annoying
            has[1] = str(has[1])
            craftingRecipes[has[1]] = []
            if has[0] in NPCs:
                NPCs[has[0]]['has'].append(has[1])
            else:
                NPCs[has[0]]['has'] = [has[1]]
            
    for npc in NPCs:
        loc = NPCs[npc]['loc']
        if loc in map['key_locations']:
            coords = map['key_locations'][loc]
            if not nodeForPos(coords[0], coords[1], closest=False):
                del NPCs[npc]
        
    if 'state_of_world' in map:
        for want in map['state_of_world']['Wants']:
            want[0] = str(want[0])
            want[1] = str(want[1])
            if want[0] in NPCs:
                for has in NPCs[want[0]]['has']:
                    if want[1] != has:
                        craftingRecipes[has].append(
                        {
                        'ingredients': [want[1]],
                        'npc': want[0]
                        })
            
        
    # print(NPCs)
    # print(craftingRecipes)
    
    rc = questFor("Rameses' head")
    if not rc:
        otherItemsToTry = ['Cheap Sword', 'Axe', 'Blade', 'Wolfsbane', 'Ale', 'Wood']
        tryIndex = -1
        while not rc and tryIndex < len(otherItemsToTry) - 1:
            tryIndex += 1
            rc = questFor(otherItemsToTry[tryIndex])
        if rc:
            finalNode = ActionNode('Rameses', 'The knight tried to kill Rameses with ' + otherItemsToTry[tryIndex] + ' and died trying', [otherItemsToTry[tryIndex]])
            # Add action to try to use the item on Ram
            parent = rc
            while parent.parent:
                parent = parent.parent
            parent.parent = finalNode
        else:
            if 'Rameses' not in NPCs:
                rc = ActionNode(None, "The knight can't reach Rameses and wallows in despair", [])
            else:
                rc = ActionNode('Rameses', 'The knight tried to fight Rameses with his fists and died trying', [])
                
    if 'King' in NPCs:
        greetKingNode = ActionNode('King', 'The knight greets the king and obtains ' + str(map['greet_king']) + ' gold', [])
        greetKingNode.parent = rc
        rc = greetKingNode
            
    global playerQuest
    playerQuest = rc
        
    # while parent is not None:
    #     print(n.message)
    #     parent = n.parent
    

def findShortestPath():
    lowest = openSet.pop(0)
    if lowest is endP:
        return endP
    
    for child in lowest.getChildren([endP.col, endP.row]):
        bisect.insort(openSet, child)
        
        
def navigateTo(x, y):
    global endP
    startNode = nodeForPos(knightPos.x, knightPos.y)
    startNode.g = 0
    openSet.append(startNode)
    startNode.evaluated = True
    endP = nodeForPos(x, y)
    rc = None
    while len(openSet) != 0 and not rc:
        rc = findShortestPath()
    path = []
    parent = rc
    while parent != startNode:
        path.insert(0, posForNode(parent))
        parent = G[parent.parent[0]][parent.parent[1]]
    global playerPath
    playerPath = path
    clearGraph()
    
def mousePressed():
    navigateTo(mouseX, mouseY)
    
def followQuest():
    global playerQuest
    if playerQuest:
        # If we're already at that location, say the message and move to the next quest
        # That means I need a way to find the nodes of certain npcs.
        
        npc = playerQuest.npc
        if npc:
            loc = NPCs[playerQuest.npc]['loc']
            coords = map['key_locations'][loc]
        else:
            coords = [knightPos.x, knightPos.y]
        if nodeForPos(coords[0], coords[1]) is nodeForPos(knightPos.x, knightPos.y):
            print(playerQuest.message)
            if hasattr(playerQuest, 'parent'):
                playerQuest = playerQuest.parent
                return
            else:
                playerQuest = None
                return
        
        navigateTo(coords[0], coords[1])
    
def followPath(vel):
    if len(playerPath) > 0:
        target = playerPath[0]
        offset = PVector.sub(target, knightPos)
        distance = offset.mag()
        if distance < vel:
            playerPos = target
            playerPath.pop(0)
            followPath(vel-distance)
        else:
            knightPos.add(offset.normalize().mult(vel))
    else:
        followQuest()


def draw():
    background(255)
    
    followPath(playerVel)
    
    for name, path in map['obstacles'].items():
        if 'lake' in name:
            fill(51,119,255)
        elif 'forest' in name:
            fill(21,128,0)
        elif 'mountain' in name:
            fill(128,85,0)
        else: 
            fill(50, 50, 50)
        beginShape()
        for p in path:
            vertex(p[0], p[1])
        endShape(CLOSE)
        
    for name, loc in map['key_locations'].items():
        if name == 'castle':
            img = castle
        elif name == 'tar_pit':
            img = tar_pit
        elif name == 'tavern':
            img = tavern
        elif name == 'tree':
            img = tree
        elif name == 'cave':
            img = cave
        elif name == 'forge':
            img = forge
        else:
            img = star
            
        image(img,loc[0] - spriteOffset,loc[1] - spriteOffset)
    
        
    image(knight,knightPos.x - spriteOffset,knightPos.y - spriteOffset)
    # for col in range(len(G)):
    #     for row in range(len(G[col])):
    #         if G[col][row] != None:
    #             x = (col - knightCol) * stepAmount + map['knight_start'][0]
    #             y = (row - knightRow) * stepAmount + map['knight_start'][1]
    #             if G[col][row].evaluated:
    #                 fill(255)
    #             else:
    #                 fill(100)
    #             circle(x, y, 2)