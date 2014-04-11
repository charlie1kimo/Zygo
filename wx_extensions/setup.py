"""
setup.py
	the distutil script for this package.
"""

from distutils.core import setup
import wx_extensions

setup(name='wx_extensions',
	version=wx_extensions.__version__,
	url="http://www.zygo.com/",
	author="Charlie Chen",
	author_email="cchen@zygo.com",
	maintainer='Charlie Chen',
	maintainer_email='cchen@zygo.com',
	description='wxPython extensions API',
	platforms=['Windows', 'MacOSX', 'Linux'],
	packages=['wx_extensions'])