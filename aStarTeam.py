# baselineTeam.py
# ---------------
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


# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
import copy
import statistics as st
from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions, Actions
import game
from util import nearestPoint


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveReflexAgent', second='DefensiveReflexAgent', numTraining=0):
    """
This function should return a list of two agents that will form the
team, initialized using firstIndex and secondIndex as their agent
index numbers.  isRed is True if the red team is being created, and
will be False if the blue team is being created.

As a potentially helpful development aid, this function can take
additional string-valued keyword arguments ("first" and "second" are
such arguments in the case of this function), which will come from
the --redOpts and --blueOpts command-line arguments to capture.py.
For the nightly contest, however, your team will be created without
any extra arguments, so you should make sure that the default
behavior is what you want for the nightly contest.
"""
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
    """
A base class for reflex agents that chooses score-maximizing actions
"""

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.start = gameState.getAgentPosition(self.index)
        self.midWidth = gameState.data.layout.width // 2
        self.height = gameState.data.layout.height
        self.retreat = False
        self.taken = None
        self.foodDef = self.getFoodYouAreDefending(gameState).asList()
        self.foodLocRad = None
        # We are using bfs search to locate all the safe and dangerous food once at the start of the game and store them in the list below
        bfs = BFS(gameState, self)
        self.safeFood = bfs.getSafeFood(self.getFood(gameState).asList())

    def boundariesPosition(self, gameState, distance):
        ''''
    Return a list of boundary position. Accepts a parameter "distance"
    to locate the required position from the mid field of the map. Note that the boundary here indicates coordinate that
    allow pacman that carrys food to score if reached.
    '''
        boundaries = []

        # Initialize the x-coordinate and change the position based on the parameter received
        if not self.red:
            x = self.midWidth + distance
        else:
            x = self.midWidth - distance - 1

        # Store all the available position from top to bottom in a list
        for y in range(self.height):
            boundaries.append((x, y))

        # If the position is not a wall, add it to the final list
        boundariesPosition = []
        for boundary in boundaries:
            if not gameState.hasWall(boundary[0], boundary[1]):
                boundariesPosition.append(boundary)
        return boundariesPosition

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        actions = gameState.getLegalActions(self.index)

        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        foodLeft = len(self.getFood(gameState).asList())

        if foodLeft <= 2:
            bestDist = 9999
            for action in actions:
                successor = self.getSuccessor(gameState, action)
                pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(self.start, pos2)
                if dist < bestDist:
                    bestAction = action
                    bestDist = dist
            return bestAction

        return random.choice(bestActions)

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def getFeatures(self, gameState, action):
        """
        Returns a counter of features for the state
        """
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)
        return features

    def getWeights(self, gameState, action):
        """
        Normally, weights do not depend on the gamestate.  They can be either
        a counter or a dictionary.
        """
        return {'successorScore': 1.0}

    def nullHeuristic(self, state, problem=None):
        return 0

    def aStarSearch(self, problem, gameState, heuristic=nullHeuristic):

        """
        This is a general a-star search function. It is taken from the P1 assignment.
        """
        frontier = util.PriorityQueue()
        frontier.push((problem.getStartState(), [], 0), 0)
        if problem.isGoalState(problem.getStartState()):
            return []
        reachedState = []
        while not frontier.isEmpty():
            # pop node and check goal
            currState, actions, totalCost = frontier.pop()
            # add node to visited list
            if currState not in reachedState:
                reachedState.append(currState)
                if problem.isGoalState(currState):
                    return actions
                # expand successors of current node
                successors = problem.getSuccessors(currState)
                for (nextState, direction, cost) in successors:
                    currentPath = list(actions)
                    # to make sure visited node is not added to list
                    if nextState not in reachedState:
                        currentPath.append(direction)
                        # evaluation function is inserted here [f(n) = g(n) + h(n)]
                        heuristicCost = totalCost + cost + heuristic(nextState, gameState)
                        successor_node = (nextState, currentPath, totalCost + cost)
                        frontier.push(successor_node, heuristicCost)

        return []

    def generalHeuristic(self, state, gameState):
        """
        We use this heuristic function to determine how dangerous the next move is.
        The shorter the distance of pacman and ghost, the higher the heuristic value
        """
        heuristic = 0

        # the heuristic below allows our pacmen to avoid ghost in opponent's side of the map
        if self.getMinGhostDistance(gameState) != None:

            # Get all the opponents on map
            opponents = []
            for opponent in self.getOpponents(gameState):
                opponents.append(gameState.getAgentState(opponent))
            ghosts = []
            for opponent in opponents:
                if not opponent.isPacman and opponent.getPosition() != None and opponent.scaredTimer < 2:
                    ghosts.append(opponent)

            if ghosts != None and len(ghosts) > 0:
                ghostsPosition = []
                ghostsDistance = []

                # get position of ghost
                for ghost in ghosts:
                    ghostsPosition.append(ghost.getPosition())

                # get distance of pacman and ghosts
                for ghostPosition in ghostsPosition:
                    if state != None and ghostPosition != None:
                        ghostsDistance.append(self.getMazeDistance(state, ghostPosition))

                # get shortest ghost distance
                if ghostsDistance != []:
                    ghostDistance = min(ghostsDistance)

                    # the shorter the distance of ghost and pacman, the higher the heuristic. The value increases exponentially.
                    if ghostDistance < 2:
                        heuristic = pow((5 - ghostDistance), 5)

                # The heuristic below is to avoid pacmen to repeat the same move if it is stuck in a certain area
                # check observation history to see if pacman has been repeating the same states for the last 14 moves
                if len(self.observationHistory) > 14:
                    previousObservations = self.observationHistory[-14:]
                    uniquePreviousObservations = set()

                    # store all observations in a set to get a list of unique position
                    for obs in previousObservations:
                        uniquePreviousObservations.add(obs.getAgentState(self.index).getPosition())

                    # if pacman has not visited more than 4 states in 14 moves, we assume it is stuck.
                    if len(uniquePreviousObservations) < 5:
                        if state in uniquePreviousObservations:
                            # the heuristic is equals to the heuristic when the pacman and ghost is in the same state.
                            # This allows pacman to suicide to the ghost if necessary or choose another path
                            heuristic += pow(5, 5)

        # the heuristic below allows our ghost to avoid pacmen in our side of the map when feared
        if self.getMinPacmanDistance(gameState) != None and gameState.getAgentState(self.index).scaredTimer > 0:

            # Get all the opponents on map
            opponents = []
            for opponent in self.getOpponents(gameState):
                opponents.append(gameState.getAgentState(opponent))
            pacmens = []
            for opponent in opponents:
                if opponent.isPacman and opponent.getPosition() != None:
                    pacmens.append(opponent)

            if pacmens != None and len(pacmens) > 0:
                pacmensPosition = []
                pacmensDistance = []

                # get position of opponent pacman
                for pacmen in pacmens:
                    pacmensPosition.append(pacmen.getPosition())

                # get distance of pacman and ghosts
                for pacmenPosition in pacmensPosition:
                    if state != None and pacmenPosition != None:
                        pacmensDistance.append(self.getMazeDistance(state, pacmenPosition))

                # get shortest pacmen distance
                if pacmensDistance != []:
                    pacmenDistance = min(pacmensDistance)

                    # the shorter the distance of ghost and pacman, the higher the heuristic. The value increases exponentially.
                    if pacmenDistance < 2:
                        heuristic += pow((5 - pacmenDistance), 5)

        return heuristic

    def getMinGhostDistance(self, gameState):
        ''''
    return nearest ghost position and its distance with pacman
    '''
        ghostsDistance = dict()
        ghostsPosDist = None
        opponents = []

        # get all opponent's ghost an store it in a dictionary array
        for opponent in self.getOpponents(gameState):
            opponents.append(gameState.getAgentState(opponent))
        ghosts = []
        for opponent in opponents:
            if not opponent.isPacman and opponent.getPosition() != None:
                ghosts.append(opponent)
        if len(ghosts) > 0:
            for ghost in ghosts:
                ghostDist = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), ghost.getPosition())
                ghostsDistance.update({ghost: ghostDist})

            # find ghost position with the minimum distance from pacman
            ghostsPosDist = min(ghostsDistance, key=ghostsDistance.get), ghostsDistance[
                min(ghostsDistance, key=ghostsDistance.get)]

        return ghostsPosDist

    def getMinPacmanDistance(self, gameState):
        ''''
    return nearest Pacman position and its distance with ghost
    '''
        pacmanDistance = dict()
        pacmanPosDist = None
        opponents = []

        # get all opponent's pacman an store it in a dictionary array
        for opponent in self.getOpponents(gameState):
            opponents.append(gameState.getAgentState(opponent))
        pacmans = []
        for opponent in opponents:
            if opponent.isPacman and opponent.getPosition() != None:
                pacmans.append(opponent)
        if len(pacmans) > 0:
            for pacman in pacmans:
                pacmanDist = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),
                                                  pacman.getPosition())
                pacmanDistance.update({pacman: pacmanDist})
            # find opponent's pacman position with the minimum distance from our pacman
            pacmanPosDist = min(pacmanDistance, key=pacmanDistance.get), pacmanDistance[
                min(pacmanDistance, key=pacmanDistance.get)]
        return pacmanPosDist

    def findMinHomeBoundaryDist(self, gameState):
        ''''
    return the distance of the agent and the nearest home boundary
    '''

        boundariesPosition = self.boundariesPosition(gameState, 1)
        distance = []
        for boundaryPosition in boundariesPosition:
            distance.append(self.getMazeDistance(boundaryPosition, gameState.getAgentState(self.index).getPosition()))

        return min(distance)

    def opponentScaredTimer(self, gameState):
        """
    Return opponent's scared timer
    """
        opponentsScaredTime = 0
        opponents = [opponent for opponent in self.getOpponents(gameState) if
                     gameState.getAgentState(opponent).scaredTimer > 1]
        for opponent in opponents:
            opponentsScaredTime = gameState.getAgentState(opponent).scaredTimer
        return opponentsScaredTime


