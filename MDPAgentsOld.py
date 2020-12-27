# sampleAgents.py
# parsons/07-oct-2017
#
# Version 1.1
#
# Some simple agents to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agents here are extensions written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class Grid:
         
    # constructor
    #
    # note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # grid elements are not restricted, so you can place whatever you
    # like at each location. you just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # print the grid out.
    def display(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # a new line after each line of the grid
            print 
        # a line after the grid
        print

    # the display function prints the grid out upside down. this
    # prints the grid out so that it matches the view we see when we
    # look at pacman.
    def prettyDisplay(self, state):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                ghosts = api.ghosts(state)
                pacman = api.whereAmI(state)
                if (j, self.height - (i+1)) in ghosts:
                    print('G'),
                elif (j, self.height - (i+1)) == pacman:
                    print('P'),
                else:
                    print self.grid[self.height - (i + 1)][j],
            # a new line after each line of the grid
            print 
        # a line after the grid
        print

    def prettyDisplayPolicy(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                val = self.grid[self.height - (i + 1)][j]
                if val == Directions.NORTH:
                    print('N'),
                elif val == Directions.EAST:
                    print('E'),
                elif val == Directions.SOUTH:
                    print('S'),
                elif val == Directions.WEST:
                    print('W'),
                else:
                    print val,
            # a new line after each line of the grid
            print 
        # a line after the grid
        print

    def prettyDisplayValues(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                val = self.grid[self.height - (i + 1)][j]
                if val == "%":
                    print "%        ",;
                elif val == "*":
                    print "*        ",;
                else:
                    value = str(round(val, 1))
                    spaces = 9 - len(value)
                    print value + (" " * spaces),
            # a new line after each line of the grid
            print 
        # a line after the grid
        print
        
    # set and get the values of specific elements in the grid.
    # here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

class MDPAgent(Agent):
    def __init__(self):
        #print "Running init!"
        pass

    def registerInitialState(self, state):
         #print "Running registerInitialState!"
         # Make a map of the right size
         self.makeMap(state)
         self.addWallsToMap(state)
         self.updateFoodInMap(state)
         self.map.display()
         self.deadends = self.getDeadends()
         self.visited = [api.whereAmI(state)]
         self.epsilon = 0.01

         if (self.getLayoutWidth(api.corners(state)) == 20):
             self.discount = 0.45
             self.depth = 5
             self.deadend_value = -20
             self.last_food_value = 50
             self.food_value = 3
             self.iterations = 10
             self.ghost_value = -19
         else:
             self.discount = 0.45
             self.depth = 5
             self.iterations = 10
             self.deadend_value = -30
             self.last_food_value = 40
             self.food_value = 3
             self.ghost_value = -19

    def final(self, state):
        #print "Looks like I just died!"
        pass

    def test(self, discount, depth, last_food_value, deadend_value, food_value, ghost_value):
        self.discount = discount
        self.depth = depth
        self.last_food_value = last_food_value
        self.deadend_value = deadend_value
        self.food_value = food_value
        self.ghost_value = ghost_value

    def makeMap(self,state):
        corners = api.corners(state)
        self.height = self.getLayoutHeight(corners)
        self.width  = self.getLayoutWidth(corners)
        self.map = Grid(self.width, self.height)
        self.policyMap = Grid(self.width, self.height)
        self.utilityMap = Grid(self.width, self.height)

    def getDeadends(self):
        deadends = []
        for x in range(1, self.width-1):
            for y in range(1, self.height-1):
                if (self.map.getValue(x, y) != "%") and (len(self.getPossibleMoves(x, y)) == 1):
                    deadends.append((x, y))

        return deadends

    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Functions to manipulate the map.
    #
    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')
            self.policyMap.setValue(walls[i][0], walls[i][1], '%')
            self.utilityMap.setValue(walls[i][0], walls[i][1], '%')

    # Create a map with a current picture of the food that exists.
    def updateFoodInMap(self, state):
        # First, make all grid elements that aren't walls blank.
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    self.map.setValue(i, j, ' ')
        food = api.food(state)
        for i in range(len(food)):
            self.map.setValue(food[i][0], food[i][1], '*')

    def calculateExpectedValues(self, x, y, valueMap):
        """Calculates the expected values for each possible move for a valid location in the world

        Parameters
        ----------
        x : int
            the x-coordinate of the initial location
        y : int
            the y-coordinate of the initial location
        valueMap : grid
            the utility values for valid locations in the map

        Returns
        ---------
        dict
            a dict with Directions as key and the expected values as values.
        """

        utility_dict = {}
        directProb = api.directionProb
        for deltaX, deltaY, direction in [(0,1, Directions.NORTH), (1, 0, Directions.EAST), (-1, 0, Directions.WEST), (0, -1, Directions.SOUTH)]:
            expectedValue = 0
            if self.map.getValue(x+deltaX, y+deltaY) != '%':
                expectedValue = directProb * valueMap.getValue(x+deltaX, y+deltaY)
                if self.map.getValue(x+deltaY, y+deltaX) != '%':
                    expectedValue += (0.5) * (1 - directProb) * valueMap.getValue(x+deltaY, y+deltaX)
                else:
                    expectedValue += (0.5) * (1 - directProb) * valueMap.getValue(x, y)
                if self.map.getValue(x-deltaY, y-deltaX) != '%':
                    expectedValue += (0.5) * (1 - directProb) * valueMap.getValue(x-deltaY, y-deltaX)
                else:
                    expectedValue += (0.5) * (1 - directProb) * valueMap.getValue(x, y)
                utility_dict[direction] = expectedValue
        return utility_dict

    def ghostAvoidance(self, state):
        ghosts = api.ghostStates(state)
        positions = {}
        for ghost in ghosts:
            ghost_pos = ghost[0]
            active_queue = util.Queue()
            inactive_queue = util.Queue()
            active_queue.push(ghost_pos)
            counter = 0
            while counter < self.depth:
                while active_queue.isEmpty() is False:
                    pos = active_queue.pop()
                    positions[pos[0], pos[1]] = (self.ghost_value / self.depth) * (self.depth - counter)
                    next_locs = self.getPossibleLocations(int(pos[0]), int(pos[1]))
                    for loc in next_locs:
                        if loc not in positions.keys():
                            inactive_queue.push(loc)
                inactive_queue, active_queue = active_queue, inactive_queue
                counter += 1
        return positions

    def rewardFunction(self, state):
        walls = api.walls(state)
        rewards = dict()
        ghostAvoidancePositions = self.ghostAvoidance(state)
        num_food = len(api.food(state))
        for x in range(1, self.width-1):
            for y in range(1, self.height-1):
                if (x, y) not in walls:
                    reward = 0

                    if (x, y) in ghostAvoidancePositions.keys():
                        reward = ghostAvoidancePositions[(x,y)]

                    if self.map.getValue(x, y) == "*":
                        if num_food is 1:
                            #reward += 50
                            reward += self.last_food_value
                        elif (x, y) in self.deadends:
                            #reward += -20
                            reward += self.deadend_value
                        else:
                            reward += 3
                            #reward += self.food_value
                    else:
                        reward += -1
                    rewards[(x, y)] = reward

        return rewards

    def approxPolicyEvaluation(self, state, iterations, rewards, originalValueMap):
        """Repeats the bellman's equation a set number of times to calculate utilities for each valid location

        Parameters
        ----------
        state : state
            Backend object containing the current details of the world
        iterations : int
            Number of times to repeat the Bellman's algorithm to calculate utilities
        rewards: grid
            Holds the reward values for every state
        """

        for i in range(iterations):
            walls = api.walls(state)
            for x in range(1, self.width-1):
                for y in range(1, self.height-1):
                    if (x, y) not in walls:
                        EVSumDict = self.calculateExpectedValues(x, y, originalValueMap)
                        EVSum = EVSumDict[self.policyMap.getValue(x, y)]
                        #EVSum = self.calculateUtilitySum(x, y, originalValueMap)

                        reward = rewards[(x, y)]
                        newUtility = reward + self.discount * EVSum
                        self.utilityMap.setValue(x, y, newUtility)
            import copy
            originalValueMap = copy.deepcopy(self.utilityMap)

    def policyImprovement(self, state, rewards, originalValueMap):
        """Caculate a new policy for each valid location 
        """
        walls = api.walls(state)
        unchanged = True
        for x in range(1, self.width-1):
            for y in range(1, self.height-1):
                if (x, y) not in walls:
                    moves = self.getPossibleMoves(x, y)
                    newExpectedValuesDict = self.calculateExpectedValues(x, y, self.utilityMap)
                    values = list(newExpectedValuesDict.values())
                    new_direction = list(newExpectedValuesDict.keys())[values.index(max(values))]
                    original_direction = self.policyMap.getValue(x, y)

                    best_value = newExpectedValuesDict[new_direction]
                    original_value = newExpectedValuesDict[original_direction]
                    if abs(best_value - original_value) > self.epsilon:
                        self.policyMap.setValue(x, y, new_direction)
                        unchanged = False

        return unchanged

    def policyEvaluation(self, state):
        ghostAvoidancePositions = self.ghostAvoidance(state)
        #print(ghostAvoidancePositions)
        rewards = self.rewardFunction(state)
        import copy
        originalValueMap = copy.deepcopy(self.utilityMap)

        while True:
            self.approxPolicyEvaluation(state, self.iterations, rewards, originalValueMap)
            unchanged = self.policyImprovement(state, rewards, originalValueMap)
            if unchanged is True:
                break


    def getPossibleMoves(self, x, y):
        """ A helpher method that returns possible moves from a valid location in the world

        Parameters
        ----------
        x : int
            The x-coordinate of the initial location
        y : int
            The y-coordinate of the initial location

        Returns
        ----------
        list
            a list of Directions correspending that are the possible moves
        """

        availableMoves = []
        if self.map.getValue(x, y+1) != '%':
            availableMoves.append(Directions.NORTH);
        if self.map.getValue(x+1, y) != '%':
            availableMoves.append(Directions.EAST)
        if self.map.getValue(x, y-1) != '%':
            availableMoves.append(Directions.SOUTH)
        if self.map.getValue(x-1, y) != '%':
            availableMoves.append(Directions.WEST)
        return availableMoves

    def getPossibleLocations(self, x, y):
        """ A helper method that returns the possible locations we can reach on the next move from a valid location

        Parameters
        ----------
        x : int
            The x-coordinate of the initial location
        y : int
            The y-coordinate of the initial location

        Returns
        ----------
        list
            a list of tuples that contain the coordinates of the possible locations
        """

        moves = self.getPossibleMoves(x, y)
        locations = [] 
        if Directions.NORTH in moves:
           locations.append((x, y+1))
        if Directions.EAST in moves:
           locations.append((x+1, y))
        if Directions.SOUTH in moves:
           locations.append((x, y-1))
        if Directions.WEST in moves:
           locations.append((x-1, y))
        return locations

    def getAction(self, state):
        self.updateFoodInMap(state)
        #self.map.prettyDisplay()

        corners = api.corners(state)
        walls = api.walls(state)
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)

        for x in range(1, width-1):
            for y in range(1, height-1):
                if (x, y) not in walls:
                    if self.map.getValue(x, y) == '*':
                        self.utilityMap.setValue(x, y, 0)
                    elif (x, y) in walls:
                        self.utilityMap.setValue(x, y, '%')
                    else:
                        self.utilityMap.setValue(x, y, 0)
                    availableMoves = self.getPossibleMoves(x, y)
                    self.policyMap.setValue(x, y, availableMoves[0])
                    #self.policyMap.setValue(x, y, random.choice(availableMoves))

        self.policyEvaluation(state)
        (x, y) = api.whereAmI(state)
        legal = api.legalActions(state)
        self.map.prettyDisplay(state)
        self.utilityMap.prettyDisplayValues()
        print(self.policyMap.getValue(x, y))
        print('--------------------------------------------------------------------------------------------------------------')
        return api.makeMove(self.policyMap.getValue(x, y), legal)

class SimpleMDPVIAgent(Agent):
    # The constructor. We don't use this to create the map because it
    # doesn't have access to state information.
    def __init__(self):
        print "Running init!"

    # This function is run when the agent is created, and it has access
    # to state information, so we use it to build a map for the agent.
    def registerInitialState(self, state):
         print "Running registerInitialState!"
         # Make a map of the right size
         self.makeMap(state)
         self.addWallsToMap(state)
         self.updateFoodInMap(state)
         self.map.display()
         self.deadends = self.getDeadends()

    # This is what gets run when the game ends.
    def final(self, state):
        print "Looks like I just died!"

    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        self.height = self.getLayoutHeight(corners)
        self.width  = self.getLayoutWidth(corners)
        self.map = Grid(self.width, self.height)
        if (self.getLayoutWidth(api.corners(state)) == 20):
            self.discount = 0.45
            self.depth = 9
            self.iterations = 10
        else:
            self.discount = 0.30
            self.depth = 6
            self.iterations = 10

    def final(self, state):
        #print "Looks like I just died!"
        pass

    def test(self, discount, depth, last_food_value, deadend_value, food_value):
        self.discount = discount
        self.depth = depth
        self.last_food_value = last_food_value
        self.deadend_value = deadend_value
        self.food_value = food_value
        print(self.discount, self.depth)

    def getDeadends(self):
        deadends = []
        for x in range(1, self.width-1):
            for y in range(1, self.height-1):
                if (self.map.getValue(x, y) != "%") and (len(self.getPossibleMoves(x, y)) == 1):
                    deadends.append((x, y))

        return deadends
        
    # Functions to get the height and the width of the grid.
    #
    # We add one to the value returned by corners to switch from the
    # index (returned by corners) to the size of the grid (that damn
    # "start counting at zero" thing again).
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Functions to manipulate the map.
    #
    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')

    # Create a map with a current picture of the food that exists.
    def updateFoodInMap(self, state):
        # First, make all grid elements that aren't walls blank.
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    self.map.setValue(i, j, ' ')
        food = api.food(state)
        for i in range(len(food)):
            self.map.setValue(food[i][0], food[i][1], '*')

    def getSpaceValue(self, x, y):
        space = self.map.getValue(x, y)
        if space == " ":
            return 0
        elif space == "*":
            return 10

    def calculateMaxUtility(self, x, y, originalValueMap):
        maxUtility = None
        best_dir = None
        directProb = api.directionProb
        for deltaX, deltaY, direction in [(1,0, 'north'), (0, 1, 'east'), (-1, 0, 'west'), (0, -1, 'south')]:
            expectedValue = 0
            if self.map.getValue(x+deltaX, y+deltaY) != '%':
                expectedValue = directProb * originalValueMap.getValue(x+deltaX, y+deltaY)
                if self.map.getValue(x+deltaY, y+deltaX) != '%':
                    expectedValue += (0.5) * (1 - directProb) * originalValueMap.getValue(x+deltaY, y+deltaX)
                else:
                    expectedValue += (0.5) * (1 - directProb) * originalValueMap.getValue(x, y)
                if self.map.getValue(x-deltaY, y-deltaX) != '%':
                    expectedValue += (0.5) * (1 - directProb) * originalValueMap.getValue(x-deltaY, y-deltaX)
                else:
                    expectedValue += (0.5) * (1 - directProb) * originalValueMap.getValue(x, y)
                if maxUtility is None or expectedValue > maxUtility:
                    maxUtility = expectedValue
                    best_dir = direction
        return maxUtility

    def ghostAvoidance(self, state):
        ghosts = api.ghostStates(state)
        positions = {}
        for ghost in ghosts:
            ghost_pos = ghost[0]
            active_queue = util.Queue()
            inactive_queue = util.Queue()
            active_queue.push(ghost_pos)
            counter = 0
            while counter < self.depth:
                while active_queue.isEmpty() is False:
                    pos = active_queue.pop()
                    if (pos[0], pos[1]) not in positions.keys():
                        positions[pos[0], pos[1]] = -40 + 2 * (counter)
                    next_locs = self.getPossibleLocations(int(pos[0]), int(pos[1]))
                    for loc in next_locs:
                        if loc not in positions.keys():
                            inactive_queue.push(loc)
                inactive_queue, active_queue = active_queue, inactive_queue
                counter += 1

        print(positions)
        return positions

    def rewardFunction(self, state):
        walls = api.walls(state)
        rewards = dict()
        ghostAvoidancePositions = self.ghostAvoidance(state)
        num_food = len(api.food(state))
        for x in range(1, self.width-1):
            for y in range(1, self.height-1):
                if (x, y) not in walls:
                    reward = 0

                    if (x, y) in ghostAvoidancePositions.keys():
                        reward = ghostAvoidancePositions[(x,y)]

                    if self.map.getValue(x, y) == "*":
                        if num_food is 1:
                            reward += 30
                            #reward += self.last_food_value
                        elif (x, y) in self.deadends:
                            reward += -20
                            #reward += self.deadend_value
                        else:
                            reward += 1
                            #reward += self.food_value
                    else:
                        reward += -1
                    rewards[(x, y)] = reward

        return rewards
    
    def valueMap(self, state, discount):
        corners = api.corners(state)
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        # ALTNERATIVE - JUST SET A DEFAULT VALUE?
        valueMap = Grid(width, height)
        food = api.food(state)
        walls = api.walls(state)
        for x in range(0, width):
            for y in range(0, height):
                if (x, y) in food:
                    valueMap.setValue(x, y, 0)
                elif (x, y) in walls:
                    valueMap.setValue(x, y, "%");
                else:
                    valueMap.setValue(x, y, 0)

        walls = api.walls(state)
        directProb = api.directionProb;
        changed = True
        rewards = self.rewardFunction(state)
        count = 0
        while changed:
            count = count +1
            import copy
            originalValueMap = copy.deepcopy(valueMap)
            changed = False
            for x in range(1, width-1):
                for y in range(1, height-1):
                    if (x, y) in walls:
                        continue
                    maxUtility = self.calculateMaxUtility(x, y, originalValueMap)

                    newUtility = rewards[(x, y)] + self.discount * maxUtility

                    
                    if abs(newUtility - originalValueMap.getValue(x, y)) > 0.001:
                        changed = True

                    valueMap.setValue(x, y, newUtility)
        print('num iterations', count)

        return valueMap

    def getPossibleMoves(self, x, y):
        availableMoves = []
        if self.map.getValue(x, y+1) != '%':
            availableMoves.append(Directions.NORTH);
        if self.map.getValue(x+1, y) != '%':
            availableMoves.append(Directions.EAST)
        if self.map.getValue(x, y-1) != '%':
            availableMoves.append(Directions.SOUTH)
        if self.map.getValue(x-1, y) != '%':
            availableMoves.append(Directions.WEST)
        return availableMoves

    def getPossibleLocations(self, x, y):
       moves = self.getPossibleMoves(x, y)
       locations = [] 
       if Directions.NORTH in moves:
           locations.append((x, y+1))
       if Directions.EAST in moves:
           locations.append((x+1, y))
       if Directions.SOUTH in moves:
           locations.append((x, y-1))
       if Directions.WEST in moves:
           locations.append((x-1, y))
       return locations


    def getAction(self, state):
        self.updateFoodInMap(state)
        valueMap = self.valueMap(state, 0.6)
        legal = api.legalActions(state) 
        (x, y) = api.whereAmI(state)

        util_dict = {}

        if Directions.NORTH in legal: 
            n_util = 0.8 * valueMap.getValue(x, y+1)
            if Directions.EAST in legal:
                n_util += 0.1 * valueMap.getValue(x+1, y)
            else:
                n_util += 0.1 * valueMap.getValue(x, y)
            if Directions.WEST in legal:
                n_util += 0.1 * valueMap.getValue(x-1, y)
            else:
                n_util += 0.1 * valueMap.getValue(x, y)
            util_dict["n_util"] = n_util


        if Directions.EAST in legal: 
            e_util = 0.8 * valueMap.getValue(x+1, y)
            if Directions.NORTH in legal:
                e_util += 0.1 * valueMap.getValue(x, y+1)
            else:
                e_util += 0.1 * valueMap.getValue(x, y)
            if Directions.SOUTH in legal:
                e_util += 0.1 * valueMap.getValue(x, y-1)
            else:
                e_util += 0.1 * valueMap.getValue(x, y)
            util_dict["e_util"] = e_util

        if Directions.SOUTH in legal: 
            s_util = 0.8 * valueMap.getValue(x, y-1)
            if Directions.EAST in legal:
                s_util += 0.1 * valueMap.getValue(x+1, y)
            else:
                s_util += 0.1 * valueMap.getValue(x, y)
            if Directions.WEST in legal:
                s_util += 0.1 * valueMap.getValue(x-1, y)
            else:
                s_util += 0.1 * valueMap.getValue(x, y)
            util_dict["s_util"] = s_util

        if Directions.WEST in legal: 
            w_util = 0.8 * valueMap.getValue(x-1, y)
            if Directions.NORTH in legal:
                w_util += 0.1 * valueMap.getValue(x, y+1)
            else:
                w_util += 0.1 * valueMap.getValue(x, y)
            if Directions.SOUTH in legal:
                w_util += 0.1 * valueMap.getValue(x, y-1)
            else:
                w_util += 0.1 * valueMap.getValue(x, y)
            util_dict["w_util"] = w_util

        import operator
        move = max(util_dict.iteritems(), key=operator.itemgetter(1))[0]
        self.map.prettyDisplay(state)
        valueMap.prettyDisplayValues()
        print(move)
        print("------------------------")
        if move is "n_util":
            return api.makeMove(Directions.NORTH, legal)
        if move is "e_util":
            return api.makeMove(Directions.EAST, legal)
        if move is "s_util":
            return api.makeMove(Directions.SOUTH, legal)
        if move is "w_util":
            return api.makeMove(Directions.WEST, legal)
