EXPERIMT = Experiment.dat
MACHINES = MachinesClemsonUnbal.dat
LOGINPUT = CompleteLogInput.dat
PLATFORM = bpete16/distplatform:4.60
LOGFILES = v4log1

runonce:
	python3 RunExpSafeBareMetal.py ${MACHINES} ${EXPERIMT}

runmult:
	python3 RunExpBareMetal.py ${MACHINES} ${EXPERIMT}

parselogs:
	python3 CompleteLogParse.py ${LOGINPUT}

nodeusage:
	python3 ParseNodeUsageTime.py ${LOGFILES}/extra0/

platform:
	docker rmi `docker images -q` || true
	cd Platformv5; docker build -f Dockerfile -t ${PLATFORM} .
	cd Platformv5; docker save --output=plat.tar ${PLATFORM}
	docker rmi `docker images -q`

clean:
	rm -f Platformv5/plat.tar
	rm -rf __pycache__ *~