class OffensiveReflexAgent(ReflexCaptureAgent):
    """
A reflex agent that seeks food. This is an agent
we give you to get an idea of what an offensive agent might look like,
but it is by no means the best or only way to build an offensive agent.
"""

    def chooseAction(self, gameState):
        """
    Update safe and dangerous food after every pacman action. The codes below can reduce computational work by
    initialize all the safe and dangerous food at the start of the game and compare it with the current food left on
    map instead of using bfs to search for safe and dangerous food after every pacman action.
    """
        currSafeFood = [food for food in self.getFood(gameState).asList() if food in self.safeFood]
        self.safeFood = copy.deepcopy(currSafeFood)

        """
    Decision Tree
    """
        # Variables
        minPacmanDist = self.getMinPacmanDistance(gameState)
        agentState = gameState.getAgentState(self.index)
        numOfCapsules = self.getCapsules(gameState)
        foodList = self.getFood(gameState).asList()
        minGhostDist = self.getMinGhostDistance(gameState)
        minHomeBoundaryDist = self.findMinHomeBoundaryDist(gameState)
        gameTimeLeft = gameState.data.timeleft

        # Problems
        if minPacmanDist is not None:
            hunter = Hunter(gameState, self, self.index, minPacmanDist[0])
        else:
            hunter = None
        capsules = Capsules(gameState, self, self.index)
        safeFood = SafeFood(gameState, self, self.index)
        food = SearchFood(gameState, self, self.index)
        escape = Escape(gameState, self, self.index)
        returnHome = Return(gameState, self, self.index)

        # Search Capsules problem
        # This problem is chosen when pacman is not carrying any food, there are still capsules on the map and opponents
        # are scared for less than 10 moves. This is the first priority goal of our pacman when the game starts or after
        # it is chased by opponent's ghost back to its territory.
        if len(numOfCapsules) != 0 and len(self.safeFood) <= 0 and self.opponentScaredTimer(gameState) < 10:
            return self.aStarSearch(capsules, gameState, self.generalHeuristic)[0]

        # Search Safe Food problem
        # This problem is chosen if there is no more capsules on the map and pacman is not carrying any food
        if agentState.numCarrying == 0 and (len(self.safeFood) >= 1):
            return self.aStarSearch(safeFood, gameState, self.generalHeuristic)[0]

        # Search Food problem
        # This problem is chosen if there is no more capsules and safe food on the map while pacman is not carrying any food
        if len(self.safeFood) == 0 and agentState.numCarrying == 0 and len(foodList) != 0:
            return self.aStarSearch(food, gameState, self.generalHeuristic)[0]

        # Hunter problem (Hunt Pacman if offensive ghost)
        # This problem is chosen when the pacman is in its home territory and a ghost is within 5 maze distance from it
        if minPacmanDist is not None and minPacmanDist[1] <= 5 and agentState.scaredTimer <= 0:
            return self.aStarSearch(hunter, gameState, self.generalHeuristic)[0]

        # Escape problem
        # This problem is chosen if opponent's ghost is within 5 maze distance from pacman
        if minGhostDist is not None and minGhostDist[1] <= 5 and minGhostDist[0].scaredTimer < 5:
            if len(self.aStarSearch(escape, self.generalHeuristic)) != 0:
                return self.aStarSearch(escape, gameState, self.generalHeuristic)[0]
            else:
                return 'Stop'

        # Return problem
        # This is problem is chosen when there is 2 food left on map or when time is almost up
        if len(foodList) < 3 or minHomeBoundaryDist + 60 > gameTimeLeft:
            if len(self.aStarSearch(returnHome, self.generalHeuristic)) != 0:
                return self.aStarSearch(returnHome, gameState, self.generalHeuristic)[0]
            else:
                return 'Stop'

        # Performs normal food search if no decision is made
        return self.aStarSearch(food, gameState, self.generalHeuristic)[0]

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        foodList = self.getFood(successor).asList()
        features['successorScore'] = -len(foodList)  # self.getScore(successor)

        # Compute distance to the nearest food

        if len(foodList) > 0:  # This should always be True,  but better safe than sorry
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance
        return features

    def getWeights(self, gameState, action):
        return {'successorScore': 100, 'distanceToFood': -1}


