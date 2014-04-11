"""
exceptions.py
	exceptions.py contains the exception class and utilities for the wx_extension module
"""

import traceback
import wx
from wx_extensions.windows import WindowBase

########
# @Purpose:
#	function to handles the exceptions thrown in wxWidget
# @Inputs:
#	(function) funct = given function
#	(list) *args = function's arguments
#	(dict) **kwargs = function's keyword arguments
# @Outputs:
#	(function) wrapper function.
########
def handlesErrors(funct, *args, **kwargs):
	def wrapper(self, *args, **kwargs):
		try:
			return funct(self, *args, **kwargs)
		except Exception, e:
			if isinstance(self, WindowBase):
				topWindow = self.getTopLevelWindow()
				if hasattr(topWindow, 'statusBarMain'):
					topWindow.statusBarMain.SetStatus('ERROR')
				self.popErrorBox("ERROR: Exception in: %s" % funct.__name__, 
								traceback.format_exc())
				traceback.print_exc()
	return wrapper

