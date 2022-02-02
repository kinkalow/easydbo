import os
import shutil
from setuptools import setup, find_packages
from easydbo import __version__

scripts_dir = 'build/_scripts'
if not os.path.exists(scripts_dir):
    os.makedirs(scripts_dir)
shutil.copyfile('easydbo.py', f'{scripts_dir}/easydbo')

setup(
    name='easydbo',
    version=__version__,
    description='GUI tool for easy database operation',
    packages=find_packages(),
    scripts=[f'{scripts_dir}/easydbo'],
    python_requires='>=3.8',
)
