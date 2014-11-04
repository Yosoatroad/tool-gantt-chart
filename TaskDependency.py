
class TaskDependency(object):
	
	@staticmethod
	def show_task_path(candi_path):
		print 'Show task path'
		for candi in candi_path[0]:
			print candi.to_task_string() + "\n"
		print candi_path[1]
		
	@staticmethod
	def create_critical_dependency_line(tasks,task_dependencies):
		'''
		dependency_file contains task dependency information generated from buildprofile.gradle.
		Currently, compileScala task's dependency is updated.
		'''
		task_map = build_task_map(tasks)
		# Get leave_tasks, which don't depend on any tasks.
		leave_tasks = shave_build_roots_and_leaves(task_dependencies,task_map)[1]
		# task_dependencies will be updated after run update_task_dependency, so it will not be used anymore.
		update_task_dependency(task_map,task_dependencies)
		
		task_path_list = find_max_task_path(task_map,leave_tasks)
		TaskDependency.mark_critical_task(task_path_list)
		
		return task_path_list
		
	@staticmethod
	def mark_critical_task(tasks):
		'''
		Mark tasks' attribute is_critical_task as True
		'''
		
		for task in tasks:
			task.is_critical_task=True
			
		
def build_task_map(tasks):
	'''
	Build Dict[String,Task] name as key, task as value
	@return task map
	'''
	task_map = dict()
	for task in tasks:
		if task.get_task_name() not in task_map:
			task_map[task.get_task_name()] = task
		else:
			raise Exception("Duplicate task name in building task map!")
	return task_map
	
def update_task_dependency(task_map,task_dependencies):
	'''
	task map: task name as key, task as value
	task_dependencies: dict, entity like: model_fx as key, [rice,model_common] list as value
	These task leaves' dependencis are updated.
	@return: a list of task leaves in str type with task name
	'''
	
	extract_build_dependencies(task_dependencies,lambda child,parent=None : save_dependency_to_map(task_map,child,parent))
	
def find_max_task_path(task_map,last_pieces):
		'''
		@return: List[Task] max task time cost path.
		'''
		#candi_path_tuples = [ task_map[piece].get_critical_path_value() for piece in last_pieces]
		#return max(candi_path_tuples,key=lambda candi_path_tuple: candi_path_tuple[1])
		last_task = task_map[max(last_pieces, key=lambda piece_name : task_map[piece_name].get_critical_path_value())]
		task_list = list()
		while(last_task != None):
			task_list.append(last_task)
			last_task = last_task.next_critical_task
		task_list.reverse()
		return task_list
		
def save_dependency_to_map(task_map,child,parent=None):
	'''
	child and parent is string, which can be used to find the exact Build Task
	If parent is None, then child is the root Build Task
	If parent is not None, then child is the node in tree that has at least one parent and should add parent as its dependency
	Warning: there is a chance that task_map not matched with task_dependency
	If parent and child are in task_map keys, an exception will be rasied.
	'''
	if parent in task_map.keys() and child in task_map.keys():
		task_map[child].add_build_task_dependency(task_map[parent])
	elif parent == None:
		pass
	elif parent not in task_map.keys() or child not in task_map.keys():
		raise Exception("It should not be happen!")
	else:
		raise Exception("Code should not touch here!")

def extract_build_dependencies(dependencies,saving_functor,removed=set()):
	'''
	args:
	dependencies is dict[String,Set[String]]
	saving_functor is a method to save extracted task dependency
	Warning: build dependencies may not be matched with build task in map
	'''
	removing = []
	for task_name in dependencies:
		tasks_to_remove_set = dependencies[task_name] & removed
		if len(tasks_to_remove_set) > 0:
			for task_to_remove in tasks_to_remove_set:
				# task_name is project and task_name depends on projects of dependencies[task_name] 
				saving_functor(task_name, task_to_remove )
			dependencies[task_name] = dependencies[task_name] - tasks_to_remove_set
		
		if len(dependencies[task_name]) == 0:
			removing.append(task_name)
	'''
	Until there is no task left
	'''
	if len(removing) > 0 :
		for piece in removing:
			dependencies.pop(piece)
		extract_build_dependencies(dependencies,saving_functor,set(removing))
		
def shave_build_roots_and_leaves(task_dependencies,task_map):
	'''
	Root task: no task depends on root task.
	Leave task: leave task doesn't depend on any task.
	In other words:
	Task leave are not in any dependency list
	Task root have empty dependency list
	Also, make sure the tasks in root or leave set are in task_map keys
	@args:
	task_dependencies: dict key: model_common, value: [rice]
	@return: Tuple (Task root, Task leave)
	
	'''
	
	dep_list = list()
	root_list = list()
	all_list = list()
	key_to_remove = set()
	for task_dep in task_dependencies:
		if task_dep in task_map:
			all_list.append(task_dep)
			all_list.extend(task_dependencies[task_dep])
			
			if len(task_dependencies[task_dep]) > 0:
				dep_list.extend(task_dependencies[task_dep])
			else:
				root_list.append(task_dep)
		else:
			key_to_remove.add(task_dep)
	'''
	Shave:
		If key in task_dependencies don't appear in task_map, it should be removed in task_dependencies
	'''
	for key in key_to_remove:
		task_dependencies.pop(key)
	'''
	Yes, there is a chance that a task is root and leave.
	'''
	return ( set(root_list), (set(all_list) - set(dep_list)) )
		
