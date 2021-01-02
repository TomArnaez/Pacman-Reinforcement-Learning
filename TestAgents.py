# coding=utf-8
# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
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

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

# version 2 by CHAOYU DENG based on code in
# pacmanAgents.py, mdpAgent.py and mapAgent.py

from game import Agent
from game import Actions
import api



# @this class is a copy from mapAgent.py and add some useful function like copy(), __eq__, isValid and minimumValueOnMap
# A class that creates a grid that can be used as a map
#
# The map itself is implemented as a nested list, and the interface
# allows it to be accessed by specifying x, y locations.
class Grid:

    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(0.0)
            subgrid.append(row)

        self.grid = subgrid

    # Print the grid out.
    def display(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # A new line after each line of the grid
            print
            # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                value = self.grid[self.height - (i + 1)][j]
                if value == '%':
                    value = '----'
                    print value,
                else:
                    value = float(value)
                    print '%.2f' % value,

            # A new line after each line of the grid
            print
            # A line after the grid
        print

    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    def __eq__(self, other):
        if other is None: return False
        if self.height != other.height: return False
        if self.width != other.width: return False

        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] != other.grid[i][j]: return Fase

        return True

    def copy(self):
        g = Grid(self.width, self.height)
        for i in range(self.height):
            for j in range(self.width):
                g.grid[i][j] = self.grid[i][j]
        return g

    # return ture if the point(x, y) is a valid point on the map
    # false otherwise
    def isValidPoint(self, x, y):
        return 0 <= x <= self.width - 1 and 0 <= y <= self.height - 1

    # get the smaller value on two maps
    def minimumValueOnMap(self, other):
        if other is None: return False
        if self.height != other.height: return False
        if self.width != other.width: return False
        self_map = self.copy()
        for i in range(self.height):
            for j in range(self.width):
                self_value = self.grid[i][j]
                other_value = other.grid[i][j]
                if self_value != other_value:
                    self_map.grid[i][j] = min(int(other_value), int(self_value))

        return self_map

