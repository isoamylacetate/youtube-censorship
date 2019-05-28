"""
Defines custom exceptions used throughout the project
"""
class HTTPError(Exception):
	"""
	Raised when bad http get request occurres
	"""
	pass

class ArgumentError(Exception):
	"""
	Raised when invalid arguments are supplied to function
	"""
	pass

class ParamsError(Exception):
	"""
	Raised when an invalid params file is supplied
	"""
	pass

