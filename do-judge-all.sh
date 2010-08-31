sum=0
for i in `seq 1 1`; do 
    sum=0
    for jahr in `seq 2004 2009`; do
	((e = `./do-judge.sh $jahr`))
	echo $jahr: $e
	((sum+=e))
    done;
    echo Summe: $sum
    echo "----"; 
done;
