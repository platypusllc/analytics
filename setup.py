from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
import os

# Get the current directory path.
here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the top-level README.
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Configure python distribution package.
setup(
    name='platypus-analytics',
    version='0.1.0.dev',
    description='Analytics for Platypus LLC',
    long_description=long_description,
    url='https://github.com/platypusllc/analytics',
    author='Pras Velagapudi',
    author_email='pras@senseplatypus.com',
    license='BSD',
    keywords='data analysis',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'import=platypus.io:import'
        ]
    },
    install_requires=[
        'numpy',
        'pymongo',
        'pyserial',
        'scipy',
        'six',
        'utm'
    ],
    test_suite="tests",
)
