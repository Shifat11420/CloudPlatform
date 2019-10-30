#!/bin/bash

nextclass=false
nextbench=false
class="S,W,A"
bench="ft,mg,sp,lu,bt,is,cg,ua,ep"

for va in "$@"
do
    if [ "$nextclass" == true ]
	then
	class=$va
	nextclass=false
    fi
    if [ "$nextbench" == true ]
	then
	bench=$va
	nextbench=false
    fi
    if [ "$va" == "--class" ]
	then
	nextclass=true
    fi
    if [ "$va" == "--bench" ]
	then
	nextbench=true
    fi
done

classarr=(${class//,/ })
bencharr=(${bench//,/ })

for i in "${classarr[@]}"
do
    for j in "${bencharr[@]}"
    do
	./Nas/NPB3.3.1/NPB3.3-SER/bin/"$j"."$i".x > Nas/rawout/"$i"_"$j"_out.txt
    done
done

python Nas/parseOutput.py
