"""
setup.py
	distribution setup script for this package
"""
from distutils.core import setup
import env_database

setup(name='env_database',
	version=env_database.__version__,
	url='http://www.zygo.com/',
	author='Charlie Chen',
	author_email='cchen@zygo.com',
	maintainer='Charlie Chen',
	maintainer_email='cchen@zygo.com',
	description='env_database package that handles communication and display with the environment database.',
	platforms=['Windows', 'MacOSX', 'Linux'],
	packages=['env_database', 'env_database.env_plots2'],
	package_data={'env_database.env_plots2': ["icons/*.jpg", "icons/*.ico"]})