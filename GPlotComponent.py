
class TaskRectangle(object):
	"""
	TaskBar represent a task rectange in the diagram, length represents time costs
	"""
	def __init__(self, bottom_left, top_right, fill_color):
		self.bottom_left = bottom_left
		self.top_right = top_right
		self.fill_color = fill_color
	
	def middle_point(self):
		x = (self.bottom_left[0] + self.top_right[0]) / 2
		y = (self.bottom_left[1] + self.top_right[1]) / 2
		return (x,y)
	
	def mid_right_point(self):
		x = self.top_right[0]
		y = (self.bottom_left[1] + self.top_right[1]) / 2
		return (x,y)
		
	def mid_left_point(self):
		x = self.bottom_left[0]
		y = (self.bottom_left[1] + self.top_right[1]) / 2
		return (x,y)

class TaskDependencyLine(object):

	def __init__(self, start, end):
		self.start = start
		self.end = end
	
	def middle_point(self):
		x = (self.start[0] + self.end[0]) / 2
		y = (self.start[1] + self.end[1]) / 2
		return (x,y)
	
class TaskLabel(object):
	"""
	TaskLabel represent a task label beside the Taskbar, give time information about the task
	value: type is str, contains time information
	"""
	def __init__(self,value,lp):
		self.value = value
		self.left_point = lp
