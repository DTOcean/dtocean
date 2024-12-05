=====================
Demo Package Features
=====================

Introduction
============

This demonstration package is a vehicle for presenting several features of
the Python programming language, with a particular focus on producing complete,
user installable applications. It also demonstrates some input and output
features and shows off the powerful Pandas data analysis package, which is
likely to be utilised often within the DTOcean project.

The following sections will introduce a feature theme and then each feature 
in turn, explaining the purpose, outcomes and programming for each.

Another great reference for those starting out with Python package development 
is:

`How To Package Your Python Code
<http://www.scotttorborg.com/python-packaging/index.html>`__

This gives some simple examples of putting a package together, although
covers less features than presented here.

Standard Python Module Structure
================================

The demo package is designed such that it will work as a typical python
module. It has a principal class called Spreadsheet (that creates a 
spreadsheet of random numbers) that can be imported in the typical
Python style. Using an `interpreter <https://docs.python.org/2/tutorial/interpreter.html>`__,
the command:

.. code:: pycon

    from dtocean_dummy import Spreadsheet
    
will add the Spreadsheet class to the session. The description and parameters
of the Spreadsheet class are found in :class:`dtocean_dummy.main.Spreadsheet`.

Within the source code, the Spreadsheet class is defined in a file called main.py, in a directory called
dtocean_dummy. This directory also contains a file called __init__.py, which
turns dtocean_dummy into the name of a package. When we import dtocean_dummy
all of the files within the directory become modules of dtocean_dummy and the
classes and functions are accessible through these. Additionally, these can have
shortcuts which are defined within __init__.py, such as the Spreadsheet class.

Doing something with Spreadsheet is easy. To make and print a spreadsheet of 5 
rows, all that is needed is:

.. code:: pycon
    
    test_sheet = Spreadsheet()
    test_sheet(5)
    
This method of executing a class directly requires the 
special __call__ method to be within the class definition. For example, the __call__
method of the Spreadsheet class may look a little like this:

.. code:: python

    class Spreadsheet(object):
        
        '''Create spreadsheets of random numbers and write to file.'''
        
        ...
            
        def __call__(self, rows):
            
            '''Create a table of the given number of rows and either print
            to stdout or create a file.'''
            
            # Make the table
            self.make_table(rows)
            
            print(self.table)
            
            return


Note, that the __call__ method uses the public method make_table. The 
Spreadsheet class can  also do more, and this is discussed further
below.

Inputs and Outputs
==================

This demo package shows several methodologies for collecting inputs and
creating outputs. Above, we have seen the most basic output type, which is to
print to screen, but we may also write to files, for instance. Additionally,
we can collect information from the user using command line commands, perhaps,
or from configuration files. Logging from the application can also be very
useful and is included in the demo. All these topics are discussed in the
subsections below.

Note that graphical user interfaces (GUIs) are not included at this stage. They 
tend to be somewhat different in design to non-graphical applications, and more 
difficult to produce in separate stages, thus it may not be appropriate for the 
module designers to consider using GUIs. That said, sometimes a simple file 
picker can be extremely useful, so it may be appropriate to demonstrate these 
features. This is a topic for further discussion. 

Command Line Interface
======================

The DTOcean dummy module has two command line interface programs, one to
create spreadsheets, the other to update configuration files. For reference, 
the Windows command prompt can be assessed in Windows using `these instructions
<http://windows.microsoft.com/en-us/windows/command-prompt-faq>`__. An
alternative is `TCC LE <http://jpsoft.com/tccle-cmd-replacement.html>`__ which 
offers more advanced (bash like) features, such as command history.

Within the dtocean-dummy-module source code, the command line interfaces are
defined in the command.py file. They rely on a module called 
:py:mod:`argparse`, which provides a framework for retrieving arguments and
options for python applications. Usefully, it also provides help to the user,
which can be retrieved from the command prompt with the commands

.. code:: bash

    dtocean-dummy -h
    
Only the positional arguments of the command line interface must be
satisfied. Therefore, a minimum working example of dtocean-dummy
is

.. code:: bash

    dtocean-dummy 5
    
This should produce a table of 5 rows and 2 columns. The additional optional
arguments relate to file outputs and configuration options, which are
discussed below. The installation of the command line programs into the 
operating system (called entry points) is a packaging issue, which also has
a dedicated section below.

File Outputs
============

