
class Bunch(object):
	def __init__(self, **kwds):
		self.__dict__.update(kwds)

	def __str__(self):
		s = 'Bunch('
		for key, value in self.__dict__.items():
			s += "%s = %s, "%(key, value)
		s = s[:-2] # get rid of ', '
		s += ')'
		return s
	
	def __repr__(self):
		s = 'Bunch('
		for key, value in self.__dict__.items():
			s += "%s = %r, "%(key, value) # use representation of value
		s = s[:-2] # get rid of ', '
		s += ')'
		return s
		#return self.__dict__.__str__()

	

	