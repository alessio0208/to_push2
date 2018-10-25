import numpy as np
import glob
import os
import math
import sys
import shutil
from scipy.spatial import distance
from numpy  import array


for iter_num in xrange(10,11):
 current_directory = os.path.dirname(os.path.abspath(__file__))
 path= current_directory + '/FOLD' +str(iter_num) + '_train'

 for f in os.listdir(path):
   
    
   if f.endswith(".predict"):

      i=0
      cluster_name=f[:-8] 
      distance_file = path +'/'+cluster_name+ '.distance' 
     
      centroid_file=open(path+'/'+cluster_name +'.centroid', 'r')
      centroid_arr = centroid_file.readlines() 
      # print np.shape(centroid_arr)  
      # print f
      print centroid_file

      for feature_centroid in xrange(0, 104):
         centroid_arr[feature_centroid]=float(centroid_arr[feature_centroid][:-1])
     
      #print centroid_arr    
      file = open(path+'/'+f, 'r')  

      for line in file: 
         line_arr = line.split(",")
         predicted_label = line_arr[0]
         real_label= line_arr[1]

         dist_euclidean=0
        
         if predicted_label != "-1":
            f=open(current_directory+'/WSC_Eval_simple_TCP_100S_50SP_15ISP_20IMP_'+str(iter_num)+'.test')
            lines=f.readlines()
            inst=lines[i]
            
            inst_arr= inst.split(":")
             
            inst_arr.pop(0)
            #print np.shape(centroid_arr)  
            for feature in xrange(0, 103):
                sep = ' '
                inst_arr[feature] = float(inst_arr[feature].split(sep, 1)[0])
            
            inst_arr[103]=float(inst_arr[103][:-1])

            #print inst_arr   
            partial=0
            for feature in xrange(0, 104):
                partial+=(inst_arr[feature]-centroid_arr[feature])**2
          
            euclidean_dist=math.sqrt(partial)    
            
            with open(distance_file, "a") as myfile:
                 line=line[:-1]
                 myfile.write(line + ','+str(euclidean_dist) + '\n')                           
            
        
         else:
            with open(distance_file, "a") as myfile:
                 myfile.write('-\n')            

            
         i+=1

      centroid_file.close()
      file.close()
    
         
   
      
           
         








            
            
