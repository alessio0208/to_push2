#!/usr/bin/env python

# easy.py adaption for k-fold evaluation of WSC with independent testing and training
# Splits websites into k-partitions and uses k-1 partitions for training and k for testing 
# Perform k-fold evaluation
# 	performs grid.py (internal k-fold CV) on each fold's training data to find parameters
# 	trains a model with the best parameters for each fold's training data
# 	use each fold's testing data to predict the results with the corresponding model
# Merge prediction results of all k-folds into a single result
#
# each wsc_file has to have a different label for each page: 1..n

# you should have a non-patched (no prediction output) svm-train executable as svm-train-q
# svm-predict and grid.py have to be patched

from __future__ import division # for division
from subprocess import *
from datetime import datetime
import sys, os, random, glob, multiprocessing
try:
    from natsort import natsorted
except:
	print('You need natsort! (pip install natsort)')
	sys.exit()
try:
	import tldextract
except:
	print('You need tldextract! (pip install tldextract)')
	sys.exit()

def exit_with_help(error=''):
    print("""\

Notes:
 - Main Pages are stored with the Filename "mainPages_{Format}" with Closed-world Numbering in the same order as the Websites are stored.
 - When no amount of background instances is specified, maximum suitable amount is chosen.
 - The script tries to resume grid-search if the output file already exists. 
 """)
    print(error)
    sys.exit(1)

#Info:
# - Add Pass-through option for svm-train & Co ? (Breaks argument checking)

# Define formats
formats = [ 'TCP' ]

inputpath = ''
# Arguments to be read from WFP_conf
args = [ ('inputpath', 'dir_EVAL_INPUT', 'in'),
         ('outputpath', 'dir_EVAL_OUTPUT', 'out'),
         ('svmpath', 'dir_EVAL_LIBSVM', 'svm') ]

# Checking if all variables are/will be set
for var, env, arg in args:
    if not '-'+arg in sys.argv:
        vars()[var] = os.getenv(env)
        if vars()[var] == None:
            exit_with_help('Error: Environmental Variables or Argument'+
                        ' insufficiently set! ($'+env+' / "-'+arg+'")')

# Setting default values
inputpath = inputpath + 'wsc_features/'
outputname = 'WSC_Eval'
bg_name = ''
scenario = ''
storage = 'Low'
form = 'TCP'
setting = 'CW'
limitPage = False; limitMainPage = False; limitBackground = False; limitSite = False; limitSites = False
perPage = -1; perMainPage = -1; bg_size = -1; perSite = -1;
quiet = False

global grid_option 
grid_option= ' '

# init values
tmp1 = None; tmp2 = None; tmp3a = None; tmp3b = None; tmp4 = None; tmp5 = None; tmp6 = None; tmp7 = None; tmp8 = None
gnuplot_exe = None

# Read parameters from command line call
if len(sys.argv) != 0:
    i = 0
    options = sys.argv[1:]
    # iterate through parameter
    while i < len(options):
        if options[i] == '-in':
                i = i + 1
                inputpath = options[i]
        elif options[i] == '-out':
                i = i + 1
                outputpath = options[i]
        elif options[i] == '-name':
                i = i + 1
                outputname=options[i]
        elif options[i] == '-storage':
                i = i + 1
                storage=options[i]
        elif options[i] == '-q':
                quiet = True
        elif options[i] == '-format':
                i = i + 1
                form=options[i]
        elif options[i] == '-mainpages':
                i = i + 1
                tmp1 = options[i]
        elif options[i] == '-quickCV':
                i = i + 1
                tmp2 = options[i]
        elif options[i] == '-randomInstances':
                i = i + 1
                tmp3a = options[i]
        elif options[i] == '-randomSubpages':
                i = i + 1
                tmp3b = options[i]
        elif options[i] == '-setting':
                i = i + 1
                setting = options[i]
        elif options[i] == '-simple':
                i = i + 1
                tmp4 = options[i]
        elif options[i] == '-background':
                i = i + 1
                bg_name = options[i]
        elif options[i] == '-separateEvaluation':
                i = i + 1
                tmp5 = options[i]
        elif options[i] == '-limitWebsites':
                i = i + 1
                limitSites = True
                websitesIndex = map(int, options[i].split(','))
        elif options[i] == '-limitInstances':
                i = i + 1
                tmp6 = options[i]
        elif options[i] == '-limitSubpages':
                i = i + 1
                perSite = int(options[i])
        elif options[i] == '-svm':
                i = i + 1
                svmpath = options[i]
        elif options[i] == '-gnuplot':
                i = i + 1
                gnuplot_exe = options[i]
        elif options[i] == '-log2g':
                i = i + 1
                grid_option = grid_option + ' -log2g ' + options[i]
        elif options[i] == '-log2c':
                i = i + 1
                grid_option = grid_option + ' -log2c ' + options[i]
        elif options[i] == '-v':
                i = i + 1
                tmp7 = options[i]
                grid_option = grid_option + ' -v ' + options[i]
        elif options[i] == '-worker':
                i = i + 1
                tmp8 = options[i]
                grid_option = grid_option + ' -worker ' + options[i]
        else:
            exit_with_help('Error: Unknown Argument! ('+ options[i] + ')')
        i = i + 1


