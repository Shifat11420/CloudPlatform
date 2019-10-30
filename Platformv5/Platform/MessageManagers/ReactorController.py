import threading

class ReactorController():

    def __init__(self, context):
        self.context = context
        self.reactors = []
        self.thrlock = threading.Lock()
        
    def AddReactor(self, newReactor):
        with self.thrlock:
            self.reactors.append(newReactor)

    def RemoveReactor(self, aReactor):
        with self.thrlock:
            self.reactors.remove(aReactor)

    def ReactorsObserve(self, aline):
        reactorsToUse = []
        with self.thrlock:
            reactorsToUse = list(self.reactors)
        for areactor in reactorsToUse:
            areactor.observer(aline)
    