class PositionSearchProblem:
    """
    This class is partly referenced from the PositionSearchProblem class in P1 searchAgent.py.
    This class acts as a parent class for the rest of the problem class defined below.
    A search problem defines the state space, start state, goal test, successor
    function and cost function.  This search problems can be used to find paths
    to a particular point on the pacman board.
    """

    def __init__(self, gameState, agentIndex):
        self.startState = gameState.getAgentState(agentIndex).getPosition()
        self.walls = gameState.getWalls()
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        return None

    def getSuccessors(self, state):
        """
    Returns successor states, the actions they require, and a cost of 1.
    For a given state, this should return a list of triples,
     (successor, action, stepCost), where 'successor' is a
     successor to the current state, 'action' is the action
     required to get there, and 'stepCost' is the incremental
     cost of expanding to that successor
    """
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state
            dx, dy = game.Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append((nextState, action, cost))

        # Bookkeeping for display purposes
        self._expanded += 1  # DO NOT CHANGE
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions):
        """
    Returns the cost of a particular sequence of actions. If those actions
    include an illegal move, return 999999.
    """
        if actions == None: return 999999
        x, y = self.getStartState()
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = game.Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x, y))
        return cost


class SearchFood(PositionSearchProblem):
    """
  This problem defines the position of food or capsule as the goal state
  """

    def __init__(self, gameState, agent, agentIndex):
        super().__init__(gameState, agentIndex)
        self.food = agent.getFood(gameState)

    def isGoalState(self, state):
        return state in self.food.asList()