# Check set variables
if not os.path.isdir(inputpath):
    exit_with_help('Error: Invalid Input Path!')
if not os.path.isdir(outputpath):
    os.mkdir(outputpath)
# Remove "Name" in Output directory?
if storage not in [ 'Low', 'RemoveTemp', 'High' ]:
    exit_with_help('Error: Unknown Storage Option!')
if form not in formats:
    exit_with_help('Error: Unknown Format!')
if tmp1 in [ 'YES', 'NO' ] or tmp1 == None:
    if tmp1 == 'NO':
        main = False
    else:
        main = True
     #   if not os.path.isfile(inputpath+'mainPages_'+form):
      #      exit_with_help('Error: Invalid Main Pages Files!')
else:
    exit_with_help('Error: Unknown Main Page Option!')
if tmp2 in [ 'YES', 'NO' ] or tmp2 == None:
    if tmp2 == 'NO':
        quick = False
    else:
        quick = True
else:
    exit_with_help('Error: Unknown Quick CV Option!')
if tmp3a in [ 'YES', 'NO' ] or tmp3a == None:
    if tmp3a == 'YES':
        shuffleInstances = True
    else:
        shuffleInstances = False
if tmp3b in [ 'YES', 'NO' ] or tmp3b == None:
    if tmp3b == 'YES':
        shuffleSubpages = True
    else:
        shuffleSubpages = False
else:
    exit_with_help('Error: Unknown Random Option!')
if setting not in [ 'CW', 'OW' ]:
    exit_with_help('Error: Unknown Setting!')
if tmp4 in [ 'YES', 'NO' ] or tmp4 == None:
    if tmp4 == 'NO':
        simple = False
    else:
        simple = True
else:
    exit_with_help('Error: Unknown Simple Option!')
if setting == 'OW':
    if bg_name == '':
        exit_with_help('Error: No Background File Set!')
    if not os.path.isfile(inputpath+bg_name+'_'+form):
        exit_with_help('Error: Invalid Background File!')
    bg_domain_file = 'list_' + bg_name[0].lower() + bg_name[1:] + '_' + form + '.txt'
    if not os.path.isfile(inputpath+bg_domain_file):
        exit_with_help('Error: Invalid Domain-Background File!')
else:
    if bg_name != '':
        exit_with_help('Error: Background File Set in Closed-world Scenario!')
if tmp5 in [ 'YES', 'NO' ] or tmp5 == None:
    if tmp5 == 'YES':
        if setting == 'OW':
            separateEval = True
        else:
            exit_with_help('Error: Separate Evaluation is only meaningful in Open-world Scenario!')
    else:
        separateEval = False
else:
    exit_with_help('Error: Unknown Separate Evaluation Option!')
if tmp6 != None:
    perPage, perMainPage, bg_size = map(int,tmp6.split(','))
if not os.path.isdir(svmpath):
    exit_with_help('Error: Invalid LibSVM Path!')
else:
	svmscale_exe = os.path.join(svmpath, 'svm-scale')
	svmtrain_exe_q = os.path.join(svmpath, 'svm-train-q')
	svmpredict_exe = os.path.join(svmpath, 'svm-predict')
	grid_py = os.path.join(svmpath, './tools/grid_patched.py')
	if gnuplot_exe == None:
		gnuplot_exe = "/usr/bin/gnuplot"
		if not os.path.exists(gnuplot_exe):
			gnuplot_exe = None
	else:
		assert os.path.exists(gnuplot_exe),"gnuplot executable not found"
	assert os.path.exists(svmscale_exe),"svm-scale executable not found"
	assert os.path.exists(svmtrain_exe_q),"svm-train executable not found"
	assert os.path.exists(svmpredict_exe),"svm-predict executable not found"
	assert os.path.exists(grid_py),"grid_patched.py not found"
