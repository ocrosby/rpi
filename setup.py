from setuptools import setup, find_packages

setup(
    name='ripper',
    version='0.1.0',
    author='Omar Crosby',
    author_email='omar.crosby@gmail.com',
    description='A CLI tool for retrieving and analyzing Soccer matches',
    packages=find_packages(),
    install_requires=[
        'requests',
        'click',
        'urllib3',
        'setuptools',
        # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'ripper=ripper.cli:cli',
        ],
    },
)
