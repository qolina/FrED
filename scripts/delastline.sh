# delete last line of a given file

num=`grep -n "" $1 | wc -l`
let "num -=1" # do calculation
echo $num `tail -n 1 $1`
`head -n $num $1 > $1.o`
#`rm $1`
