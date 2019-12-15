from setuptools import setup
from setuptools import find_packages

setup(
    name='sfdlpy',
    version='0.0.1a',
    py_modules=['sfdlpy'],
    install_requires=[
        'Click',
    ],
    packages=find_packages(include='lib.*'),
    entry_points='''
        [console_scripts]
        sfdlpy=sfdlpy:sfdl
    '''
)
