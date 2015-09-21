.. _installation:

Installation
============

Babel is distributed as a standard Python package fully set up with all
the dependencies it needs.  It primarily depends on the excellent `pytz`_
library for timezone handling.  To install it you can use ``easy_install``
or ``pip``.

.. _pytz: http://pytz.sourceforge.net/

.. _virtualenv:

virtualenv
----------

Virtualenv is probably what you want to use during development, and if you
have shell access to your production machines, you'll probably want to use
it there, too.

If you are on Mac OS X or Linux, chances are that one of the following two
commands will work for you::

    $ sudo easy_install virtualenv

If you are on Windows and don't have the `easy_install` command, you must
install it first.  Check the :ref:`windows-easy-install` section for more
information about how to do that.  Once you have it installed, run the same
commands as above, but without the `sudo` prefix.

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

If `pip` is not available on your system you can use `easy_install`.

(On Windows systems, run it in a command-prompt window with administrator
privileges, and leave out `sudo`.)


Living on the Edge
------------------

If you want to work with the latest version of Babel, you will need to
use a git checkout.

Get the git checkout in a new virtualenv and run in development mode::

    $ git clone http://github.com/python-babel/babel.git
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
you will be missing the locale data.  This custom command will download
the most appropriate CLDR release from the official website and convert it
for Babel.

This will pull also in the dependencies and activate the git head as the
current version inside the virtualenv.  Then all you have to do is run
``git pull origin`` to update to the latest version.  If the CLDR data
changes you will have to re-run ``python setup.py import_cldr``.

.. _windows-easy-install:

`pip` and `distribute` on Windows
-----------------------------------

On Windows, installation of `easy_install` is a little bit trickier, but
still quite easy.  The easiest way to do it is to download the
`distribute_setup.py`_ file and run it.  The easiest way to run the file
is to open your downloads folder and double-click on the file.

Next, add the `easy_install` command and other Python scripts to the
command search path, by adding your Python installation's Scripts folder
to the `PATH` environment variable.  To do that, right-click on the
"Computer" icon on the Desktop or in the Start menu, and choose "Properties".
Then click on "Advanced System settings" (in Windows XP, click on the
"Advanced" tab instead).  Then click on the "Environment variables" button.
Finally, double-click on the "Path" variable in the "System variables" section,
and add the path of your Python interpreter's Scripts folder. Be sure to
delimit it from existing values with a semicolon.  Assuming you are using
Python 2.7 on the default path, add the following value::


    ;C:\Python27\Scripts

And you are done!  To check that it worked, open the Command Prompt and execute
``easy_install``.  If you have User Account Control enabled on Windows Vista or
Windows 7, it should prompt you for administrator privileges.

Now that you have ``easy_install``, you can use it to install ``pip``::

    > easy_install pip


.. _distribute_setup.py: http://python-distribute.org/distribute_setup.py
