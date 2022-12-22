# qlearningAgents.py
# ------------------
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


from game import *
from learningAgents import ReinforcementAgent
from captureAgents import CaptureAgent
# from featureExtractors import *
from myTeam import SearchFood
import random,util,math

def createTeam(firstIndex, secondIndex, isRed,
               first='ApproximateQAgent', second='NullAgent', numTraining=0):
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
    print(first, " isRed: ", isRed)
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

class QLearningAgent(ReinforcementAgent):
    """
      Q-Learning Agent

      Functions you should fill in:
        - computeValueFromQValues
        - computeActionFromQValues
        - getQValue
        - getAction
        - update

      Instance variables you have access to
        - self.epsilon (exploration prob)
        - self.alpha (learning rate)
        - self.discount (discount rate)

      Functions you should use
        - self.getLegalActions(state)
          which returns legal actions for a state
    """

    def __init__(self, **args):
        "You can initialize Q-values here..."
        self.qValues = util.Counter()
        ReinforcementAgent.__init__(self, **args)

    # def getLegalActions(self):
    #     currGameState = self.getCurrentObservation()
    #     return currGameState.getLegalActions(self.index)

    def getQValue(self, state, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        return float(self.qValues[(state, action)])

    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        qValues = []
        for action in self.getLegalActions(state):
            qValues.append((self.getQValue(state, action), action))
        if len(qValues):
            return max(qValues)[0]
        else:
            return 0.0

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        qValues = []
        for action in self.getLegalActions(state):
            qValues.append((self.getQValue(state, action), action))
        if len(qValues):
            return max(qValues)[1]
        else:
            return None

    def getAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.

          HINT: You might want to use util.flipCoin(prob)
          HINT: To pick randomly from a list, use random.choice(list)
        """
        self.observationHistory.append(state)
        legalActions = self.getLegalActions(state)
        action = None
        if len(legalActions):
            if util.flipCoin(self.epsilon):
                action = random.choice(legalActions)
            else:
                action = self.getPolicy(state)
        return action


    def update(self, state, action, nextState, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here

          NOTE: You should never call this function,
          it will be called on your behalf
        """

        qval = self.getQValue(state, action) + self.alpha*((reward+self.discount*self.getValue(nextState)) - self.getQValue(state, action))
        self.qValues[(state, action)] = qval
        return qval


    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)

class PacmanQAgent(QLearningAgent):
    "Exactly the same as QLearningAgent, but with different default parameters"

    def __init__(self, epsilon=0.05,gamma=0.8,alpha=0.2, numTraining=0, **args):
        """
        These default parameters can be changed from the pacman.py command line.
        For example, to change the exploration rate, try:
            python pacman.py -p PacmanQLearningAgent -a epsilon=0.1

        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after these many episodes
        """
        args['epsilon'] = epsilon
        args['gamma'] = gamma
        args['alpha'] = alpha
        args['numTraining'] = numTraining
        self.index = 0  # This is always Pacman
        QLearningAgent.__init__(self, **args)

    # def __init__(self, index, timeForComputing, epsilon, gamma, alpha, numTraining):
    #     """
    #     These default parameters can be changed from the pacman.py command line.
    #     For example, to change the exploration rate, try:
    #         python pacman.py -p PacmanQLearningAgent -a epsilon=0.1
    #
    #     alpha    - learning rate
    #     epsilon  - exploration rate
    #     gamma    - discount factor
    #     numTraining - number of training episodes, i.e. no learning after these many episodes
    #     """
    #     # args['epsilon'] = epsilon
    #     # args['gamma'] = gamma
    #     # args['alpha'] = alpha
    #     # args['numTraining'] = numTraining
    #     self.index = 0  # This is always Pacman
    #     QLearningAgent.__init__(self, index, timeForComputing, epsilon, gamma, alpha, numTraining)

    def getAction(self, state):
        """
        Simply calls the getAction method of QLearningAgent and then
        informs parent of action for Pacman.  Do not change or remove this
        method.
        """
        action = QLearningAgent.getAction(self, state)
        while action.lower() == 'stop':
            action = random.choice(self.getLegalActions(state))
        self.doAction(state, action)
        # if self.index == 0:
        #     print(action)
        return action



