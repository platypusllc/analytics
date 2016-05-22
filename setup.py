from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
import os
import pip

# Get the current directory path.
here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the top-level README.
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get the dependencies from the requirements.txt file.
# Based on: https://gist.github.com/rochacbruno/90efe90e6549721e4189
requirements = pip.req.parse_requirements(
    'requirements.txt', session=pip.download.PipSession())
dependency_links = [str(item.link) for item in requirements
                    if getattr(item, 'link', None)]
install_requires = [str(item.req) for item in requirements
                    if item.req]

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
    test_suite="tests",
    install_requires=install_requires,
    dependency_links=dependency_links
)
