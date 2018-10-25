wc="$(wc -l *.result)"
num_all_results="$(echo $wc | cut -d" " -f 1)"
echo $num_all_results

num_results_each_fold=$((num_all_results/10))

echo $num_results_each_fold
for i in {1..10}; do 
    touch result_fold${i}
done 

printLine() 
{ 
  sed -n -e "$1p" "$2"
}

start=1
counter=1

for fold in {1..10}; do 
   
   end=$((num_results_each_fold*counter))
   echo $start,$end
   printLine ${start},${end} WSC_Eval_simple_TCP.result > result_fold${fold}
   start=$((start + num_results_each_fold))
   counter=$((counter+1))
done


for fold in {1..10}; do
  #foldNum="$(echo $fold | cut -d'_' -f2)"
   
   
  while read line; do
      predicted_label_cluster="$(echo $line | cut -d',' -f1)" 
      real_label_site="$(echo $line | cut -d',' -f2)"
     # echo $fold  $num_clusters_${foldNum}
      cluster_corresponding_site="$(grep -n " $predicted_label_cluster " num_clusters_fold${fold} | cut -d: -f1)"
      echo "$cluster_corresponding_site,$real_label_site" >> FINAL_RESULT

  done < result_fold${fold}
done


