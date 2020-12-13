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
import game
import random
import util

DIRECTION_VECTORS = {Directions.NORTH: (0,1), Directions.SOUTH: (0, -1), Directions.EAST: (1, 0), Directions.WEST: (-1, 0)}
EPSILON = 0.01
GHOST_VALUE = -10.0
DEADEND_VALUE = -50.0
FOOD_VALUE = 3.0
EMPTY_VALUE = 0.0
DISCOUNT = 0.6
GHOST_RANGE = 12
ITERATIONS = 10

class MDPAgent(Agent):

    def test(self, ghost_value=50, ghost_range=12):
        """
        Method for modifying of global variables for testing purposes
        """
        global GHOST_VALUE
        global GHOST_RANGE
        GHOST_VALUE = ghost_value
        GHOST_RANGE = ghost_range

    def __init__(self):
        """
        Constructor to initialise variables
        """
        self.rewards = {}
        self.utilities = {}
        self.stateNeighbours = {}

    def registerInitialState(self, state):
        """
        Builds the agent's internal view of the world using the current game state

        @param state: The current pacman game state.
        """

        # Set constant world values
        self.corners = api.corners(state)
        self.walls = api.walls(state)

        # Calculate the width and height using the corners
        from operator import itemgetter
        self.height = max(self.corners, key=itemgetter(1))[1] + 1
        self.width= max(self.corners, key=itemgetter(0))[0] + 1

        # Holds the set of all reachable locations
        self.valid_locations = set((x, y) for x in range(self.width) for y in range(self.height) if (x, y) not in self.walls)

    def buildMap(self, state):
        """ 
        Builds a map of the current game world via calls to the api

        @param state: The current game state.
        """
        
        # Build the grid to hold the map, iterate starting with the maximum height to make bottom left the origin.
        self.grid = [[" " for y in range(self.height)] for x in range(self.width)]
        
        # Populate the map
        for food in self.food:
            self.grid[food[0]][food[1]] = '*'

        for wall in self.walls:
            self.grid[wall[0]][wall[1]] = '%'

        for ghost in self.ghosts:
            self.grid[int(ghost[0])][int(ghost[1])] = 'G'

        for capsule in self.capsules:
            self.grid[capsule[0]][capsule[1]] = 'C'

        self.grid[self.pacman[0]][self.pacman[1]] = 'P'

    def setRewards(self):
        """
        Populates the reward dictionary with the reward value each state
        """

        self.rewards = {pos : EMPTY_VALUE for pos in self.valid_locations}
        self.rewards.update({pos : FOOD_VALUE for pos in self.food})
        self.rewards.update(self.ghostRewardValues())

    def ghostRewardValues(self):
        """
        Uses a depth-limited breadth-first search to calculate decaying ghost reward values

        @returns dict: The reward values for positions
        """
        positions = {}

        for ghost in self.ghosts:
            active_queue = util.Queue()
            inactive_queue = util.Queue()
            active_queue.push(ghost)
            counter = 1
            while counter < GHOST_RANGE:
                while active_queue.isEmpty() is False:
                    pos = active_queue.pop()
                    next_locs = self.getLegalMoves(pos)[1]

                    
                    positions[pos] = self.rewards[pos] + GHOST_VALUE * (1.0 / counter)
                    #if (len(next_locs) == 1) and (len(self.food) > 1) and (util.manhattanDistance(self.pacman, pos) > 1):
                        #print("deadend", util.manhattanDistance(self.pacman, pos))
                        #positions[pos] = self.rewards[pos] + (GHOST_VALUE + DEADEND_VALUE) * (1.0 / counter)
                    #else:
                        #positions[pos] = self.rewards[pos] + GHOST_VALUE * (1.0 / counter)

                    for loc in next_locs:
                        if loc not in positions.keys():
                            inactive_queue.push(loc)
                # Swap the queues
                inactive_queue, active_queue = active_queue, inactive_queue
                counter += 1
        return positions

    def setNeighbours(self):
        """
        Populates the state neighbours dictionary with the possible neighbours for each state.
        """
        for location in self.valid_locations:
            moves = {}
            for direction in DIRECTION_VECTORS:
                (x, y) = DIRECTION_VECTORS[direction]
                move = (location[0] + x, location[1] + y)
                # If we hit a wall, bounce back
                if move in self.walls:
                    move = location
                moves[direction] = move

            moves_dict = {
                    Directions.NORTH: [moves[Directions.NORTH], moves[Directions.EAST], moves[Directions.WEST]],
                    Directions.SOUTH: [moves[Directions.SOUTH], moves[Directions.EAST], moves[Directions.WEST]],
                    Directions.EAST: [moves[Directions.EAST], moves[Directions.NORTH], moves[Directions.SOUTH]],
                    Directions.WEST: [moves[Directions.WEST], moves[Directions.NORTH], moves[Directions.SOUTH]]
                }

            self.stateNeighbours[location] = moves_dict
    
    def getLegalMoves(self, location):
        legal_moves = []
        locations = []
        for direction in DIRECTION_VECTORS:
            (x, y) = DIRECTION_VECTORS[direction]
            new_location = (location[0] + x, location[1] + y)
            if new_location in self.valid_locations:
                legal_moves.append(direction)
                locations.append(new_location)
        return (legal_moves, locations)

    def modifiedPolicyIteration(self):
        """
        Repeats the bellman's equation a set number of times to calculate utilities for each valid location
        """

        # Set initial utilities to zero
        self.utilities = {location: 0 for location in self.valid_locations}

        # Start with random policy
        self.policies = {location: random.choice(self.getLegalMoves(location)[0]) for location in self.valid_locations}
        import copy
        new_utilities = copy.deepcopy(self.utilities)
        changed = True
        while changed:
            changed = False 

          # Perform approx bellmans
            for i in range(ITERATIONS):
                for location in self.valid_locations:
                    neighbours = self.stateNeighbours[location]
                    policy = self.policies[location]
                    if (policy is Directions.STOP):
                        expectedValue = self.utilities[location]
                    else:
                        move = neighbours[policy]
                        expectedValue = 0.8 * self.utilities[move[0]] + 0.1 * self.utilities[move[1]] + 0.1 * self.utilities[move[2]]
                    new_utilities[location] = self.rewards[location] + DISCOUNT * expectedValue
                self.utilities = new_utilities
            
            # Check for improved policy decisions
            for location in self.valid_locations:
                moves = self.getLegalMoves(location)[0]
                neighbours = self.stateNeighbours[location]
                expectedValues = {
                        move: 0.8 * new_utilities[neighbours[move][0]] + 0.1 * new_utilities[neighbours[move][1]] + 0.1 * new_utilities[neighbours[move][2]] for move in moves
                        }
                expectedValues[Directions.STOP] = new_utilities[location]
                values = list(expectedValues.values())
                max_value = max(values)
                new_policy = list(expectedValues.keys())[values.index(max_value)]

                original_policy = self.policies[location]
                original_value = expectedValues[original_policy]

                if abs(max_value - original_value) > EPSILON:
                    changed = True
                    self.policies[location] = new_policy

    def display(self, info=None):       
        """
        Neatly prints the current map.
        @param info: Which internal data to display within the map, default is world objects (pacman, food etc.).
        """
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width):
                if info == 'utilities':
                    if (x, y) in self.utilities.keys():
                        print(self.utilities[(x, y)]),
                    else:
                        print(self.grid[x][y]) + "   ",
                elif info == 'rewards':
                    if (x, y) in self.rewards.keys():
                        print(self.rewards[(x, y)]),
                    else:
                        print(self.grid[x][y]) + "   ",
                else:
                    print(self.grid[x][y]),
            print
        print

    def getAction(self, state):
        # Set constants about environment
        self.ghosts = api.ghosts(state)
        self.capsules = api.capsules(state)
        self.pacman = api.whereAmI(state)
        self.food = api.food(state)

        # Build internal data
        self.buildMap(state)
        self.setRewards()
        self.setNeighbours()

        self.modifiedPolicyIteration()

        # self.display()
        # self.display(info='utilities')
        # self.display(info='rewards')
        # print(self.policies[self.pacman])
        # print(GHOST_VALUE)
        # print(GHOST_RANGE)
        legal = api.legalActions(state)

        return api.makeMove(self.policies[self.pacman], legal)
