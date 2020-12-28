from pacman import Directions
from game import Agent
import api
import game
import random
import util

DIRECTION_VECTORS = {Directions.NORTH: (0,1), Directions.SOUTH: (0, -1), Directions.EAST: (1, 0), Directions.WEST: (-1, 0)}
EPSILON = 0.01
SMALL_MAP_VALUES = { 'ghost_value': -5.0, 'deadend': -10.0, 'food': 1.0, 'empty': 0.0, 'discount': 0.9, 'ghost_range':  12, 'iterations': 10 }
MEDIUM_MAP_VALUES = { 'ghost_value': -5.0, 'deadend': -10.0, 'food': 1.0, 'empty': 0.0, 'discount': 0.9, 'ghost_range':  12, 'iterations': 10 }

# ghost_value=-5, deadend = -10, food=1, disc = 0.9, ghost_range = 12 for 77% over 20000

class MDPAgent(Agent):

    def test(self, ghost_value=-50, ghost_range=12, food_value=1, empty_value=0, discount=0.6, deadend_value = -50.0):
        """
        Method for modifying of global variables for testing purposes
        """
        self.values['ghost_value'] = ghost_value
        self.values['ghost_range'] = ghost_range
        self.values['food'] = food_value
        self.values['empty'] = empty_value
        self.values['discount'] = discount
        self.values['deadend'] = deadend_value

    def __init__(self):
        """
        Constructor to initialise the dictionaries to be used on the bellman's.
        """
        self.values = SMALL_MAP_VALUES
        self.rewards = {}
        self.utilities = {}
        self.stateNeighbours = {}

    def registerInitialState(self, state):
        """
        Builds the agent's internal view of the world using the current game state in calls to the api.

        @param state: The current pacman game state.
        """

        # Set constant world values.
        self.corners = api.corners(state)
        self.walls = api.walls(state)

        # Calculate the width and height using the corners.
        from operator import itemgetter
        self.height = max(self.corners, key=itemgetter(1))[1] + 1
        self.width= max(self.corners, key=itemgetter(0))[0] + 1

        # Holds the set of all reachable locations.
        self.valid_locations = set((x, y) for x in range(self.width) for y in range(self.height) if (x, y) not in self.walls)

    def buildMap(self, state):
        """ 
        Builds an internal representation of the current game world using information gained from calls to the api

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
        Initializes the dictionary which will hold the reward value for each state.
        This must be run before bellmans.
        """

        self.rewards = {pos : self.values['empty'] for pos in self.valid_locations}
        self.rewards.update({pos : self.values['food'] for pos in self.food})
        self.rewards.update(self.ghostRewardValues())

    def ghostRewardValues(self):
        """
        Returns the reward values for locations relevant to ghosts.
        Uses a depth-limited breadth-first search to calculate reward values that are inversely proportional to the distance of nearby ghosts.
        Considers deadends in its calculations as they are only dangerous when a ghost is nearby.

        @returns dict: The reward values for positions
        """
        ghost_state_rewards = {}

        for ghost in self.ghosts:
            # Use of two queues to perform a breadth-first search.
            active_queue = util.Queue()
            inactive_queue = util.Queue()
            location = (int(ghost[0]), int(ghost[1]))
            active_queue.push(location)

            for counter in range(1, self.values['ghost_range']):
                while active_queue.isEmpty() is False:
                    pos = active_queue.pop()

                    # Add the adjacent locations of the ghost to the queue.
                    next_locs = [self.moveInDirection(pos, move) for move in self.getLegalMoves(pos)]
                    for loc in next_locs:
                        inactive_queue.push(loc)

                    # If there is only one possible move this most be a deadend.
                    # Don't add a deadend penalty if this is the last food or pacman is adjacent to it.
                    if (len(next_locs) == 1) and (len(self.food) > 1) and (util.manhattanDistance(self.pacman, pos) > 1):
                         reward_value = self.rewards[pos] + self.values['deadend'] + self.values['ghost_value'] * (1.0 / counter)
                    # No deadend so consider this a normal ghost-penalized state.
                    else:
                         reward_value = self.rewards[pos] + self.values['ghost_value'] * (1.0 / counter)

                    # Ensure that we only replace a ghost value with more signifcant (negative) value.
                    if pos not in ghost_state_rewards or ghost_state_rewards[pos] > reward_value:
                        ghost_state_rewards[pos] = reward_value

                # Swap the queues
                inactive_queue, active_queue = active_queue, inactive_queue
        return ghost_state_rewards

    def setNeighbours(self):
        """
        Populates the state neighbours dictionary with the possible neighbours for each state, including the nondeterministic possibilities.
        """
        for location in self.valid_locations:
            moves = {}
            for direction in DIRECTION_VECTORS:
                # Calculate the resulting location from a move in this direction.
                move = self.moveInDirection(location, direction)

                # If we move into a wall we bounce back to the original position.
                if move in self.walls:
                    move = location
                moves[direction] = move

            # For each action we set the result of moving in the intended direction as index 0, and possible unintended directions as indices 1 and 2.
            moves_dict = {
                    Directions.NORTH: [moves[Directions.NORTH], moves[Directions.EAST], moves[Directions.WEST]],
                    Directions.SOUTH: [moves[Directions.SOUTH], moves[Directions.EAST], moves[Directions.WEST]],
                    Directions.EAST: [moves[Directions.EAST], moves[Directions.NORTH], moves[Directions.SOUTH]],
                    Directions.WEST: [moves[Directions.WEST], moves[Directions.NORTH], moves[Directions.SOUTH]]
                }

            self.stateNeighbours[location] = moves_dict
    
    def getLegalMoves(self, location):
        """
        @param location: where to move from
        @returns list: legal moves for a direction
        """
        legal_moves = []
        for direction in DIRECTION_VECTORS:
            if self.moveInDirection(location, direction) in self.valid_locations:
                legal_moves.append(direction)
        return legal_moves

    def moveInDirection(self, location, direction):
        """
        Helper method to get the result of a movement.
        @param location: where to move from.
        @param direction: the action to undertake.
        @returns tuple: the resulting location.
        """
        (deltaX, deltaY) = DIRECTION_VECTORS[direction]
        return (location[0] + deltaX, location[1] + deltaY)

    def calculateExpectedValue(self, utilities, location, move):
        """
        Calculates the expected value of a move using for a location using the coursework's given probabilties
        @param utilities: the current utility values for each location to be used in the calculation.
        @param location: the state for which the expected value we are calculating.
        @param move:
        @result float: the expected value for moving in a given direction from a given location.
        """
        neighbours = self.stateNeighbours[location]
        destinations = neighbours[move]
        return 0.8 * utilities[destinations[0]] + 0.1 * utilities[destinations[1]] + 0.1 * utilities[destinations[1]]

    def modifiedPolicyIteration(self):
        """
        Repeats the bellman's equation a set number of times to calculate utilities for each valid location
        """

        # Set initial utilities to zero.
        self.utilities = {location: 0 for location in self.valid_locations}

        # Start with random policies for each state.
        self.policies = {location: random.choice(self.getLegalMoves(location)) for location in self.valid_locations}
    
        # We need to retain a copy of all old utilities values to be used for calculating expected values for new utilities.
        import copy
        new_utilities = copy.deepcopy(self.utilities)

        # We iterate so long as there is significant (> epsilon) change.
        changed = True
        while changed:
            changed = False 
          # Perform approximate bellmans.
            for i in range(self.values['iterations']):
                for location in self.valid_locations:
                    policy = self.policies[location]
                    # Stopping is a deterministic action so we just use the current location's utility.
                    if (policy is Directions.STOP):
                        expectedValue = self.utilities[location]
                    else:
                        expectedValue = self.calculateExpectedValue(self.utilities, location, policy)
                    new_utilities[location] = self.rewards[location] + self.values['discount'] * expectedValue
                self.utilities = new_utilities
            
            # Check for improved policy decisions.
            for location in self.valid_locations:
                moves = self.getLegalMoves(location)
                # For each move we get the expected value using the possible neighbours.
                expectedValues = {move: self.calculateExpectedValue(new_utilities, location, move) for move in moves}
                expectedValues[Directions.STOP] = new_utilities[location]

                # Find the policy that results in the highest expected value state.
                values = list(expectedValues.values())
                max_value = max(values)
                new_policy = list(expectedValues.keys())[values.index(max_value)]

                # Check if the new policy produces a significant change in utility over the old value.
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
        # Set constants about environment.
        self.ghosts = api.ghosts(state)
        self.capsules = api.capsules(state)
        self.pacman = api.whereAmI(state)
        self.food = api.food(state)

        # Build internal data.
        self.buildMap(state)
        self.setRewards()
        self.setNeighbours()

        # Peform the modified policy iteration algorithm.
        self.modifiedPolicyIteration()

        # For debugging
        # self.display()
        # self.display(info='utilities')
        # self.display(info='rewards')

        legal = api.legalActions(state)
        return api.makeMove(self.policies[self.pacman], legal)
