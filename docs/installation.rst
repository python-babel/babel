.. _installation:

Installation
============

Babel is distributed as a standard Python package fully set up with all
the dependencies it needs.  On Python versions where the standard library
`zoneinfo`_ module is not available, `pytz`_  needs to be installed for
timezone support. If `pytz`_  is installed, it is preferred over the
standard library `zoneinfo`_  module where possible.

.. _pytz: https://pythonhosted.org/pytz/

.. _zoneinfo: https://docs.python.org/3/library/zoneinfo.html

.. _virtualenv:

virtualenv
----------

Virtualenv is probably what you want to use during development, and if you
have shell access to your production machines, you'll probably want to use
it there, too.  Use ``pip`` to install it::

    $ sudo pip install virtualenv

If you're on Windows, run it in a command-prompt window with administrator
privileges, and leave out ``sudo``.

Once you have virtualenv installed, just fire up a shell and create
your own environment.  I usually create a project folder and a `venv`
folder within::

    $ mkdir myproject
    $ cd myproject
    $ virtualenv venv
    New python executable in venv/bin/python
    Installing distribute............done.

Now, whenever you want to work on a project, you only have to activate the
corresponding environment.  On OS X and Linux, do the following::

    $ . venv/bin/activate

If you are a Windows user, the following command is for you::

    $ venv\scripts\activate

Either way, you should now be using your virtualenv (notice how the prompt of
your shell has changed to show the active environment).

Now you can just enter the following command to get Babel installed in your
virtualenv::

    $ pip install Babel

A few seconds later and you are good to go.

System-Wide Installation
------------------------

This is possible as well, though I do not recommend it.  Just run `pip`
with root privileges::

    $ sudo pip install Babel

(On Windows systems, run it in a command-prompt window with administrator
privileges, and leave out `sudo`.)


Living on the Edge
------------------

If you want to work with the latest version of Babel, you will need to
use a git checkout.

Get the git checkout in a new virtualenv and run in development mode::

    $ git clone https://github.com/python-babel/babel
    Initialized empty Git repository in ~/dev/babel/.git/
    $ cd babel
    $ virtualenv venv
    New python executable in venv/bin/python
    Installing distribute............done.
    $ . venv/bin/activate
    $ python setup.py import_cldr
    $ pip install --editable .
    ...
    Finished processing dependencies for Babel

Make sure to not forget about the ``import_cldr`` step because otherwise
you will be missing the locale data.
The custom setup command will download the most appropriate CLDR release from the
official website and convert it for Babel.

This will pull also in the dependencies and activate the git head as the
current version inside the virtualenv.  Then all you have to do is run
``git pull origin`` to update to the latest version.  If the CLDR data
changes you will have to re-run ``python setup.py import_cldr``.
