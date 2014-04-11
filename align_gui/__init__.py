__doc__ = \
"""
package align_py:
	This package contains the hexapod alignment modules and utilities
"""
__version__ = "1.8.1_beta; 02-26-2013"
__owner__ = 'cchen'
__history__ = \
"""
History:
02/26/2013	1.8.1_beta		cchen	moveTestPanel.py added for displaying moveTest tab
02/17/2013	1.8.0_beta		cchen	capgauge reading scale factor change. acutator module scale factor should be reversed. miscellaneous display changes.
12/03/2013	1.7.1_beta		cchen	bugs fixed in hexapodPositionsPanel.py
12/02/2013	1.7.0_beta		cchen	error-handling in wxWidget added; add hexapodPositionsPanel.py (tab to go to different saved positions)
11/25/2013	1.6.0_beta		cchen	major updates/tests pass for the program. pushing it to beta version.
11/21/2013	1.5.1_alpha		cchen	minor updates on how plotting change through plotLegChange() and plotCapChange() in moveHexapodPanel.py
10/29/2013	1.5.0_alpha		cchen	major updates in titles and descriptions in every tabs. Add icons.
10/03/2013	1.4.0_alpha		cchen	updated adjustHexpodPanel. Add threading and move dialog. Add the actual Actuator modules to perform movements.
09/20/2013	1.3.0_alpha		cchen	hexapod tab updates; miscellaneous bugs fixed.
09/17/2013	1.2.0_alpha		cchen	add adjust hexapod tab/panel; add mode options in inputs
09/11/2013	1.1.0_alpha		cchen	fixed miscellaneous bugs in inputs/starting/residual/results panel
09/09/2013	1.0.0_alpha		cchen	add version number to the package.
"""
__bugs__ = \
"""
02/26/2014	1.8.1_beta		cchen	CompositeCapgauge unreserved makes the program not responsible. Should create a menu item for re-initialize CompositeCapgauge class
									Keep a LOG file when enabling DEBUG MODE
"""
