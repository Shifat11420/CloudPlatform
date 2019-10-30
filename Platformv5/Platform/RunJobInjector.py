from Testing.JobInjector import JobInjector


ji = JobInjector()
ji.run()
quit = raw_input("enter anything to quit")
ji.pm.terminate = True
