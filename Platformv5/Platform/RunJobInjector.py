from Testing.JobInjector import JobInjector
from twisted.python.compat import raw_input                     ##added import


ji = JobInjector()
ji.run()
quit = raw_input("enter anything to quit")
ji.pm.terminate = True