class ApproximateQAgent(PacmanQAgent):
    """
       ApproximateQLearningAgent

       You should only have to overwrite getQValue
       and update.  All other QLearningAgent functions
       should work as is.
    """

    def __init__(self, extractor='IdentityExtractor', **args):
        self.featExtractor = IdentityExtractor()
        PacmanQAgent.__init__(self, **args)
        self.weights = util.Counter()

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        """
          Should return Q(state,action) = w * featureVector
          where * is the dotProduct operator
        """
        features = self.featExtractor.getFeatures(state, action, self)
        dotProd = sum(features[feat] * self.getWeights()[feat] for feat in features)
        return dotProd

    def update(self, state, action, nextState, reward):
        """
           Should update your weights based on transition
        """
        print("Current Food: ", self.getFood(state).asList())
        feat = self.featExtractor.getFeatures(state, action, self)
        diff = (reward + self.discount*self.getValue(nextState)) - self.getQValue(state, action)
        # print("Reward: ", reward)
        if diff != 0.0:
            for feature in feat:
                self.weights[feature] += self.alpha*diff*feat[feature]
                print("Diff: ", diff, ", Weight: ", self.getWeights()[feature])
        # print("Alpha: ", self.alpha, ", Gamma: ", self.discount, ", Learning rate: ", self.epsilon)

        return self.getWeights()

    def final(self, state):
        "Called at the end of each game."
        # call the super-class final method
        PacmanQAgent.final(self, state)
        with open('weights.txt', 'w') as f:
            for feature in self.getWeights():
                f.write(str(str(feature) + ": " + str(self.getWeights()[feature]) + "\n"))
        # did we finish training?
        if self.episodesSoFar == self.numTraining:
            print(self.getWeights())
            pass


class IdentityExtractor:
    def getFeatures(self, state, action, agent):
        """
            Get the feature values for a state/action pairs.
        """
        feats = util.Counter()
        successorGameState = agent.getSuccessor(state, action)
        foodList = agent.getFood(successorGameState).asList()
        agentState = state.getAgentState(agent.index).getPosition()
        dist, minDistFood = self.minDistToFoodCluster(state, agent, agentState, foodList)
        sizeOfCluster = self.sizeOfFoodCluster(minDistFood, foodList)
        if dist == 0:
            feats[(dist, sizeOfCluster)] = sizeOfCluster
        else:
            feats[(dist, sizeOfCluster)] = (1.0 / dist) * sizeOfCluster
        return feats

    def minDistToFoodCluster(self, state, agent, agentState, foodList):
        aStarRes = agent.aStarSearch(SearchFood(state, agent, agent.index), state, agent.manhattanHeuristic)
        # distToFood = min([(agent.getMazeDistance(state, food), food) for food in foodList])
        # distToFood = 100000
        # retFood = (0, 0)
        # for food in foodList:
        #     mazeDist = agent.getMazeDistance(state, food)
        #     if mazeDist < distToFood:
        #         distToFood = mazeDist
        #         retFood = food
        # return distToFood, retFood
        return len(aStarRes), tracePosMoves(agentState, aStarRes)


    def sizeOfFoodCluster(self, foodZero, foodList):
        clusterRadius = 3
        sizeOfCluster = len([food for food in foodList if util.manhattanDistance(foodZero, food) <= clusterRadius])
        return float(sizeOfCluster)


class NullAgent(CaptureAgent):
    '''
        A Null Agent to handle other agents required for training.
    '''
    def chooseAction(self, gameState):
        return 'Stop'

def tracePosMoves(pos, moves):
    for action in moves:
        action = action.lower()
        if action == 'west':
            pos = (pos[0] - 1, pos[1])
        elif action == 'east':
            pos = (pos[0] + 1, pos[1])
        elif action == 'north':
            pos = (pos[0], pos[1] + 1)
        elif action == 'south':
            pos = (pos[0], pos[1] - 1)
    return pos