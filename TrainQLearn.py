from captureAgents import CaptureAgent

from qlearningAgent import ApproximateQAgent
import layout
from captureTRAINING import randomLayout, runGames

class TrainQLearn:
    def __init__(self):
        self.running = True

    def generateFoodMazes(self, numGames):
        '''
            This code is adapted from capture.py and mazeGenerator.py. It is mostly borrowed and not mine.
        '''
        layouts = []
        for i in range(numGames):
            l = layout.Layout(randomLayout().split('\n'))
            if l is None:
                raise Exception("The layout cannot be generated")
            layouts.append(l)
        return layouts

    def runTraining(self):
        numGames = 100
        numTraining = numGames
        epsilon = 0.05
        gamma = 0.8
        alpha = 0.1
        index = 0
        timeForComputing = 0
        numTraining = numTraining
        # Set time for computing to 0
        nullAgent1 = NullAgent(1)
        nullAgent2 = NullAgent(2)
        nullAgent3 = NullAgent(3)
        approxQLearnAgent = ApproximateQAgent(index, timeForComputing, epsilon, alpha, gamma, numTraining)
        agents = [approxQLearnAgent]
        layouts = self.generateFoodMazes(numGames)

        # Set display to null because numTraining = numGames so it will never be invoked
        # length set to default 1200. Could shorten for more incentive.
        # Num games set to 1000 initially, will configure more.
        # runGames(layouts, agents, display, length, numGames, record, numTraining, redTeamName, blueTeamName,
        #              muteAgents=False, catchExceptions=False, delay_step=0):
        runGames(layouts, agents, None, 10000, numTraining, False, numTraining, 'Red', 'Blue')


class NullAgent(CaptureAgent):
    '''
        A Null Agent to handle other agents required for training.
    '''
    def chooseAction(self, gameState):
        return 'Stop'


trainQLearn = TrainQLearn()
trainQLearn.runTraining()