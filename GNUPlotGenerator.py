import itertools
import os,fnmatch
from collections import defaultdict
from GPlotComponent import TaskRectangle, TaskLabel, TaskDependencyLine
from Task import Task
from TaskDependency import TaskDependency

class GNUPlotGenerator(object):

	def __init__(self, title, build_tasks_all, build_task_dependencies, outputfile, png_file, timefilter, timedisplay):
		'''
		Except Inpufile and Dependencyfile, all other files and data should be loaded from configure file.
		'''
		
		self._build_tasks_all = build_tasks_all
		self._build_task_dependencies = build_task_dependencies
		self._outputfile = outputfile

		self._png_file = png_file
		
		self._title = title
		self._timefilter = timefilter # used to filter tasks that take less than a given time threshold
		self._timedisplay = timedisplay # user to specify which task time labels to display 
		self._trick_length = 0.00 # make task rectangle a little longer in the diagram for easily recognizing
		self._single_task_row_height = 30
		self._color_pool = {'compileScala': 'rgbcolor "#0000FF"', #blue
					  'compileTestScala' : 'rgbcolor "#00FF00"', #green
					  'test' : 'rgbcolor "#FF8000"' , #orange
					  'compileFunctionalTestScala' : 'rgbcolor "#9F35FF"' , #purple
					  'functionalTest' : 'rgbcolor "#FFCC33"' , #yellow
					  'others' :'rgbcolor "#FFFFFF"'} #white
		
	def make_task_rectangles_and_dependency_path(self, build_tasks,task_path, task_name_map, colors):
		"""
		make sure tasks of task_path are in build_tasks.
		build_tasks must be sorted by starting timestamp.
		Generate a list of TaskRectangle by width refer to task time costs, color refer to build task type
		Return: a list of TaskRectangle
		"""
		task_rectangles = []
		task_height = 0.8  # set a height of rectangle in diagram.
		task_lines = []
		labels = []
		#task_line_point = []
		task_rectangles_map = dict()
		
		'''for index in range(0,len(task_path)):
			task = task_path[index]
			axis_y = task_name_map[task.task_name]
			bottom_left = (task.start, axis_y - 0.5 * task_height)
			top_right = (task.stop + self._trick_length, axis_y + 0.5 * task_height)
			point = ((bottom_left[0] + top_right[0]) / 2,(bottom_left[1] + top_right[1]) / 2) 
			task_line_point.append(point)'''
		
		for task in build_tasks:
			axis_y = task_name_map[task.task_name]
			bottom_left = (task.start, axis_y - 0.5 * task_height)
			top_right = (task.stop + self._trick_length, axis_y + 0.5 * task_height)
			task_rectangle = TaskRectangle(bottom_left, top_right, colors[task.task_type])
			task_rectangles.append(task_rectangle)
			task_rectangles_map[task.task_name] = task_rectangle
		
		'''for index in range( 0,len(task_line_point) - 1):
			task_lines.append(TaskDependencyLine(task_line_point[index],task_line_point[index + 1]))'''
		
		for index in range( 0, len(task_path) - 1):
			line = TaskDependencyLine(task_rectangles_map[task_path[index].task_name].mid_right_point(), task_rectangles_map[task_path[index + 1].task_name].mid_left_point() )
			task_lines.append(line)
			
		return (task_rectangles,task_lines)
					  
	def make_labels(self, build_tasks, task_name_map):
		"""
		Return: a list of TaskLabel, which will be displayed beside task rectangle.
		"""
		labels = []
		if (self._timedisplay != 'None'):		
			for task in build_tasks:
				# if True in (self._timedisplay=='All', self._timedisplay=='CriticalOnly' and task.is_critical_task, self._timedisplay=='AboveTimeThreshold' and task.mins * 60 + task.sec >= self._timefilter):
				if self._timedisplay=='All' or \
				   (self._timedisplay=='CriticalOnly' and task.is_critical_task) or \
				   (self._timedisplay=='AboveTimeThreshold' and task.mins * 60 + task.sec >= self._timefilter):
					axis_y = task_name_map[task.task_name]
					labels.append(TaskLabel(task.to_task_string(),( task.stop + self._trick_length, axis_y))) 

		return labels

	def make_task_names_and_types(self,build_tasks):
		"""
		Collect task names in reverse seqence and task types in set from build_tasks
		Return: a list of task name and a list of unique task type
		"""
		
		task_names = []
		task_types = set()
		for task in build_tasks:
			if task.task_name not in task_names:
				task_names.append(task.task_name)
			task_types.add(task.task_type)
		
		task_names.reverse() # task names are drawn from top to bottom in y-axis
		return list(task_types), task_names

	def make_task_color(self,task_types):
		"""
		assign each task_type with a color
		Return: a dict with key: task_type, value: color
		"""
		task_colors = dict()
	   
		for task_type in task_types:
			if task_type in self._color_pool:
				task_colors[task_type] = self._color_pool[task_type]
			else:
				task_colors[task_type] = self._color_pool['others']

		return task_colors
		
	def generate_plot_coord(self,diagram_title, build_tasks, task_names, task_name_map):
		"""
		Generate Gnuplot coordinates.
		Return: a list of Gnuplot command line
		"""
		axis_x_max = max(task.stop for task in build_tasks) + 5 #set max axis_x value, book 5 space for concatenating label at the end of task rectangle
		axis_y_max = len(task_names) + 1 #set max axis_y value
		axis_x_label = 'time (minutes)' # set x axis a title
		axis_y_label = 'task' # set y axis a title
		# Set each unit of axis y with task name
		ytics = ''.join(['(', ', '.join(('"%s" %d' % item) for item in task_name_map.iteritems()), ')'])
		
		# Set plot coordinates axis
		plot_coordinates = ['reset', 'set xrange [0:%f]' % axis_x_max,
						   'set yrange [0:%f]' %  axis_y_max,
						   'set xlabel "%s"' % axis_x_label,
						   'set ylabel "%s"' % axis_y_label,
						   'set title "%s"' % diagram_title,
						   'set ytics %s' % ytics,
						   'set grid xtics',
						   'set grid ytics',
						   'set autoscale x']
						   
		return plot_coordinates

	def generate_plot_rectangle(self, task_rectangles):
		"""
		Generate Gnuplot rectangles.
		Return: a list of Gnuplot command line
		"""
		# Generate gnuplot rectangle objects
		plot_task_rectangles = (' '.join(['set object %d rectangle' % index,
									 'from %f, %f' % rectangle.bottom_left,
									 'to %f, %f' % rectangle.top_right,
									 'fillcolor %s ' % rectangle.fill_color])
						for index, rectangle in itertools.izip(itertools.count(1), task_rectangles))
		
		return plot_task_rectangles
	
	def generate_plot_arrow(self,task_lines):
		"""
		Generate task lines
		Return: a list arrow-headed lines
		"""
		plot_arrows = (' '.join(['set arrow',
								 'from %f, %f' % line.start,
								 'to %f, %f' % line.end,
								 ' linetype 2 linecolor rgbcolor "#FF0000"  linewidth 1.980 filled size 0.15,15'])
						for line in task_lines)
		
		return plot_arrows
		
	def generate_plot_label(self, task_labels):
		"""
		Generate Gnuplot labels.
		Return: a list of Gnuplot command line
		"""
		plot_labels = (' '.join(['set label \"%s\" ' % label.value, 'at %f, %f' % label.left_point]) for label in task_labels) 
		
		return plot_labels

	def generate_plot_line(self):
		"""
		Generate Gnuplot lines.
		Return: a list of Gnuplot command line
		"""
		# Generate gnuplot lines
		plot_lines = ['plot ' + ', \\\n\t'.join(' '.join(['-1', 'title "%s"' % t, 'with lines', 'linecolor %s ' % self._color_pool[t], 'linewidth 5']) for t in sorted(self._color_pool,key=lambda task_type: len(task_type)))]

		return plot_lines
	#png size and font size should come from configuration.
	def generate_plot_png(self,png_file,height=1500,width=1980,font_size=13):
		"""
		Generate PNG gnuplot configuration
		Return: a list of gnuplot command line
		"""
		font_file_paths = self.find_avail_fontpaths()
		if height < 1500:
			height = 1500
		if len(font_file_paths) > 0: 
			set_png = 'set terminal png font \'%s\' %d size %d,%d' % (font_file_paths[0],font_size,width,height)
		else:
			set_png = 'set terminal png size %d,%d' % (width,height)
		
		return [ set_png, 'set output \"%s\"' % ( png_file)]
					 
	def generate_plot_output(self):
		"""
		Generate gnuplot output
		Return: a list of gnuplot command line
		"""
		return ['unset output','exit']
		
	def generate_plot_file(self):

			'''
			Step One: analyse the build task
			'''
			#filter tasks by given type wanted
			#build_tasks_unsorted = Task.filter_task_in_by_type(self._build_tasks_all,self.task_type)
			
			#get a task list that cost max time cost
			task_list = TaskDependency.create_critical_dependency_line(self._build_tasks_all, self._build_task_dependencies)
			'''
			Step Two: filter tasks and sort tasks
			'''
			time_threshold = max(1.0, self._timefilter ) # time threshold must be at least 1.0 second
			#filter tasks by given time_threshold
			build_tasks_unsorted = Task.filter_task_by_time(self._build_tasks_all,time_threshold,task_list)
			#sort it with time start
			build_tasks = sorted(build_tasks_unsorted, key=lambda build_task: build_task.start)
			'''
			Step Three: draw the build task
			'''
			# Collect task type and task name from build tasks
			task_types, task_names = self.make_task_names_and_types(build_tasks)
			# Set color for each task type
			color_task = self.make_task_color(task_types)
			# Set indices to tasks
			task_map = dict(itertools.izip(task_names, itertools.count(1)))
			# Make task_rectangles in the coordinates axis
			(task_rectangles,task_arrows) = self.make_task_rectangles_and_dependency_path(build_tasks,task_list, task_map, color_task)
			# Make Task label between  task_rectangle in the coordinates axis
			task_labels = self.make_labels(build_tasks, task_map)
		   
			# Generate png gnuplot commands
			plot_png = self.generate_plot_png(self._png_file,len(task_rectangles) * self._single_task_row_height)
			plot_coord = self.generate_plot_coord(self._title, build_tasks, task_names, task_map)
			plot_rectangles = self.generate_plot_rectangle(task_rectangles)
			plot_arrows = self.generate_plot_arrow(task_arrows)
			plot_labels = self.generate_plot_label(task_labels)
			plot_lines = self.generate_plot_line()
			plot_output = self.generate_plot_output()
			# Save plot file and generate png 
			return self.save_file(self._outputfile,plot_png, plot_coord, plot_rectangles, plot_arrows, plot_labels, plot_lines,plot_output)

	def find_avail_fontpaths(self):
		"""
		Find available font files endwith *.ttf (Linux only for the time being)
		Return: a list of fonts file path
		"""
		font_pattern = "*.ttf"
		font_dir = "/usr/share/fonts" 
		avail_fonts = []
		if os.path.exists(font_dir): #check font dir exists
			for path, dirlist, filelist in os.walk(font_dir):
				for name in fnmatch.filter(filelist,font_pattern):
					avail_fonts.append(os.path.join(path,name))
		
		return sorted(avail_fonts)
		

	
	def save_file(self,outputfile,plot_png, plot_coord, plot_rectangles, plot_arrows, plot_labels, plot_lines,plot_output):
		"""
		Save plot command to outputfile.
		"""
		with open(outputfile, 'wt') as out_file:
			out_file.write('\n'.join(itertools.chain(plot_png, plot_coord, plot_rectangles,plot_arrows, plot_labels, plot_lines, plot_output)))
			print ("Create GPL file %s" % outputfile)
			return True
