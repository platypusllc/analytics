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
    name='platypus-analysis',
    version='0.1.0.dev',
    description='Analysis tools for Platypus data',
    long_description=long_description,
    url='https://github.com/platypusllc/Analysis',
    author='Pras Velagapudi',
    author_email='pras@senseplatypus.com',
    license='Platypus LLC CONFIDENTIAL',
    keywords='data analysis',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: Other/Proprietary License',
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
        'scipy'
    ],
)
