from Testing.ServerKiller import ServerKiller
import sys

if(len(sys.argv) < 3):
    print "Bad Args"
else:
    sk = ServerKiller(sys.argv[1], sys.argv[2])
    sk.run()
    quit = raw_input("enter anything to quit")
    sk.pm.terminate = True
