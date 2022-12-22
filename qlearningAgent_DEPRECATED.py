# qlearningAgent_DEPRECATED.py
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

import random
import util
from myTeam import ReflexCaptureAgent


class QLearningAgent(ReflexCaptureAgent):
    """
      Q-Learning Agent

      Functions you should use
        - self.getLegalActions(state)
          which returns legal actions for a state
    """

    def __init__(self, index, epsilon, alpha, discount):
        super().__init__(index)
        self.epsilon = epsilon
        self.alpha = alpha
        self.discount = discount
        self.qValues = util.Counter()
        self.index

    def getQValue(self, state, action):
        return float(self.qValues[(state, action)])

    def computeValueFromQValues(self, gameState):
        """
          Returns max_action Q(state,action)
        """
        qValues = []
        for action in gameState.getLegalActions(self.index):
            qValues.append((self.getQValue(gameState.getAgentState(self.index), action), action))
        if len(qValues):
            return max(qValues)[0]
        else:
            return 0.0

    def computeActionFromQValues(self, gameState):
        """
          Compute the best action to take in a state.
        """
        qValues = []
        for action in gameState.getLegalActions(self.index):
            qValues.append((self.getQValue(gameState.getAgentState(self.index), action), action))
        if len(qValues):
            return max(qValues)[1]
        else:
            return None

    def getAction(self, gameState):
        """
          Compute the action to take in the current state.  Random actions are chosen with probability epsilon
        """
        legalActions = gameState.getLegalActions(self.index)
        action = None
        if len(legalActions):
            if util.flipCoin(self.epsilon):
                action = random.choice(legalActions)
            else:
                action = self.getPolicy(gameState)
        return action

    # def update(self, gameState, action, reward):
    #     """
    #       Updating Q values without features or weights.
    #     """
    #     state = gameState.getAgentState(self.index)
    #     nextState = self.getSuccessor(gameState, action)
    #     qval = self.getQValue(state, action) + self.alpha * (
    #             (reward + self.discount * self.getValue(nextState)) - self.getQValue(state, action))
    #     self.qValues[(state, action)] = qval
    #     return qval

    def getPolicy(self, gameState):
        return self.computeActionFromQValues(gameState)

    def getValue(self, gameState):
        return self.computeValueFromQValues(gameState)


class PacmanQAgent(QLearningAgent):
    "Exactly the same as QLearningAgent, but with different default parameters"

    def __init__(self, index, epsilon, alpha, discount, numTraining=0):
        self.index = 0  # This is always Pacman
        self.numTraining = numTraining
        QLearningAgent.__init__(self, index, epsilon, alpha, discount)

    # def getAction(self, state):
    #     """
    #
    #     """
    #     action = QLearningAgent.getAction(self, state)
    #     self.doAction(state, action)
    #     return action


class ApproximateQAgent(PacmanQAgent):
    """
       ApproximateQLearningAgent

    """

    def __init__(self, index, epsilon, alpha, discount):
        self.featExtractor = IdentityExtractor
        PacmanQAgent.__init__(self, index, epsilon, alpha, discount)
        self.weights = util.Counter()
        self.openWeights()

    def getWeights(self):
        return self.weights

    def openWeights(self):
        try:
            with open('weightsLARGE.txt', 'r') as f:
                for line in f:
                    entry = line.split(",")
                    self.weights[entry[0]] = entry[1]
        except:
            pass

    def saveWeights(self):
        with open('weightsLARGE.txt', 'w') as f:
            writeStr = ""
            for weight in self.getWeights():
                writeStr += (weight[0],",",weight[1],"\n")
            f.write(writeStr)

    def getQValue(self, state, action):
        """
          Returns weights for features.
        """
        features = self.featExtractor.getFeatures(state, action, self)
        dotProd = sum(features[feat] * self.getWeights()[feat] for feat in features)
        return dotProd

    def update(self, gameState, action):
        """
          Updates weights based on Q Value.
        """
        if self.taken >= 8:
            gameState.gameOver = True
            self.saveWeights()
        reward = 0
        if self.getSuccessor(gameState, action).getAgentState(self.index) in self.getFood(gameState):
            reward += 10
        state = gameState.getAgentState(self.index)
        nextState = self.getSuccessor(gameState, action)
        feat = self.featExtractor.getFeatures(gameState, action, self)
        diff = (reward + self.discount * self.getValue(nextState)) - self.getQValue(state, action)
        for feature in feat:
            self.weights[feature] += self.alpha * diff * feat[feature]
        return self.getWeights()

    def computeActionFromQValues(self, gameState):
        """
          Compute the best action to take in a state. Also update the Q Value for each time the action is evaluated.
        """
        qValues = []
        for action in gameState.getLegalActions(self.index):
            qValues.append((self.getQValue(gameState.getAgentState(self.index), action), action))
        if len(qValues):
            action = max(qValues)[1]
            self.update(gameState, action)
            return action
        else:
            return None
    # def final(self, state):
    #     PacmanQAgent.final(self, state)
    #     if self.episodesSoFar == self.numTraining:
    #         with open('readme.txt', 'w') as f:
    #             for feature in self.getWeights():
    #                 f.write(str(feature + ": " + str(weight) + "\n"))


class IdentityExtractor:
    def getFeatures(self, gameState, action, agent):
        feats = util.Counter()
        dist, minDistFood = self.minDistToFoodCluster(gameState, action, agent)
        sizeOfCluster = self.sizeOfFoodCluster(gameState, minDistFood, agent)
        feats[(gameState.getAgentState(agent.index), action)] = (1.0/dist) * sizeOfCluster
        return feats

    def minDistToFoodCluster(self, gameState, action, agent):
        nextAgentState = agent.getSuccessor(gameState, action).getAgentState(agent.index)
        foodList = agent.getFood(gameState).asList()
        distsForFood = [(util.manhattanDistance(nextAgentState, food), food) for food in foodList]
        return min(distsForFood)

    def sizeOfFoodCluster(self, gameState, foodZero, agent):
        clusterRadius = 3
        foodList = agent.getFood(gameState).asList()
        sizeOfCluster = len([food for food in foodList if util.manhattanDistance(foodZero, food) <= clusterRadius])
        return sizeOfCluster