The dtocean-dummy-module can save the tables it produces as either comma
separated value (csv) or Microsoft Excel (xls) files. This feature harnesses
the power of the Python :py:mod:`pandas` package, which has many useful
functions for working with tabulated data, including file inputs and outputs.

To create files using the command line interface, the options -f (or --format)
and -o (or --out) must be provided. The first specifies what format the file
should take, the second where the file should be placed. A simple example
is as follows:

.. code:: bash

    dtocean-dummy -f xls -o test.xls 5
    
This will create a file called "test.xls" in the `working directory 
<http://en.wikipedia.org/wiki/Working_directory>`__ of the command prompt. This
file can then be opened using Excel.

For users that require ASCII format output, the csv option can be used, for
example:

.. code:: bash

    dtocean-dummy -f csv -o test.csv 5

which will create a file called test.csv in the working directory which can be
opened with any text reader.

All of the above commands can also be executed using the python interpretor and
the Spreadsheet class. To create a csv file, for example, the following code
is required:

.. code:: pycon

    from dtocean_dummy import Spreadsheet
    
    test_sheet = Spreadsheet()
    test_sheet(5, out_path='test.csv')
    
This will then create the file "test.csv" in the working directory of the
Python interpretor. In the :meth:`dtocean_dummy.main.Spreadsheet.__call__`
method, the default value for the "out_fmt" argument is "csv" and so it is
not required in the above function call.

Configuration Files
===================

Although the Spreadsheet class does not require file inputs for its 
functionality, certain optional values can be set using a configuration file
that is not directory accessible using the command prompt tool. To explain,
the :meth:`dtocean_dummy.main.Spreadsheet.__init__` method of spreadsheet has
two optional arguments, "low" and "high". These arguments specify the range
of values that the random numbers in the created table may take. By default,
this is set to the range \[0, 1), but to change it is simple:     

.. code:: pycon

    test_sheet = Spreadsheet(high=10)
    test_sheet(5)
    
This will print a table of 5 rows, where the entries in the first column lie
between 0 and 10.

It is **not** possible to directly change the "low" and "high" values using the
dtocean-dummy command prompt tool. Instead, the tool locates this information
in a configuration file.

If dtocean-dummy has never been run before, no configuration file will have
been created. Running dtocean-dummy will create one.

Within the config folder is a file called "configuration.ini" and this file
is examined by dtocean-dummy when it is run. Open the file in your `favourite
text editor <http://notepad-plus-plus.org/>`__. It should look like this:

.. code:: ini

    # Configuration file for dtocean_dummy

    # This section is for configuring the high and low values of the Spreadsheet
    # random numbers
    [Spreadsheet]
    high = 1.0
    low = 0.0
    
The above file has a section called Spreadsheet and two parameters called 
high and low. These correspond to the low and high arguments to the Spreadsheet
__call__ method. Thus, if we set the following configuration:

.. code:: ini

    [Spreadsheet]
    high = 10.0
    low = 0.0
    
Now save the file and run

.. code:: bash

    dtocean-dummy 5
    
The result should be a table where the first column has 5 
values ranging from 0 to 10.

The python module used to read this configuration file is called
`configobj <https://pypi.python.org/pypi/configobj>`__. A group of helper classes for creating and reading
configuration files are found in the configuration.py file of the 
dtocean-dummy-module source code. Specifically, the class 
:class:`dtocean_dummy.configuration.ReadINI` is used to copy, read and test
the configuration file for dtocean-dummy.

Logging
=======

The dtocean-dummy-module is configured to use the standard Python
:py:mod:`logging` module, throughout the system. The configuration of the 
logging module can, in fact, be altered by modifying the logging.yaml file
found in the user configuration directory, discussed in the section above.

The logging system for the demo package is configured by default to create 
a file called dtocean-dummy.log in the directory that dtocean-dummy is run 
from. This behaviour can be modified in logging.yaml but **do not** use a 
different name to "dtocean_dummy" for the main logger. If this is changed
the logging for each sub-module will not inherit the configuration set in
the file.

Within the source code, the creating of a log message is achieved with
something like this:

.. code:: python

    import logging
    
    module_logger = logging.getLogger(__name__)

    def log_info(message):
    
        module_logger.info(message)
        
        return

Here "__name__" is used to automatically name the logger with the module
name. The log messages created by the above function are at the INFO level,
i.e. useful info. A list of the available levels is:

* CRITICAL
* ERROR
* WARNING
* INFO
* DEBUG
* NOTSET

