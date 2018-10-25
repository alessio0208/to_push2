to_be_evaluated=$1

#get range 
cat 10folds/*1/*/*/* >> WSC_Eval_simple_TCP.merged
cat $to_be_evaluated/*1/mainPages_TCP >> WSC_Eval_simple_TCP.merged

./svm-scale -l -1 -u 1 -s WSC_Eval_simple_TCP.range WSC_Eval_simple_TCP.merged 


for d in $to_be_evaluated/*/*/*; do 
    ./svm-scale -l -1 -u 1 -r WSC_Eval_simple_TCP.range $d > ${d}_temp
    rm $d 
    mv ${d}_temp $d
done


for d in $to_be_evaluated/*/mainPages_TCP; do 
    ./svm-scale -l -1 -u 1 -r WSC_Eval_simple_TCP.range $d > ${d}_temp
    rm $d 
    mv ${d}_temp $d
done


#cp -r 10folds 10folds_only_testSet

#rm -r 10folds_only_testSet/*/*/train*

#for test in 10folds_only_testSet/*/*/*/*; do
 #   ./svm-scale -l -1 -u 1 -r WSC_Eval_simple_TCP.range $test > ${test}_temp
 #   rm $test
 #   mv ${test}_temp $test
#done       

#./svm-scale -l -1 -u 1 -r WSC_Eval_simple_TCP.range WSC_Eval_simple_TCP.merged > WSC_Eval_simple_TCP.merged.scaled

#svm-scale -l -1 -u 1 -r WSC_Eval_simple_TCP.range ciao.txt > ciao_temp


    



