
workFolder=${PWD}

PDFs=( $(seq 303000 303001) )
echo ${PDFs[@]}
for pdf in  ${PDFs[@]}; do
	# "y\ny\n11\n" y- change seeds, y- sure, stage 11, 12, 13, 14, 15, 2, 31
	# if stage is 11, the first two yes are not necessary
	# python submit_handler.py N-jobs, path ttbarj, mass top, LHA PDF NUMBER, muR factor, muF factor
	echo "11" | python submit_handler.py 10 ../POWHEG-BOX-V2/ttbarj/ 172.5 ${pdf} 1.0 1.0
	cd ${workFolder}
done
