from threading import Lock

class JobLock():
    def __init__(self):
        self.ilock = Lock()
        self.inclu_lockers = []
        self.exclu_locker = ""

    def is_there_a_lock(self, anid):
        if(anid in self.inclu_lockers):
            return True
        return False
        
    def incllock(self, anid):
        rval = False
        self.ilock.acquire()
        if(self.exclu_locker == ""):
            self.inclu_lockers.append(anid)
            rval = True
        self.ilock.release()
        return rval

    def excllock(self, anid):
        rval = False
        self.ilock.acquire()
        if(self.exclu_locker == ""):
            if(len(self.inclu_lockers) == 0):
                rval = True
                self.exclu_locker = anid
        self.ilock.release()
        return rval

    def inclrel(self, anid):
        self.ilock.acquire()
        self.inclu_lockers.remove(anid)
        self.ilock.release()

    def exclrel(self, anid):
        self.ilock.acquire()
        self.exclu_locker = ""
        self.ilock.release()
