__doc__ = \
"""
package wx_extension:
	This package contains the wxPython extension modules that allows fast user interface develop.
	Modules:
		1. dialogs:
			- contains dialogs extensions
		2. exceptions:
			- contains exceptions handling utility functions
		3. grid:
			- contains grids extensions
		4. statusbar:
			- contains statusbar extensions
		5. windows
			- contains windows (frame, panel) extensions
"""
__version__ = '1.2.1'
__owner__ = 'cchen'
__history__ = \
"""
History:
03/13/2014	1.2.1	cchen	add popInfoBoxAndReturnBool() and popRetryBoxAndReturnBool() in windows.WindowsBase for better API design
12/09/2013	1.2.0	cchen	add documentation to exceptions module
11/25/2013	1.1.2	cchen	small modification on windows.WindowsBase. Add __getThreadMap__ public function.
10/17/2013	1.1.1	cchen	modify windows.WindowsBase.__startThread__ and add windows.WindowsBase.__cleanThreadMap__; WindowsBase now handles and save the running background threads in a hashmap.
10/03/2013	1.1.0	cchen	Add "dialogs" module.
10/01/2013	1.0.3	cchen	ScrolledPanelBase add SetFocusIgnoringChildren() for setting focus on the panel. This makes scrolling works. Add __startThread__ into WindowsBase. Add dialogs modules.
09/20/2013	1.0.2	cchen	small bug fix in grid.SetValue() -> if value to set is string and data type != str, there might be error; add 2 functions to grid.
09/10/2013	1.0.1	cchen	add getTopLevelWindow() to WindowsBase class
04/05/2013	1.0.0	cchen	first created documentation
"""