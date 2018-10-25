dataset=$1

for c in $dataset/*; do
  prev_total=0
  aux="$(echo $c | rev | cut -d_ -f1 | rev)"
  foldNum="$(echo $aux | cut -c 5-)"


  echo $foldNum
  for d in $c/*;do 
    if [[ -d $d ]]; then  
      numFiles_currentDir="$( ls $d | wc -l)"
         
      current_total=$((prev_total + numFiles_currentDir))
      
      # echo $current_total
      i=$((prev_total + 1))
      counter=0
      
      array=()      
      while [[ $i -le $current_total ]]; do 
          array[$counter]=$i
          
          i=$((i+1))
          counter=$((counter+1))
      done
             
      echo " ${array[*]} " >> num_clusters_fold${foldNum}      
      prev_total=$current_total      
    fi
  done
     
done