class SearchOtherFood(PositionSearchProblem):
    """
  This problem defines the position of food or capsule as the goal state
  """

    def __init__(self, gameState, agent, agentIndex, food):
        super().__init__(gameState, agentIndex)
        self.food = food

    def isGoalState(self, state):
        return state in self.food


class Return(PositionSearchProblem):
    """
  This problem defines the boundary of our side of the map as the goal state
  """

    def __init__(self, gameState, agent, agentIndex):
        super().__init__(gameState, agentIndex)
        self.homeBoundary = agent.boundariesPosition(gameState, 1)

    def isGoalState(self, state):
        return state in self.homeBoundary


class Escape(PositionSearchProblem):
    """
  This problem defines the home boundary or nearby capsule as the goal state when being chased by ghosts
  """

    def __init__(self, gameState, agent, agentIndex):
        super().__init__(gameState, agentIndex)
        self.capsule = agent.getCapsules(gameState)
        self.homeBoundaries = agent.boundariesPosition(gameState, 1)

    def isGoalState(self, state):
        return state in self.homeBoundaries or state in self.capsule


class Capsules(PositionSearchProblem):
    """
      This problem defines the capsule as the goal state when being chased by ghosts
  """

    def __init__(self, gameState, agent, agentIndex):
        super().__init__(gameState, agentIndex)
        self.capsules = agent.getCapsules(gameState)

    def isGoalState(self, state):
        return state in self.capsules


