# Platypus Analytics

[![Build Status](https://travis-ci.org/platypusllc/analytics.svg)](https://travis-ci.org/platypusllc/analytics)
[![Documentation Status](https://readthedocs.org/projects/platypus-analytics/badge/?version=latest)](http://platypus-analytics.readthedocs.org/en/latest/?badge=latest)

Python library for Platypus data analysis.

 >:warning: This library is currently under development!  Some of the functionality in the library may be incomplete or untested.

## Quickstart

The easiest way to install is via `pip`:
```bash
$ pip install git+https://github.com/platypusllc/analytics.git
```

## Documentation ##

* **API documentation** can be found on [ReadTheDocs](http://platypus-analytics.readthedocs.org/en/latest/).
* **Usage examples** of this library can be found in the [examples](examples) directory.

[1]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
[2]: https://www.continuum.io/documentation

## Development

If you would like to develop the library, you can install the library with the `--editable/-e` option.  If you do this, you may want to consider using a python virtual environment.  Two popular options are [virtualenv][1] and [anaconda][2]:

**Standalone:**
```
$ git clone https://github.com/platypusllc/analytics.git
$ pip install -e analytics
```

**Virtualenv:**
```bash
$ virtualenv ./venv
$ . ./venv/bin/activate
$ pip install -e git+https://github.com/platypusllc/analytics.git#egg=platypus-analytics
$ cd ./venv/src/platypus-analytics
```

**Anaconda:**
```bash
$ conda create -n platypus
$ source activate platypus
$ pip install -e git+https://github.com/platypusllc/analytics.git#egg=platypus-analytics
```