The way and how these messages are delivered can vary from level to level,
so debug messages may go to a file, for instance, and info messages may be
printed on the console and go to the file.

Further useful information about setting up and configuring the python logging
system can be found on the following pages:

- `Logging HOWTO <https://docs.python.org/2/howto/logging.html>`__
- `Good logging practice in Python 
  <http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python>`__
  
Documentation
=============

The DTOcean project has decided to use the Sphinx documentation system 
combined with Google Code Python docstrings. The following pages provide an
overview of these concepts and the specific software requirements:

- `Documenting Your Project Using Sphinx
  <https://pythonhosted.org/an_example_pypi_project/sphinx.html>`__
- `Napoleon - Marching toward legible docstrings
  <http://sphinxcontrib-napoleon.readthedocs.org/en/latest/>`__
  
The documentation for this package is hosted online at `Read the Docs 
<https://readthedocs.org/>`__. This is a free service that builds the
Sphinx documentation of your package automatically by downloading it from
a repository source.

The documentation can be also be built from the local source code, by running
the command

.. code:: bash

    sphinx-build -v -b html source build
    
in the "doc" directory of the source code. Note, it may be necessary to have
installed the package prior to building the documentation.

Sphinx with Python is normally an amalgamation of *two parts*. The first is the
standard Sphinx formatting system which uses `ReStructuredText
<http://es.wikipedia.org/wiki/ReStructuredText>`__ (ReST) files in a similar way to
LaTeX to generate pleasantly formatted documentation in html, pdf etc format.

This documentation page has been written in ReST format, and the source of the last
paragraph looks like this:

.. code:: rest

   Sphinx with Python is normally an amalgamation of *two parts*. The first is the
   standard Sphinx formatting system which uses `ReStructuredText
   <http://es.wikipedia.org/wiki/ReStructuredText>`__ (ReST) files in a similar way to
   LaTeX to generate pleasantly formatted documentation in html, pdf etc format.
   
The second feature is extremely powerful and has been one of the key reasons
for adopting Sphinx as the defacto Python documentation generator. This is
the *autodoc* feature of Sphinx that will read the Python package source codes
and automatically generate documentation from the docstrings of the modules,
classes and functions in the code.

Python `docstrings <http://en.wikipedia.org/wiki/Docstring#Python>`__ are
extremely important as these provide information to the user of the package
as the functions of the packages. These are normally invoked using Python's
built-in "help" function. For instance to see the docstrings for the 
:class:`dtocean_dummy.main.Spreadsheet` class, issue the commands:

.. code:: pycon

    from dtocean_dummy import Spreadsheet
    help(Spreadsheet)
    
The formatting of the docstrings shown here uses the Google Code Python
conventions. There are a few conventions that can be used to create docstrings
but this one is recommended by the
`Khan Academy
<https://github.com/Khan/style-guides/blob/master/style/python.md>`__. Previously, the requirements of
Sphinx meant that the formatting of docstrings were somewhat ugly, but now
the `Napoleon extension
<http://sphinxcontrib-napoleon.readthedocs.org/en/latest/>`__ means that
google code docstrings are also compatible, allowing both attractive docstrings
and this powerful documentation system to be used together.

The *autodoc* function of Sphinx is also capable of reading Python docstrings
and embedding them within the documentation to be produced. The links to the
API reference of classes such as :class:`dtocean_dummy.main.Spreadsheet` are
only capable because of this functionality.

Finally, an example of a Google style docstring is taken from the Spreadsheet
class once again. This is the description of the class and its __init__ 
function:

.. code:: python

    class Spreadsheet(object):
        
        '''Create spreadsheets of random numbers and write to file.
        
        Args:
          low (float, optional): Minimum value of random numbers (inclusive).
            Defaults to 0.
          high (float, optional): Maximum value of random numbers (exclusive).
            Defaults to 1.
        
        Attributes:
          table (pandas.DataFrame): Pandas dataframe containing spreadsheet data.
          low (float): Minimum value of random numbers (inclusive).
          high (float): Maximum value of random numbers (exclusive).
        '''
        
        # Valid formats
        _valid_formats = set(['csv', 'xls'])
        
        def __init__(self, low=0., high=1.):
        
            self.table = None
            self.low = low
            self.high = high
                    
            return
    
        ...

        

Testing
=======

The dtocean dummy module uses a testing framework package called 
`py.test <http://pytest.org/>`__ to verifying the functionality of the 
code and check for negative impacts of code changes. 

