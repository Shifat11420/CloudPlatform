EXPERIMT = Experiment.dat
MACHINES = MachinesClemsonUnbal.dat
LOGINPUT = CompleteLogInput.dat
PLATFORM = bpete16/distplatform:4.0
LOGFILES = log1
SPHINXOP = -H CloudPlatform -A 'S. Mithila, B. Peterson, G. Baumgartner'

runonce:
	python3.8 RunExpSafeBareMetal.py ${MACHINES} ${EXPERIMT}

runmult:
	python3.8 RunExpBareMetal.py ${MACHINES} ${EXPERIMT}

parselogs:
	python3.8 CompleteLogParse.py ${LOGINPUT}

nodeusage:
	python3.8 ParseNodeUsageTime.py ${LOGFILES}/extra0/

platform:
	docker rmi `docker images -q` || true
	cd Platformv5; docker build --network=host -f Dockerfile -t ${PLATFORM} .
	cd Platformv5; docker save --output=plat.tar ${PLATFORM}
	docker rmi `docker images -q`

# FIXME: This doesn't work yet.
# The code probably need to be ported to Python3 first, since I installed
# python3-sphinx.  When running sphinx-apidoc, it tries to import all
# Python files.  That doesn't seem to be working correctly, either
# imports work differently in Python 3, the modules hierarchy hasn't been
# constructed correctly, or sphinx-apidoc hasn't been set up right.
documentation:
	cd Platformv5; sphinx-apidoc -FMf ${SPHINXOP} -o Documentation Platform
	cd Platformv5/Documentation; make html

clean:
	rm -f Platformv5/plat.tar
	rm -rf __pycache__ *~

processclean:
	fuser -k 15000/tcp
	fuser -k 11100/tcp
	fuser -k 11101/tcp	
	fuser -k 11102/tcp
