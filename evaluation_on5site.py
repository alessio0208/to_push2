import numpy as np
import glob
import os
import math
import sys
import shutil
from collections import Counter


current_directory = os.path.dirname(os.path.abspath(__file__))
path= current_directory + '/FOLD1_train'

partial_results= [['0,0,0,0' for x in xrange(100)] for x in xrange(15)]


list_dirs=[x[0] for x in os.walk(path)]
list_dirs.pop(0)


site_num=1
for d in sorted(list_dirs):

   list_files = os.listdir(d)
   number_files_in_dir = len(list_files)
   print number_files_in_dir
   total_positive=[0 for x in xrange(1000)]
   tot_pos_index=0
 
   for f in os.listdir(d):
     site_results= [[0 for x in xrange(100)] for x in xrange(15)]
     distance=[[0 for x in xrange(100)] for x in xrange(15)]
     
     for instance in xrange(0,15):
        file = open(path+'/'+f, 'r')
        lines = file.readlines()
        five_sites = lines[instance:-1:15]

        j=0   
             
        for page in five_sites:
            #print j/5             
            if ',' in page:              
                site_results[instance][j/5]+=1
                page_arr = page.split(",") 
                distance[instance][j/5]= distance[instance][j/5] + float(page_arr[3])
                total_positive[tot_pos_index]+=1
           
            j+=1
        
        for k in xrange(0,100): 
           if site_results[instance][k] !=0:
              distance[instance][k]= float(distance[instance][k]) / float(site_results[instance][k])
     
     print total_positive[tot_pos_index]
     for instance in xrange(0,15):
        for k in xrange(0,100): 
            res_arr = partial_results[instance][k].split(",")
            #print res_arr 
            
            #print str(site_results[i][k]) + " " + str(res_arr[1])
            if int(site_results[instance][k])>int(res_arr[1]):
                  partial_results[instance][k]= str(site_num) + "," +str(site_results[instance][k]) +"," + str(distance[instance][k]) + "," +str(total_positive[tot_pos_index])
                  print partial_results[instance][k]

            if int(site_results[instance][k]) == int(res_arr[1]):
              #if k+1==site_num:
              if total_positive[tot_pos_index]< float(res_arr[3]):
              #if distance[instance][k] < float(res_arr[2]):
                  partial_results[instance][k]= str(site_num) + "," +str(site_results[instance][k]) +"," + str(distance[instance][k]) + ","+str(total_positive[tot_pos_index])
     
     tot_pos_index+=1          
   site_num+=1      



partial_results=[list(a) for a in zip(*partial_results)]

print (partial_results)
with open('results_5pages', 'w') as f:
      for i in xrange(0,100):
       for j in xrange(0,5): 
          for k in xrange(0,15):

            temp=partial_results[i][k].split(",")
       #    print temp[0], " ", temp[1]
            f.write(temp[0]+","+ str(i+1)+ "\n")

