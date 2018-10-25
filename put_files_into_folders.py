import numpy as np
import glob
import os
import math
import sys
import shutil
from scipy.spatial import distance
from numpy  import array


for iter_num in xrange(1,2):
 current_directory = os.path.dirname(os.path.abspath(__file__))
 path= current_directory  
 previous_site="" 
 for f in sorted(os.listdir(path)):
    
   if f.endswith(".distance"):

      distance_file_arr=f.split("_") 
      current_site=distance_file_arr[-2]
      site_dir=path + '/'+ current_site 
     
      if current_site != previous_site:
          os.makedirs(site_dir)
          previous_site=current_site
          shutil.copy(path+'/'+f, site_dir)
      
      else:
         shutil.copy(path+'/'+f, site_dir)
      

 list_dirs=[x[0] for x in os.walk(path)]
 list_dirs.pop(0)
 print list_dirs
