import argparse
import itertools
import os,fnmatch
import platform
from subprocess import call
from collections import defaultdict
from GNUPlotGenerator import GNUPlotGenerator
from Task import Task

def run( gnuplotCMD, title, inputfileprefix, timefilter, timedisplay):
	'''
	This run method will process raw data file, generate underlying gnuplot data and generate underlying chart.
	'''
	platform_os = platform.platform(aliased=1)
	#generate a png file path that cross platform
	
	basename = os.path.basename(inputfileprefix)
	basedir = os.path.dirname(inputfileprefix)
	profile_file_pattern= "%s*.txt" % basename
	dependency_file_pattern= "%s*.dep" % basename
	
	match_profile_files = []
	match_dependency_files = []
	for path, dirlist,filelist in os.walk(basedir):
		
		#find profile files
		for file in fnmatch.filter(filelist,profile_file_pattern):
			match_profile_files.append(os.path.join(path,file))
		#find dependency files
		for file in fnmatch.filter(filelist,dependency_file_pattern):
			match_dependency_files.append(os.path.join(path,file))
			
	if len(match_profile_files) != len(match_dependency_files):
		raise Exception("Dependency file and data file should be paired.")
	print "matches \n"
	print match_profile_files
	print match_dependency_files
	
	#process each pair of dependency file and raw data file
	for (no,file_pair) in itertools.izip(itertools.count(1),zip(match_profile_files, match_dependency_files)):
		# print file_pair
		outputfile = file_pair[0].replace('.txt','.gpl')
		png_file = file_pair[0].replace('.txt','.png')
		pngfile = png_file.replace('\\','\\\\') if "windows" in platform_os.lower() else png_file
		
		outputfile_no = change_name(outputfile,no)
		pngfile_no = change_name(pngfile,no)
		(build_tasks_all, build_task_dependencies) = preprocess(file_pair[0], file_pair[1])
		print pngfile_no
		# Generating plot script
		plot_gen = GNUPlotGenerator(title, build_tasks_all, build_task_dependencies, outputfile_no, pngfile_no ,timefilter,timedisplay)
		if plot_gen.generate_plot_file():
			#use gnuplot module to call generating file and draw picture.
			call([gnuplotCMD, outputfile_no])

def preprocess(inputfile, dependencyfile):
	# Get build tasks data from data file
	build_tasks_all = load_datafile(inputfile)
	# Get tasks dependency from data file
	build_task_dependencies = load_build_dependencies_file(dependencyfile)
	return (build_tasks_all, build_task_dependencies)
			
			
def load_datafile(datafile):
	"""
	Load task file.
	Porcess Per line in File with pattern 'task_name  start_time  end_time, task_type'
	Return: a list() of Task.
	"""
	build_tasks = []
	for line in open(datafile, 'r').readlines():
		line = line.strip().split()
		build_tasks.append(Task(line[0], float(line[1]) , float(line[2]), line[3]))

	return build_tasks

def load_build_dependencies_file(path):
	"""
	Process Per line in File with pattern 'model_fx \t rice \t model_common' , which means model_fx depends on rice and model_common
	Return dict, model_fx as key, [rice,model_common] list as value
	"""
	dependencies = dict()
	with open(path,'rt') as p:
		for line in p:
			pi = line.strip().split('\t')
			if len(pi) > 0:
				dependencies[pi[0]] = set(pi[1:])
	
	return dependencies

def change_name(file_path, change):
	basename0 = os.path.basename(file_path)
	if '.' in basename0:
		basename = basename0.replace('.','_%d.' % change )
	else:
		basename = basename0 + str(change)
	basedir = os.path.dirname(file_path)	
	return os.path.join(basedir,basename)

if __name__ == '__main__':
	#arg_parser = argparse.ArgumentParser()

	#arg_parser.add_argument('--inputfileprefix', help="Input data file path pattern, which will match *.txt and *.dep files", required=True)
	#arg_parser.add_argument('--title', help="Title for the diagram", required=True)
	#arg_parser.add_argument('--timefilter', help="Filter tasks taking less than X seconds",type=float,required=True)
	#arg_parser.add_argument('--timedisplay', help="Time labels to display, such as All, CriticalOnly or AboveTimeThreshold", required=True)
	#args = arg_parser.parse_args()
	
	gnuplotCMD = gnuplot/4.6.1/bin/gnuplot"
	#args.inputfileprefix
	#run(gnuplotCMD, "It is a test", , args.timefilter, args.timedisplay)
	run(gnuplotCMD, "It is a test", "./test1" ,60.0, "CriticalOnly")