if tmp7 == None or tmp7.isdigit():
    if tmp7 == None:
        folds = 10
    elif int(tmp7) > 0:
        folds = int(tmp7)
    else:
        exit_with_help('Error: Number of Folds is not a valid Number!')
else:
    exit_with_help('Error: Number of Folds is not a Number!')
if tmp8 == None or tmp8.isdigit():
    if tmp8 == None:
        nr_worker = multiprocessing.cpu_count()
    elif int(tmp8) > 0:
        nr_worker = int(tmp8)
    else:
        exit_with_help('Error: Number of Workers is not a valid Number!')
else:
    exit_with_help('Error: Number of Workers is not a Number!')


# Additional checks
if setting == 'OW':
    openworld = True
else:
    openworld = False
if simple:
    scenario = scenario + '_simple'
if perPage > -1:
    limitPage = True
if perMainPage > -1:
    limitMainPage = True
if bg_size > -1 and openworld:
    limitBackground = True
if perSite > -1:
    limitSite = True
scenario = scenario + '_' + form


def evaluation(grid_option):
    for trainFold in os.listdir(outputpath):
      
      
         
      if trainFold.endswith("_train"):
        
        print trainFold  
        train_fold=os.path.join(outputpath, trainFold)
  
	for currentTrainFile in os.listdir(train_fold):
               
                print grid_option
     		training_file = os.path.join(train_fold, currentTrainFile)
		model_file = os.path.join(train_fold, currentTrainFile + '.model')
		
                status_file = os.path.join(train_fold, outputname + scenario + '.out')
	        gnuplot_file = os.path.join(train_fold, outputname + scenario + '.png')
			
			# CV for each fold of each
				# check if we can resume
                if os.path.isfile(status_file):
			grid_option_current = grid_option + ' -resume "{0}" -out "{0}" -png "{1}" '.format(status_file, gnuplot_file)
		else:
			grid_option_current = grid_option + ' -out "{0}" -png "{1}" '.format(status_file, gnuplot_file)

		
                cmd = 'python {0}  -svmtrain "{1}" -gnuplot "{2}" {3} "{4}"'.format(grid_py, svmtrain_exe_q, gnuplot_exe, grid_option_current, training_file)

                #print cmd 
                f = Popen(cmd, shell = True, stdout = PIPE).stdout
 
                line = ''
                while True:
	              last_line = line
                      line = f.readline()
	              if not line: break
                c,g,rate = map(float,last_line.split())


		# train model for each fold
                cmd = '{0} -c {1} -g {2} "{3}" "{4}"'.format(svmtrain_exe_q, c, g, training_file, model_file)


                		
		if not quiet:
			print('[' + str(datetime.now()).split('.')[0] + '] Fold: {0:>3} - Training...'.format(currentTrainFile))
		Popen(cmd, shell = True, stdout = PIPE).communicate()
                
               
                head, sep, tail = trainFold.partition('_')
                currentFoldNum= head.split("FOLD",1)[1]    
               
		testing_file = os.path.join(outputpath, 'WSC_Eval_simple_TCP_100S_50SP_15ISP_20IMP_' + currentFoldNum +'.test')
                  
                #print train_fold
                #print testing_file   
               
		predict_file = os.path.join(train_fold, currentTrainFile + '.predict')
		
		# test model for each fold
		cmd = '{0} "{1}" "{2}" "{3}"'.format(svmpredict_exe, testing_file, model_file, predict_file)
		if not quiet:
			print('[' + str(datetime.now()).split('.')[0] + '] Fold: {0:>3} - Testing...'.format(currentTrainFile))
			Popen(cmd, shell = True).communicate()
		else:
      			Popen(cmd, shell = True, stdout = PIPE).communicate()

                #print "BREAK "      	
    return

#def removeTemp():
#	for currentFold in range(1, folds+1):
#		os.remove(os.path.join(outputpath, outputname + scenario + '_' + str(currentFold) + '.train'))
#		os.remove(os.path.join(outputpath, outputname + scenario + '_' + str(currentFold) + '.test'))
#		os.remove(os.path.join(outputpath, outputname + scenario + '_' + str(currentFold) + '.predict'))




	# perform evaluation


evaluation(grid_option)
	# remove temporary data
#	if storage == 'RemoveTemp' or storage == 'Low':
#		removeTemp()
	
	# The evaluation has been performed
