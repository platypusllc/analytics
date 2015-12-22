# Platypus Analytics #

[![Build Status](https://travis-ci.org/platypusllc/analytics.svg)](https://travis-ci.org/platypusllc/analytics)

Python library for Platypus data analysis.

 >:warning: This library is currently under development!  Some of the functionality in the library may be incomplete or untested.

## Installation ##
The easiest way to install is via `pip`:
```bash
$ sudo pip install git+https://github.com/platypusllc/analytics.git
```

If you would like to develop, you can install the library with the `--editable` option.  If you do this, it is highly recommended that you use a [virtualenv][1]:
```bash
$ virtualenv ./venv
$ . ./venv/bin/activate
$ pip install -e pip install -e git+https://github.com/platypusllc/analytics.git#egg=platypus-analytics
$ cd ./venv/src/platypus-analytics
```

Now, in a terminal, you can access your `virtualenv` and the `analytics` library by calling:
```bash
$ . ./venv/bin/activate
$ python
>>> import platypus
```

[1]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
