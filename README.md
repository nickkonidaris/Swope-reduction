Swope Telescope Photometry
==========================
[![Build Status](https://travis-ci.org/nickkonidaris/Swope-reduction.svg?branch=master)](https://travis-ci.org/nickkonidaris/Swope-reduction)




Documentation
-------------
Goes here

Installation
------------
clone the repository  
    `git clone git@github.com:`
change into the top-level directory  
    `cd empty_python`  
install using  
    `pip install .`

Dependencies
------------
 * Python 3.5

Example usage
-------------
May not be needed

Contribution guide
------------------
The empty_python Project follows the Google Python style guide, with Sphinxdoc docstrings for module public functions. If you want to
contribute to the project please fork it, create a branch including your addition, and create a pull request.

The tests use relative imports and can be run directly after making
changes to the code. To run all tests use `nosetests` in the main directory.
To run the examples after code changes, you need to run `pip install --upgrade .`
Documentation is generated by typing `make html` in the doc directory,
the contents of doc/build/html/ should then be copied to the right directory of your gh-pages branch.

Before creating a pull request please ensure the following:
* You have written unit tests to test your additions
* All unit tests pass
* The examples still work and produce the same (or better) results
* The code is compatible with both Python 2.7 and Python 3.5
* An entry about the change or addition is created in CHANGELOG.md
* Add yourself as contributing author

Contributing authors so far:
* Nick Konidaris