class DangerousFood(PositionSearchProblem):
    """
  This problem defines the food that have only one direction home as its goal state
  """

    def __init__(self, gameState, agent, agentIndex):
        super().__init__(gameState, agentIndex)
        self.dangerousFood = agent.dangerousFood

    def isGoalState(self, state):
        return state in self.dangerousFood


class SafeFood(PositionSearchProblem):
    """
  This problem defines the food that have more than one direction home as its goal state
  """

    def __init__(self, gameState, agent, agentIndex):
        super().__init__(gameState, agentIndex)
        self.safeFood = agent.safeFood

    def isGoalState(self, state):
        return state in self.safeFood


class Hunter(PositionSearchProblem):
    """
      This problem defines the position of Pacman as its goal state
  """

    def __init__(self, gameState, agent, agentIndex, pacman):
        super().__init__(gameState, agentIndex)
        self.pacmanPos = pacman.getPosition()

    def isGoalState(self, state):
        return state == self.pacmanPos


class Retreat(PositionSearchProblem):
    """
  This problem defines any position that is 5 horizontal distance away from the boundary  as the goal state when successfully escaped from ghost
  """

    def __init__(self, gameState, agent, agentIndex):
        super().__init__(gameState, agentIndex)
        self.homeBoundaries = agent.boundariesPosition(gameState, 5)

    def isGoalState(self, state):
        return state in self.homeBoundaries


class TakenFood(PositionSearchProblem):

    def __init__(self, gameState, agent, agentIndex):
        super().__init__(gameState, agentIndex)
        self.foodPos = agent.taken

    def isGoalState(self, state):
        return state == self.foodPos


class SmallRadius(PositionSearchProblem):

    def __init__(self, gameState, agent, agentIndex):
        super().__init__(gameState, agentIndex)
        self.foodPos = agent.foodLocRad[0]

    def isGoalState(self, state):
        return state == self.foodPos


