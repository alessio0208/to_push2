to_be_evaluated=$1

to_be_eval=${to_be_evaluated::-1}

number_sites="$(find ${to_be_eval}/ALL_INSTANCES_FOLD1/* -maxdepth 1 -type d | wc -l)"

echo $number_sites

for d in $to_be_eval/*; do
    aux="$(echo $d | rev | cut -d'_' -f1 | rev)"
    echo $aux
    foldNum=${aux:4}
      
    
    index_cluster=1
            
    for e in $d/*/*; do 
        cut -d " " -f 1- $e > temp
        awk -v x=$index_cluster '$1=x ' temp >> WSC_Eval_simple_TCP_${number_sites}S_50SP_15ISP_20IMP_${foldNum}.train

        index_cluster=$((index_cluster+1))              
    done 
    
    cat $d/mainPages_TCP >> WSC_Eval_simple_TCP_${number_sites}S_50SP_15ISP_20IMP_${foldNum}.train
    
done
  
rm temp
