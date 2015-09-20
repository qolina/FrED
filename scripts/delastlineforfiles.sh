for i in `ls $1`
do
    file=$1$i
    num=`grep -n "" $file | wc -l`
    let "num -=1" # do calculation
    echo $i $num `tail -n 1 $file`
    `head -n $num $file > $file.o`
    `rm $file`
done
