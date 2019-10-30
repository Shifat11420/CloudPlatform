
    def AddTGJob(self, ajob):
        with self.lock_tgjobq:
            tg_jobqueue.append(ajob)

    def RespAcceptLeader(self, newleaderip, newleaderport):
        resp = None
        with self.lock_leader:
            if(self.tgleaderip == ""):
                self.tgleaderip = newleaderip
                self.tgleaderport = newleaderport
                resp = NewLeaderAcceptMG(self)
            else:
                resp = NewLeaderRejectMG(self)

        return resp

    def ReleaseFromGroup(self):
        with self.lock_leader:
            self.tgleaderip = ""
            self.tgleaderport = 0

    def StartRecievingTaskGraph(self, aStartMsg):
        ntg = TaskGraph(aStartMsg)
        self.taskgraphincoming[ntg.idval] = ntg
        
    def MidRecieveTaskGraph(self, aTGMsg):
        #thinking about this.
        pass
    
        
    def ReceiveTGOblig(self, obligid, obligval):
        for i in range(len(self.tgjobqueue)):
            ajob = self.tgjobqueue[i]