The tests are written in files placed in the *test*
folder of the source code. The basic usage of this package is to run the
command

.. code:: bash

    py.test
    
in the root directory of the source code. Note that the demo package must be 
installed before running the tests. One test is set to deliberately fail to 
show the output, but all other tests should pass. 

Each test is prepared by the developer to test the correctness of one 
isolated operation. For instance, observe the following test of one
of the Spreadsheet class methods:

.. code:: python

    def test_array_size(sheet):
        '''Test that the random array size is as requested.'''
        
        assert len(sheet._get_random_array(10)) == 10
        
Here we are simply testing if the random numpy array we have requested is
of the anticipated size. Although this is trivial, it demonstrates the
premise of designing functions with a single clearly defined output
that can be easily tested, using such a framework.
 
Strict test driven development is very rigid, requiring each test to be designed before 
the function is created. I prefer a more relaxed approach, using tests to help 
solve bugs, for instance. If a bug has appeared, then we know an unexpected 
solution is being produced. If we then create a test for the correct solution, 
at the final or intermediate stage, we can isolate the bug and verify that it 
has been solved. Also, once tested, the same bug can never return undetected,
should the algorithm have changed for some reason as the test becomes part of
a suite which is repeated rerun.

Not all of the tests in this demo package are for demonstration, some were
created to expose and solve real bugs that appeared even in this simplistic
application. Thus, the value of testing for more complicated systems should
be obvious.

Finally, for a gentle introduction to py.test and unit tests in general, I recommend
the following references:
 
`Why I use py.test and you probably should too 
<http://halfcooked.com/presentations/pyconau2013/why_I_use_pytest.html>`__

`Improve Your Python: Understanding Unit Testing
<http://www.jeffknupp.com/blog/2013/12/09/improve-your-python-understanding-unit-testing/>`__

Packaging
=========

The dtocean dummy module is packaged using `setuptools
<https://pythonhosted.org/setuptools/>`__ and also using
`conda build <http://conda.pydata.org/docs/build.html>`__ with the
`binstar <https://binstar.org>`__ service. 

Packaging is extremely useful if the developer wants to share their code
with the outside world as it allows the user to easily install complex
programs without *too* much prior knowledge.

The classic methodology for a user to install a packaged python application
is:

.. code:: bash

    python setup.py install
    
called from the source directory. For this to work the developer must create 
a setup.py file in the root of the package. The content of this file varies
from package to package, but the one for this demo looks something like this:

.. code:: python

    from setuptools import setup

    setup(name='dtocean-dummy-module',
          version='1.0.0',
          description='dtocean-dummy.py: Demo package for DTOcean modules',
          author='Mathew Toppper',
          author_email='mathew.topper@tecnalia.com',
          packages=['dtocean_dummy'],
          install_requires=[
              'configobj',
              'numpy',
              'pandas',
              'pyyaml',
              'xlwt'
          ],
          entry_points={
              'console_scripts':
                  [
                   'dtocean-dummy = dtocean_dummy.command:module_interface'
                   ]},
          zip_safe=False,
          package_data={'dtocean_dummy': ['*.ini', 'config/*.ini', 'config/*.yaml']
                        }
          )
          
An introduction to files like this can be found at the `The Hitchhiker's Guide
to Packaging <http://the-hitchhikers-guide-to-packaging.readthedocs.org/en/latest/>`__
which gives a good overview of what useful stuff this file can do (like
working with dependencies, creating command line scripts called entry points
and other exciting stuff).

Alternatively, the demo package also can be installed using conda, the package manager for
`Anaconda <https://store.continuum.io/cshop/anaconda/>`__ . This allows an
easy installation process for the user, who will be familiar with the command

.. code:: bash

    conda install some-package
    
Conda will download all dependencies and these will work correctly with
eachother (something that is not always possible with the setuptools approach).

Building a package for Anaconda is somewhat more complex, however, requiring
a "recipe", a Binstar account, and the removing of repeated code in the
setup.py file. This leads to requiring an additional "branch" to maintain
the conda / Binstar version of this package.

Users are invited to inspect the recipe folder found in the source tree of the
"binstar" branch of this application. Without going into great detail, further
information about creating these recipes can be found at:

`conda build Recipe Reference <http://conda.pydata.org/docs/build.html>`__

`Uploading a Conda Package
<http://binstar-client.readthedocs.org/en/latest/getting_started.html>`__

