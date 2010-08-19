credit=0
for ((round=1;round<=34;round++))
do
    ./main.py --predict $round < judge-data/$1/round$round > judge-data/$1/prediction$round
    ./main.py --verify $round < judge-data/$1/result$round
    ((credit+=`./judge judge-data/$1/prediction$round judge-data/$1/round$round --points`))
done
echo Total: $credit
