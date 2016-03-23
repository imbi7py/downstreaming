# Downstream Review Service

Initial downstream reviews of open source projects being
considered for redistribution.

Provides human sign-off of the following characteristics:

* project appears to published in good faith
* project appears to be benign

Depending on your background, one potentially useful way to think of
downstreaming is as a simple supplier management system specifically for
open source projects.

(Originally forked from Fedora Infrastructure's Fresque review
service)

# Future objectives

Downstreaming currently aims to handle reviewing individual projects directly.
In the future, I'd like to introduce the notion of a "Publisher" (separately
from projects) such that software publishers can be reviewed for possible
"auto-approval" (or "auto-rejection") status for the projects they publish,
and projects can be automatically flagged for reassessment if their Publisher
information changes.

(Note that a publisher in this sense is the entity granting the right to
deploy and use their software, not the entity providing the publishing platform
they happen to be using for distribution)

# Initial Developer setup

Clone downstreaming from GitHub:

    $ git clone https://github.com/ncoghlan/downstreaming.git

Fork the repo on GitHub and add a new remote to use to submit PRs:

    $ cd downstreaming
    $ git remote add pr git@github.com:<your GitHub ID>/downstreaming.git

Downstreaming is a Flask application which can be run locally in a Python
virtual environment. If you don't already have a preferred tool for managing
those, I recommend using vex to create and manage it:

    $ pip install --user vex
    $ vex -m downstreaming

To start the environment again later:

    $ vex downstreaming

Unlike some other environment management tools, vex environments run as
subshells rather than altering the current shell environment.

With the virtual environment active, install downstreaming's dependencies:

    (downstreaming) $ pip install -r requirements.txt
    (downstreaming) $ pip install -r requirements-dev.txt

These same two commands are also used to update the dependencies when they
change.

Create the local SQLite database:

    (downstreaming) $ python createdb.py

If needed or desired, the database can be recreated later:

    (downstreaming) $ rm downstreaming.sqlite
    (downstreaming) $ python createdb.py


# Local development activities

Running a local dev instance accessible only via the loopback interface:

    (downstreaming) $ ./runserver.py

Any changes made to source code and templates should be picked up automatically
when saved to disk, although syntax errors may cause the instance to crash
and need to be restarted.

Running a local dev instance inside Vagrant or a Docker container so it's
accessible from the host:

    (downstreaming) $ ./runserver.py --public

The dev server only binds to the loopback instance by default, so it needs to
be told to also bind to the host bridge when running in a Docker container
or virtual machine.

Running pylint:

    (downstreaming) $ pylint downstreaming

Running the unit tests sadly isn't possible yet, as there aren't any (they'll
probably arrive at the same time a REST API does)
