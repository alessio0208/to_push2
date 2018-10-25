for iter_num in {1..10};do 
 for var in FOLD${iter_num}*/*.train; do

  wc="$(wc -l $var)"
  num_instances="$(echo $wc | cut -d" " -f 1)"

  size_background=$((num_instances/2))

  echo $size_background
  head -n $size_background $var > background
 
  for k in {2..105}; do
      awk -v k="$k" -v s="$size_background" -F ":" '/1/ {sum += $k} END {print sum/s}' background >> ${var}.centroid
  done
 done
done