class DefensiveReflexAgent(ReflexCaptureAgent):
    """
A reflex agent that keeps its side Pacman-free. Again,
this is to give you an idea of what a defensive agent
could be like.  It is not the best or only way to make
such an agent.
"""

    def getMinFoodTakenDistance(self, gameState):
        '''
    returns nearest recently taken food position
    '''
        preState = self.getPreviousObservation()
        preFood = self.getFoodYouAreDefending(preState)
        crntFood = self.getFoodYouAreDefending(gameState)

        # Checks if food has been taken
        if len(crntFood.asList()) < len(preFood.asList()):
            # print("CrtFood = %i", len(crntFood.asList()))
            # print("PreFood = %i", len(preFood.asList()))

            for food in preFood.asList():
                if food not in crntFood.asList():
                    return food

        return None

    def getFoodLeftRadius(self, gameState):
        foodDefX = []
        foodDefY = []
        for t in self.foodDef:
            foodDefX.append(t[0])
            foodDefY.append(t[1])

        xMean = st.mean(foodDefX)
        yMean = st.mean(foodDefY)
        xStdev = st.stdev(foodDefX)
        yStdev = st.stdev(foodDefY)

        stdFood = []
        for x, y in zip(foodDefX, foodDefY):
            zScoreX = None
            zScoreY = None

            if xStdev != 0: zScoreX = (x - xMean) / xStdev
            if yStdev != 0: zScoreY = (y - yMean) / yStdev

            if zScoreX != None and zScoreY != None:
                if abs(zScoreX) < 2.5 and abs(zScoreY) < 2.5:
                    stdFood.append(tuple([x, y]))
            elif zScoreX != None:
                if abs(zScoreX) < 2.5:
                    stdFood.append(tuple([x, y]))
            elif zScoreY != None:
                if abs(zScoreY) < 2.5:
                    stdFood.append(tuple([x, y]))

        maxDist = 0
        minDist = 999
        meanFoodLoc = tuple([round(xMean), round(yMean)])
        for food in stdFood:
            dist = distanceCalculator.manhattanDistance(meanFoodLoc, food)
            if dist > maxDist:
                maxDist = dist
            if dist < minDist:
                minDist = dist
                minDistFood = food

        if gameState.hasWall(meanFoodLoc[0], meanFoodLoc[1]):
            meanFoodLoc = minDistFood

        return [meanFoodLoc, maxDist]

    def chooseAction(self, gameState):

        # Calling Getters once for optimisation
        getSelf = gameState.getAgentState(self.index)
        getTeam = gameState.getAgentState(self.agentsOnTeam[0])
        getTime = gameState.data.timeleft
        getFoodDef = self.getFoodYouAreDefending(gameState).asList()
        getFood = self.getFood(gameState).asList()
        getGhost = self.getMinGhostDistance(gameState)
        getPacman = self.getMinPacmanDistance(gameState)
        getBoundary = self.findMinHomeBoundaryDist(gameState)

        # Updating Other Food list, Changes as food left lessens
        if len(getFood) > 25:
            getotherfood = [food for food in getFood if
                            self.getMazeDistance(getSelf.getPosition(), food) <= 3 or self.getMazeDistance(
                                getTeam.getPosition(), food) > 5]
        elif len(getFood) > 15:
            getotherfood = [food for food in getFood if
                            self.getMazeDistance(getSelf.getPosition(), food) <= 3 or self.getMazeDistance(
                                getTeam.getPosition(), food) > 4]
        elif len(getFood) > 10:
            getotherfood = [food for food in getFood if
                            self.getMazeDistance(getSelf.getPosition(), food) <= 3 or self.getMazeDistance(
                                getTeam.getPosition(), food) > 3]
        else:
            getotherfood = getFood

        # Make sure there is a Previous Observation before checking if food has been taken
        if getTime < 1195:
            getFoodtaken = self.getMinFoodTakenDistance(gameState)
            if getFoodtaken != None:
                self.taken = getFoodtaken  # Location of food most recently taken by enemy

            # Resets food taken to None if the enemy team manages to deposit food
            # or if you reach the location of that food
            if self.getScore(gameState) < self.getScore(self.getPreviousObservation()) or \
                    self.taken != None and getSelf.getPosition() == self.taken:
                self.taken = None

        # Updates Food Defending mean location and radius
        if self.foodLocRad == None or len(getFoodDef) != len(self.foodDef) and 10 >= len(getFoodDef) >= 4:
            self.foodDef = getFoodDef
            self.foodLocRad = self.getFoodLeftRadius(gameState)

        # Problems
        if getPacman != None:
            pacmanhunter = Hunter(gameState, self, self.index, getPacman[0])
        else:
            pacmanhunter = None

        if getGhost != None:
            ghosthunter = Hunter(gameState, self, self.index, getGhost[0])
        else:
            ghosthunter = None

        food = SearchFood(gameState, self, self.index)
        otherFood = SearchOtherFood(gameState, self, self.index, getotherfood)
        takenFood = TakenFood(gameState, self, self.index)
        escape = Escape(gameState, self, self.index)
        returnHome = Return(gameState, self, self.index)
        retreat = Retreat(gameState, self, self.index)
        smallRadius = SmallRadius(gameState, self, self.index)

        # Hunter problem (Hunt Pacman if Defensive ghost)
        if getPacman != None and getPacman[1] <= 5 and getSelf.scaredTimer <= 0:
            # print("Hunt Pacman")
            return self.aStarSearch(pacmanhunter, gameState)[0]

        # Escape Problem (As Scared Ghost Escaping Pacman)
        if getPacman != None and getPacman[1] <= 5 and getSelf.scaredTimer > 0:
            action = self.aStarSearch(escape, gameState, self.generalHeuristic)
            if len(action) != 0:
                return action[0]
            else:
                return 'Stop'

        # Full Offensive Problem
        if len(getFoodDef) >= 10 and len(getFoodDef) - len(getFood) > 5:
            action = self.aStarSearch(otherFood, gameState, self.generalHeuristic)
            if len(action) != 0:
                return action[0]

        # Search Taken Food Problem
        if self.taken != None and getSelf.getPosition() != self.taken and getSelf.scaredTimer <= 5 and len(
                getFood) > len(getFoodDef):
            # print("Taken = " + str(self.taken))
            return self.aStarSearch(takenFood, gameState, self.generalHeuristic)[0]

        # Small Radius Problem
        if 10 >= len(self.foodDef) >= 4 and self.foodLocRad[1] < 5:
            action = self.aStarSearch(smallRadius, gameState, self.generalHeuristic)
            if len(action) != 0:
                return action[0]

        # Hunter problem (Hunt Ghost if Defensive Pacman)
        if getGhost != None and getGhost[0].scaredTimer > 4 and getGhost[1] <= 4:
            # print("Hunt Ghost")
            return self.aStarSearch(ghosthunter, gameState)[0]

        # Escape problem
        if getGhost != None and getGhost[1] < 5 and getGhost[0].scaredTimer <= 4:
            action = self.aStarSearch(escape, gameState, self.generalHeuristic)
            if len(action) != 0:
                return action[0]
            else:
                return 'Stop'

        # Return problem
        if len(self.getFood(gameState).asList()) < 3 \
                or getBoundary + 60 > getTime:
            # Change to only call aStarSearch once (For optimisation).
            action = self.aStarSearch(returnHome, gameState, self.generalHeuristic)
            if len(action) != 0:
                # print("Return")
                return action[0]
            else:
                return 'Stop'

        # Search Food Away From Offensive Agent Problem
        action = self.aStarSearch(otherFood, gameState, self.generalHeuristic)
        if len(action) != 0:
            return action[0]

        # Search Food Problem
        return self.aStarSearch(food, gameState, self.generalHeuristic)

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        foodList = self.getFood(successor).asList()
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0)
        features['onDefense'] = 1
        if myState.isPacman: features['onDefense'] = 0

        # Computes distance to invaders we can see
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        features['numInvaders'] = len(invaders)
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)

        if len(foodList) > 0:  # This should always be True,  but better safe than sorry
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance
        return features

    def getWeights(self, gameState, action):
        return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}


