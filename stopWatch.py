import time
class stopwatch:
    def __init__(self):
        self.start = time.time()
        self.total = None
        
    def elapsedTime(self):
        return time.time() - self.start 
    
    def stop(self):
        self.total = time.time() - self.start

