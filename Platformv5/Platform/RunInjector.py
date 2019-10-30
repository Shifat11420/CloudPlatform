from Injectors.InjectorFactory import BuildInjector
import sys

if(len(sys.argv) > 1):
    afilename = sys.argv[1]
    inj = BuildInjector(afilename)
    if not inj is None:
        inj.run()
        quit = raw_input("Enter anything to quit")
        inj.pm.terminate = True
    else:
        print "No Injector"
else:
    print "Bad Args"
