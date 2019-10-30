#!/bin/bash

./Nas/NPB3.3.1/NPB3.3-SER/bin/bt.S.x > Nas/rawout/bt_out.txt
./Nas/NPB3.3.1/NPB3.3-SER/bin/cg.S.x > Nas/rawout/cg_out.txt
./Nas/NPB3.3.1/NPB3.3-SER/bin/dc.S.x > Nas/rawout/dc_out.txt
./Nas/NPB3.3.1/NPB3.3-SER/bin/ep.S.x > Nas/rawout/ep_out.txt
./Nas/NPB3.3.1/NPB3.3-SER/bin/ft.S.x > Nas/rawout/ft_out.txt
./Nas/NPB3.3.1/NPB3.3-SER/bin/is.S.x > Nas/rawout/is_out.txt
./Nas/NPB3.3.1/NPB3.3-SER/bin/lu.S.x > Nas/rawout/lu_out.txt
./Nas/NPB3.3.1/NPB3.3-SER/bin/mg.S.x > Nas/rawout/mg_out.txt
./Nas/NPB3.3.1/NPB3.3-SER/bin/sp.S.x > Nas/rawout/sp_out.txt
./Nas/NPB3.3.1/NPB3.3-SER/bin/ua.S.x > Nas/rawout/ua_out.txt

python Nas/parseOutput.py