class BFS:
    """
This class is used to explore the map when ghost position can be ignored.
"""

    def __init__(self, gameState, agent):

        self.food = agent.getFood(gameState).asList()
        self.walls = gameState.getWalls()
        self.homeBoundaries = agent.boundariesPosition(gameState, 1)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0

    def Search(self, startState, stateReached, goalState):
        """
  This a geneal BFS search method
  """
        frontier = util.Queue()
        frontier.push((startState, [], 0))
        # check goal state
        if startState in goalState:
            return []
        while not frontier.isEmpty():
            currState, actions, totalCost = frontier.pop()
            # expand successors
            successors = self.getSuccessors(currState)
            for (nextState, direction, cost) in successors:
                # check goal state
                if nextState in goalState:
                    return actions + [direction]
                # add to frontier if node has not been visited
                if nextState not in stateReached:
                    stateReached.append(nextState)
                    frontier.push((nextState, actions + [direction], totalCost + cost))

    def getSuccessors(self, state):
        """
  This function is from P1 searchAgent.py
  Returns successor states, the actions they require, and a cost of 1.
  For a given state, this should return a list of triples,
   (successor, action, stepCost), where 'successor' is a
   successor to the current state, 'action' is the action
   required to get there, and 'stepCost' is the incremental
   cost of expanding to that successor
  """
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state
            dx, dy = game.Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append((nextState, action, cost))

        # Bookkeeping for display purposes
        self._expanded += 1  # DO NOT CHANGE
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getNumOfValidDirectionBackHome(self, food):
        """
    We use BFS search to indicate whether all the legal neighbors of the food eventually lead the pacman back home.
    This method aims to identify food that are located in alleys that have dead end.
    """
        count = 0
        stateReached = []
        stateReached.append(food)

        # get all legal next state (last state is the state checked)
        legalNeighbors = Actions.getLegalNeighbors(food, self.walls)
        for legalNeighbor in legalNeighbors[:-1]:
            closed = copy.deepcopy(stateReached)
            if self.Search(legalNeighbor, closed, self.homeBoundaries):
                count += 1

        return count

    def getSafeFood(self, food):
        """
    Return a list of safe food
    """
        safeFood = []
        for f in food:
            count = self.getNumOfValidDirectionBackHome(f)
            if count > 1:
                safeFood.append(f)
        return safeFood