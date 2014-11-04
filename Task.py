from TaskDependency import TaskDependency

time_unit_millisec_to_min = 60.0 * 1000.0  #convert from millisecond to minute
time_unit_sec_to_min = 60.0
time_unit_millisec_to_sec = 1000.0

class Task(object):
	"""
	Task represent a task of a sub-project, such as rice:compileScala
	task_type: str type.such as compileScala
	start, stop: time in seconds, type is float
	mins, sec: time interval from start to stop, type is int. such as 6 min 7 sec
	"""
	def __init__(self, task_name, start, stop, task_type):
		self.task_name = task_name
		self.start = start / time_unit_millisec_to_min
		self.stop = stop / time_unit_millisec_to_min
		self.task_type = task_type
		self.mins = int(self.stop - self.start)
		self.sec = int((stop - start) / time_unit_millisec_to_sec - self.mins * time_unit_sec_to_min)
		self.project = self.task_name.split(':')[0]
		self.tasks_dependency = set()
		self.path_value = None
		self.is_critical_task = False
		self.next_critical_task = None
		
	def add_build_task_dependency(self,tasks):
		if isinstance(tasks , Task):
			self.tasks_dependency.add(tasks)
		elif tasks is list:
			self.tasks_dependency.union(tasks)
		else:
			
			raise Exception("Unmatch %s for Build Task Type!" % str(type(tasks)))
	
	def not_less_seconds(self, secs):
		return ((self.stop - self.start) * time_unit_sec_to_min - secs) >= 0
	
	def get_task_name(self):
		'''
		Pleas don't use this method, this method is only for task dependency usage
		'''
		#if 'compileScala' ==  self.task_type:
		#	return self.project
		return self.task_name
	
	def get_self_value(self):
		'''
		value is self time cost
		'''
		return self.stop - self.start
	
	def get_critical_path_value(self):
		'''
		Get path_value, which is critical task path vaule
		Initilize next_critical_task. If has not dependency, set next_critical_task with None 
		If have calc path_value before, return it
		'''
		if self.path_value != None:
			return self.path_value
		
		if len(self.tasks_dependency) == 0:
			self.path_value = self.get_self_value()
		else:
			self.next_critical_task = max(self.tasks_dependency,key=lambda task: task.get_critical_path_value()) 
			self.path_value = self.next_critical_task.get_critical_path_value() + self.get_self_value()
			
		return self.path_value

	def to_task_string(self):
		str = ""
		if self.mins > 0 :
			str += "%i min " % self.mins
		if self.sec > 0 :
			str += "%i sec" % self.sec
		if len(str) > 0 :
			str = "costs " + str
		else:
			str = "costs %i millisec" % (int((self.stop - self.start) * time_unit_millisec_to_min))
		
		return "  " + self.task_name+ " " + str
	
	def to_time_string(self):
		str = ""
		if self.mins > 0 :
			str += "%i min " % self.mins
		if self.sec > 0 :
			str += "%i sec" % self.sec
			
		return "  " + str
	
	@staticmethod
	def merge_tasks(project_name,tasks):
		'''
		task_name in pattern: rice:compileScala
		If two tasks share same sub-project name, two tasks could be combine to two tasks.
		Combine two tasks by their time cost and task_type
		Return a combined build task
		'''
		min_task_start = tasks[0].start
		max_task_stops = tasks[0].stop
		task_types = list()
		
		for task in tasks:
			task_types.append(task.task_type)
			max_task_stops = max(max_task_stops,task.stop)
			min_task_start = min(min_task_start,task.start)
			if task.project != project_name:
				raise Exception("Un match Build Project Name!")
		
		task_type_name = '{' + ', '.join(task_types) + '}'
		new_task_name = project_name + ':' + task_type_name
		return Task(new_task_name, min_task_start * time_unit_millisec_to_min, max_task_stops * time_unit_millisec_to_min ,task_type_name)
	
	@staticmethod
	def filter_task_in_by_type(build_tasks,task_types,task_keep=list()):
		'''
		Given a list of task_types and a list of tasks
		Return: a list of tasks that belong to given types
		'''
		filtered_build_tasks = list()
		for task in build_tasks:
			if task.task_type in task_types or task.task_name in task_keep:
				filtered_build_tasks.append(task)
		
		return filtered_build_tasks

	@staticmethod
	def merge_tasks_by_type(build_tasks,task_types):
		'''
		Given a list of build_tasks, merge task that belong to given task_typ1 and task_type2
		find task_pair that has same subproject name and one is belong to task_type1 and another is task_type2
		Return a new list of build_tasks than contain new 
		'''
		
		task_result = list()
		task_dict = defaultdict(list)
		
		for task in build_tasks:
			if task.task_type in task_types:
				task_dict[task.project].append(task)
			else:
				task_result.append(task)
				
		for task_list_key in task_dict.keys():
			if len(task_dict[task_list_key]) > 1:
				task_result.append(Task.merge_tasks(task_list_key,task_dict[task_list_key]))
			else:
				task_result.extend(task_dict[task_list_key])
				
		return task_result
   
	@staticmethod
	def filter_task_by_time(build_tasks, time_threshold , task_keeping):
		''''
		get task that more than time_threshold seconds
		build_tasks and task_keeping are all List[Task]
		return: List[Task]'''
		filter_tasks = dict()
		for task in task_keeping:
			filter_tasks[task.task_name] = task
		for task in build_tasks:
			if task.not_less_seconds(time_threshold):
				filter_tasks[task.task_name] = task
				
		return filter_tasks.values()
		
