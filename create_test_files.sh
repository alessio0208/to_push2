for d in 10folds/fold*; do
    
    aux="$(echo $d | rev | cut -d'/' -f 1 | rev)"  
    foldNum="$(echo $aux | cut -c 5-)"
    
    echo "fold " $foldNum
    siteNum=1  
    for e in $d/*/test*;do 
        
        for f in $e/*; do 
          cut -d " " -f 1- $f > temp
          awk -v x=$siteNum '$1=x ' temp >> WSC_Eval_simple_TCP_100S_50SP_15ISP_20IMP_${foldNum}.test
          rm temp          
        done

        siteNum=$((siteNum+1))
    done
    
    foldNum=$((foldNum+1))
done

