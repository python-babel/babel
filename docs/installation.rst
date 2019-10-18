.. _installation:

Installation
============

Babel is distributed as a standard Python package fully set up with all
the dependencies it needs.  It primarily depends on the excellent `pytz`_
library for timezone handling.  To install it you can use ``pip``.

.. _pytz: http://pytz.sourceforge.net/

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
    $ pip install pytz
    $ python setup.py import_cldr
    $ pip install --editable .
    ...
    Finished processing dependencies for Babel

Make sure to not forget about the ``pip install pytz`` and ``import_cldr`` steps
because otherwise you will be missing the locale data.  
The custom setup command will download the most appropriate CLDR release from the
official website and convert it for Babel but will not work without ``pytz``.

This will pull also in the dependencies and activate the git head as the
current version inside the virtualenv.  Then all you have to do is run
``git pull origin`` to update to the latest version.  If the CLDR data
changes you will have to re-run ``python setup.py import_cldr``.