class MDPTestAgent(Agent):

    # The constructor.
    # initialize the tolerant ot value iteration and discount of bellman equation
    # and some test parameters
    def __init__(self):
        print "Running init!"
        self.tolerant = 0.0001
        self.dis_count = 0.8

        # self.numberOfGame = 0
        # self.time_start = time.time()
        # self.time_end = time.time()
        # self.max_time_need = 0
        # self.iteration_count = 0
        # self.average_count = 0

    # This function is run when the agent is created, and it has access
    # to state information, so we use it to build a map for the agent. 0.1457
    def registerInitialState(self, state):
        # self.numberOfGame += 1
        print "Running registerInitialState!"
        # Make a map of the right size
        self.makeMap(state)
        self.addWallsToMap(state)
        self.reward_map = self.map.copy()
        # map base codes
        self.is_small_grid = True
        if self.reward_map.getWidth() < 9:
            self.dis_count = 0.8
            self.tolerant = 0.0001
        else:
            self.is_small_grid = False
            self.dis_count = 0.85
            self.tolerant = 0.000001


        # initialize the position of ghosts
        self.current_ghosts_states = api.ghostStatesWithTimes(state)
        self.last_ghosts_states = api.ghostStatesWithTimes(state)

    def final(self, state):
        # del some unused variables
        del self.map
        del self.reward_map
        del self.current_ghosts_states
        del self.last_ghosts_states
        del self.ghosts_facing

        # print the average time consuming and max time consuming

        # time_end = time.time()
        # overall_time_need = (time_end - self.time_start)
        # time_need = (time_end - self.time_end)
        # self.time_end = time.time()
        # if time_need > self.max_time_need:
        #     self.max_time_need = time_need
        # print('average time cost', overall_time_need / self.numberOfGame, 's')
        # print('max time cost', self.max_time_need, 's')
        # print self.average_count/float(self.iteration_count)

    # Make a map by creating a grid of the right size (copy from mapAgent.py)
    def makeMap(self, state):
        corners = api.corners(state)
        height = self.getLayoutHeight(corners)
        width = self.getLayoutWidth(corners)
        self.map = Grid(width, height)

    # (copy from mapAgent.py)
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

    # Functions to manipulate the map.(copy from mapAgent.py)
    #
    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')

    # Create a map that contain reward for all movable states in MDP
    # the reward function depends on the distance to ghost and the type of states(ghost, food or empty)
    def initialRewardMap(self, state):

        foods = api.food(state)
        ghosts = map(lambda x: ((int(x[0][0]), int(x[0][1])), x[1]), self.current_ghosts_states)
        capsules = api.capsules(state)
        pacman = api.whereAmI(state)

        # find the real distance for ghosts to every points and take the minimum distance between different ghosts
        if ghosts:
            walkDistanceMapOfGhosts = self.getGhostWalkDistance(tuple(map(int, ghosts[-1][0])), self.ghosts_facing[-1], ghosts[-1][1])
        else:
            walkDistanceMapOfGhosts = Grid(self.reward_map.getWidth(), self.reward_map.getHeight())

        for ghost in ghosts[0:-1]:
            walkDistanceMapOfGhosts = walkDistanceMapOfGhosts.minimumValueOnMap(
                self.getGhostWalkDistance(tuple(map(int, ghost[0])), self.ghosts_facing[ghosts.index(ghost)], ghost[1]))

        # the distance between pacman and ghost
        distance_pacman_to_ghost = walkDistanceMapOfGhosts.getValue(pacman[0], pacman[1])

        # smallGird
        if self.is_small_grid:
            #  max ghost distance 17
            # if the pacman is too close the ghost the pacman will try the closest food
            # otherwise eat the food in bottom left
            if distance_pacman_to_ghost <= 2:
                self.rewardMapFunction(foods, capsules, map(lambda x: x[0], ghosts), walkDistanceMapOfGhosts, 1, 2,
                                       1, 3, -5)
            else:
                self.rewardMapFunction([foods[0]], capsules, map(lambda x: x[0], ghosts), walkDistanceMapOfGhosts, 1, 2,
                                       1, 3, -3)
        else:
            self.rewardMapFunction(foods, capsules, map(lambda x: x[0], ghosts), walkDistanceMapOfGhosts, 0, 1.5,
                                   2, 12, -5)
        # delete the distance map
        del walkDistanceMapOfGhosts

    def rewardMapFunction(self, foods, capsules, ghosts, distance_map, normal_initial_value, max_penalty_normal,
                          food_initial_value, max_penalty_food, ghost_value):
        """
            initialize a reward map for all reachable position
            Parameters:
                foods: a list of foods containing the position of foods
                capsules: a list of foods containing the position of capsules
                ghosts: a list of foods containing the position of ghosts
                distance_map: a map containing the real distance to the ghost
                normal_initial_value: the initial reward for empty position
                max_penalty_normal: the discount_factor for empty point (the higher value, the lower reward)
                food_initial_value: the initial reward for food and capsules position
                max_penalty_food: higher discount, the lower terminal value in food or capsules
                ghost_value: the reward of ghost
        """
        for i in range(1, self.reward_map.getWidth() - 1):
            for j in range(1, self.reward_map.getHeight() - 1):
                if self.reward_map.getValue(i, j) == '%':
                    continue
                else:
                    min_distance_ghost = float(distance_map.getValue(i, j))

                    score = normal_initial_value - max_penalty_normal / (min_distance_ghost + 1)

                    if (i, j) in foods + capsules:
                        score = score + food_initial_value - max_penalty_food / (min_distance_ghost + 1)

                    if (i, j) in ghosts:
                        score = score + ghost_value

                    self.reward_map.setValue(i, j, score)

    def getAction(self, state):
        # find the facing direction of ghost
        self.current_ghosts_states = api.ghostStatesWithTimes(state)

        valid_facing = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
        self.ghosts_facing = []
        for i in range(len(self.current_ghosts_states)):
            facing_of_ghost = (int(round(self.current_ghosts_states[i][0][0] - self.last_ghosts_states[i][0][0])),
                               int(round(self.current_ghosts_states[i][0][1] - self.last_ghosts_states[i][0][1])))
            # elated by pacman
            if facing_of_ghost not in valid_facing:
                facing_of_ghost = (0, 0)
            self.ghosts_facing.append(facing_of_ghost)

        self.last_ghosts_states = self.current_ghosts_states

        # search optimal policy and do an optimal action
        self.initialRewardMap(state)

        pacman = api.whereAmI(state)
        utilities_map = self.updateUtilities()

        legal = api.legalActions(state)

        action_vectors = [Actions.directionToVector(a, 1) for a in legal]
        optic_action = max(
            map(lambda x: (float(utilities_map.getValue(x[0] + pacman[0], x[1] + pacman[1])), x),
                action_vectors))
        return api.makeMove(Actions.vectorToDirection(optic_action[1]), legal)

    # value iteration
    def updateUtilities(self):
        utilities_map = self.map.copy()

        while True:
            temp_map = utilities_map.copy()
            delta = 0
            for i in range(1, self.map.getWidth() - 1):
                for j in range(1, self.map.getHeight() - 1):
                    if self.map.getValue(i, j) != '%':
                        new_value = self.reward_map.getValue(i, j) + self.dis_count * self.getMaxUtility(i, j, temp_map)
                        old_value = utilities_map.getValue(i, j)
                        utilities_map.setValue(i, j, new_value)
                        delta = max(delta, abs(new_value - old_value))

            if delta <= self.tolerant:
                break

        return utilities_map

    ##
    # return a maximum utility of a point
    # param: x, y: the coordinate of point
    # param temp_map: a map with utilities
    # return: the max reward
    def getMaxUtility(self, x, y, temp_map):
        near_pos = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        utility_of_origin = temp_map.getValue(x, y)
        max_reward = utility_of_origin
        for point in map(lambda vector: (vector[0] + x, vector[1] + y), near_pos):
            forward = temp_map.getValue(point[0], point[1])
            if forward == '%':
                continue
            else:
                total_reward = 0.8 * forward
                side_points = self.getSide(x, y, (point[0] - x, point[1] - y))
                for side_point in side_points:
                    side = temp_map.getValue(side_point[0], side_point[1])
                    total_reward += 0.1 * (utility_of_origin if side == '%' else side)

                if total_reward > max_reward:
                    max_reward = total_reward

        return max_reward

    ##
    # Vision 2
    # O(height * width)
    # return a distance map that the ghost run start from origin
    # @param origin: the start pos of ghost
    # @param facing: the ini facing of ghost, if facing == (0, 0), it can run all direction in first step
    # @param edible_time: after the edible_time closest to 0, ghost will become more dangerous and decrease all distance
    # @return: return a distance map
    def getGhostWalkDistance(self, origin, facing, edible_time):
        distance_map = self.map.copy()
        distance = 0 + edible_time
        distance_map.setValue(origin[0], origin[1], distance)
        queue = [[origin, facing]]
        temp_queue = []
        seen = {origin: 1}
        while queue:
            distance += 1
            while queue:
                [(x, y), current_facing] = queue.pop()

                valid_pos = [(current_facing[0] + x, current_facing[1] + y)]
                if current_facing == (0, 0):
                    valid_pos = self.getSide(x, y, current_facing)
                else:
                    valid_pos += self.getSide(x, y, current_facing)
                count = 0
                for (i, j) in valid_pos:
                    if distance_map.isValidPoint(i, j) and distance_map.getValue(i, j) != '%':
                        if (i, j) in seen:
                            if seen[(i, j)] < 2:
                                temp_queue.append([(i, j), (i - x, j - y)])
                                count += 1
                                seen[(i, j)] += 1
                                distance_map.setValue(i, j, min(distance, distance_map.getValue(i, j)))
                        else:
                            count += 1
                            temp_queue.append([(i, j), (i - x, j - y)])
                            seen[(i, j)] = 1
                            distance_map.setValue(i, j, distance)

                if count == 0 and seen[(x, y)] < 2:
                    next_point = (x - current_facing[0], y - current_facing[1])
                    temp_queue.append([next_point, (-current_facing[0], - current_facing[1])])
                    if next_point in seen:
                        distance_map.setValue(next_point[0], next_point[1], min(distance, distance_map.getValue(next_point[0], next_point[1])))
                        seen[(next_point[0], next_point[1])] += 1
                    else:
                        distance_map.setValue(next_point[0], next_point[1], distance)
                        seen[(next_point[0], next_point[1])] = 1

                    seen[(x, y)] += 1

            queue = temp_queue
            temp_queue = []
        return distance_map

    ##
    # if the point facing to one direction return the side points
    # @param x: x position of origin
    # @param y: y position of origin
    # @param facing: four direction (1, 0), (-1, 0), (0, 1), (0, -1) or no facing (0, 0)
    # @return: a list of side positions and return all neighbour positions if facing = (0, 0)
    def getSide(self, x, y, facing):

        if facing[0] == -1 or facing[0] == 1:
            side = [(x, 1 + y), (x, -1 + y)]
        elif facing[1] == 1 or facing[1] == -1:
            side = [(1 + x, y), (-1 + x, y)]
        else:
            side = [(1 + x, y), (x - 1, y), (x, y + 1), (x, y - 1)]

        return side
