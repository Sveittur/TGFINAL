from stopWatch import stopwatch
from Objects import GameObject, Point
import random
class aimbots:
    def __init__(self):
        self.active = False
        self.stopwatch = None
        self.killCount = None
        self.time = None
        self.dir = "right"

    def startChallenge(self):
        self.active = True
        self.time = 0
        self.killCount = 0
        self.stopwatch = stopwatch()

    def stopChallenge(self):
        self.stopwatch.stop()
        self.time = self.stopwatch.total
        self.active = False

    def checkWin(self):
        return self.time < 21

class flickGame:
    def __init__(self):
        self.active = False
        self.stopwatch = None
        self.killCount = None
        self.time = None
        self.circle = GameObject(Point(0,2.5,-0.55), Point(1,1,1))
       

    
    def updateCircle(self):
        self.circle.position.x = random.uniform(-9,9)
        self.circle.position.y = random.uniform(0 , 4.5)
        self.circle.update()

    def startChallenge(self):
        self.active = True
        self.time = 0
        self.killCount = 0
        self.stopwatch = stopwatch()

    def stopChallenge(self):
        self.stopwatch.stop()
        self.time = self.stopwatch.total
        self.active = False

    def checkWin(self):
        return self.time < 41