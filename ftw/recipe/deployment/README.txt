Example usage
=============

First we create a fake ``plone.recipe.zope2instance`` recipe, which we can
use in our tests.

Create a recipes source directory::

    >>> mkdir(sample_buildout, 'plone.recipe.zope2instance')

and then create a source file with the fake recipe::

    >>> write(sample_buildout, 'plone.recipe.zope2instance',
    ...       'zope2instance.py',
    ... """
    ... import os, zc.buildout
    ...
    ... class Recipe(object):
    ...
    ...     def __init__(self, buildout, name, options):
    ...         self.name, self.options = name, options
    ...         options['event-log'] = os.path.join(
    ...                               buildout['buildout']['directory'],
    ...                               'var', 'log', self.name + '.log'
    ...                               )
    ...         options['z2-log'] = os.path.join(
    ...                               buildout['buildout']['directory'],
    ...                               'var', 'log', self.name + '-Z2.log'
    ...                               )
    ...
    ...     def install(self):
    ...         return tuple()
    ...
    ...     def update(self):
    ...         pass
    ... """)

Provide packaging information so that the recipe can be installed as a develop
egg::

    >>> write(sample_buildout, 'plone.recipe.zope2instance', 'setup.py',
    ... """
    ... from setuptools import setup
    ...
    ... setup(
    ...     name = "plone.recipe.zope2instance",
    ...     entry_points = {'zc.buildout': ['default = zope2instance:Recipe']},
    ...     )
    ... """)

Add a README.txt to avoid an annoying warning from distutils::

    >>> write(sample_buildout, 'plone.recipe.zope2instance', 'README.txt', " ")

We'll start by creating a simple buildout that uses our recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop = plone.recipe.zope2instance
    ... parts = instance1 deployment
    ...
    ... [instance1]
    ... recipe = plone.recipe.zope2instance
    ...
    ... [deployment]
    ... recipe = ftw.recipe.deployment
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Develop: '/sample-buildout/plone.recipe.zope2instance'
    Installing instance1.
    Installing deployment.
    <BLANKLINE>

We should now have a file with the same name as our buildout directory
containing our logrotate configuration::

    >>> cat(sample_buildout, 'etc', 'logrotate.d', 'sample-buildout')
    /sample-buildout/var/log/instance1.log
    /sample-buildout/var/log/instance1-Z2.log {
        sharedscripts
        postrotate
            /bin/kill -SIGUSR2 `cat /sample-buildout/var/instance1.pid` >/dev/null 2>&1
        endscript
    }

We should also have a run-control script for instance1::

    >>> cat(sample_buildout, 'bin', 'rc-instance1')
    #!/bin/sh
    <BLANKLINE>
    # chkconfig: 345 90 10
    # description: Starts Zope
    <BLANKLINE>
    START_SCRIPT="/sample-buildout/bin/instance1"
    <BLANKLINE>
    [ -f $START_SCRIPT ] || exit 1
    <BLANKLINE>
    # Source function library.
    . /etc/init.d/functions
    <BLANKLINE>
    RETVAL=0
    <BLANKLINE>
    if [ $(whoami) != "root" ]; then
        echo "You must be root."
        exit 1
    fi
    <BLANKLINE>
    case $1 in
        start|stop)
            su zope -c "$START_SCRIPT $*" </dev/null
            RETVAL=$?
            if [ $RETVAL -eq 0 ]
            then
                echo_success
            else
                echo_failure
            fi
            echo
            ;;
        restart)
            ${0} stop
            sleep 1
            ${0} start
            ;;
        *)
            su zope -c "$START_SCRIPT $*" </dev/null
            ;;
    esac


Let's also add a zeo part. Thus we first need a fake ``plone.recipe.zeoserver``
recipe::

    >>> mkdir(sample_buildout, 'plone.recipe.zeoserver')
    >>> write(sample_buildout, 'plone.recipe.zeoserver', 'zeoserver.py',
    ... """
    ... import os, zc.buildout
    ...
    ... class Recipe(object):
    ...
    ...     def __init__(self, buildout, name, options):
    ...         self.name, self.options = name, options
    ...         options['zeo-log'] = os.path.join(
    ...                               buildout['buildout']['directory'],
    ...                               'var', 'log', self.name + '.log'
    ...                               )
    ...
    ...     def install(self):
    ...         return tuple()
    ...
    ...     def update(self):
    ...         pass
    ... """)
    >>> write(sample_buildout, 'plone.recipe.zeoserver', 'setup.py',
    ... """
    ... from setuptools import setup
    ...
    ... setup(
    ...     name = "plone.recipe.zeoserver",
    ...     entry_points = {'zc.buildout': ['default = zeoserver:Recipe']},
    ...     )
    ... """)
    >>> write(sample_buildout, 'plone.recipe.zeoserver', 'README.txt', " ")

Create a buildout with multiple instance parts and a zeo part::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop = plone.recipe.zope2instance plone.recipe.zeoserver
    ... parts = instance1 instance2 zeo deployment
    ...
    ... [instance1]
    ... recipe = plone.recipe.zope2instance
    ...
    ... [instance2]
    ... <= instance1
    ...
    ... [zeo]
    ... recipe = plone.recipe.zeoserver
    ...
    ... [deployment]
    ... recipe = ftw.recipe.deployment
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Develop: '/sample-buildout/plone.recipe.zope2instance'
    Develop: '/sample-buildout/plone.recipe.zeoserver'
    Updating instance1.
    Installing instance2.
    Installing zeo.
    Updating deployment.
    <BLANKLINE>

Verify the contents of the logrotate configuration file::

    >>> cat(sample_buildout, 'etc', 'logrotate.d', 'sample-buildout')
    /sample-buildout/var/log/instance1.log
    /sample-buildout/var/log/instance1-Z2.log {
        sharedscripts
        postrotate
            /bin/kill -SIGUSR2 `cat /sample-buildout/var/instance1.pid` >/dev/null 2>&1
        endscript
    }
    /sample-buildout/var/log/instance2.log
    /sample-buildout/var/log/instance2-Z2.log {
        sharedscripts
        postrotate
            /bin/kill -SIGUSR2 `cat /sample-buildout/var/instance2.pid` >/dev/null 2>&1
        endscript
    }
    /sample-buildout/var/log/zeo.log {
        copytruncate
    }

Verify the zeo run control script::

    >>> cat(sample_buildout, 'bin', 'rc-zeo')
    #!/bin/sh
    <BLANKLINE>
    # chkconfig: 345 85 15
    # description: Starts ZEO server
    <BLANKLINE>
    START_SCRIPT="/sample-buildout/bin/zeo"
    <BLANKLINE>
    [ -f $START_SCRIPT ] || exit 1
    <BLANKLINE>
    # Source function library.
    . /etc/init.d/functions
    <BLANKLINE>
    RETVAL=0
    <BLANKLINE>
    if [ $(whoami) != "root" ]; then
        echo "You must be root."
        exit 1
    fi
    <BLANKLINE>
    case $1 in
        start|stop)
            su zope -c "$START_SCRIPT $*" </dev/null
            RETVAL=$?
            if [ $RETVAL -eq 0 ]
            then
                echo_success
            else
                echo_failure
            fi
            echo
            ;;
        restart)
            ${0} stop
            sleep 1
            ${0} start
            ;;
        *)
            su zope -c "$START_SCRIPT $*" </dev/null
            ;;
    esac

Verify the run control script for instance 2::

    >>> cat(sample_buildout, 'bin', 'rc-instance2')
    #!/bin/sh
    <BLANKLINE>
    # chkconfig: 345 90 10
    # description: Starts Zope
    <BLANKLINE>
    START_SCRIPT="/sample-buildout/bin/instance2"
    <BLANKLINE>
    [ -f $START_SCRIPT ] || exit 1
    <BLANKLINE>
    # Source function library.
    . /etc/init.d/functions
    <BLANKLINE>
    RETVAL=0
    <BLANKLINE>
    if [ $(whoami) != "root" ]; then
        echo "You must be root."
        exit 1
    fi
    <BLANKLINE>
    case $1 in
        start|stop)
            su zope -c "$START_SCRIPT $*" </dev/null
            RETVAL=$?
            if [ $RETVAL -eq 0 ]
            then
                echo_success
            else
                echo_failure
            fi
            echo
            ;;
        restart)
            ${0} stop
            sleep 1
            ${0} start
            ;;
        *)
            su zope -c "$START_SCRIPT $*" </dev/null
            ;;
    esac

Before we can add a supervisor part we need a fake recipe for it::

    >>> mkdir(sample_buildout, 'collective.recipe.supervisor')
    >>> write(sample_buildout, 'collective.recipe.supervisor', 'supervisor.py',
    ... """
    ... import os, zc.buildout
    ...
    ... class Recipe(object):
    ...
    ...     def __init__(self, buildout, name, options):
    ...         pass
    ...
    ...     def install(self):
    ...         return tuple()
    ...
    ...     def update(self):
    ...         pass
    ... """)
    >>> write(sample_buildout, 'collective.recipe.supervisor', 'setup.py',
    ... """
    ... from setuptools import setup
    ...
    ... setup(
    ...     name = "collective.recipe.supervisor",
    ...     entry_points = {'zc.buildout': ['default = supervisor:Recipe']},
    ...     )
    ... """)
    >>> write(sample_buildout, 'collective.recipe.supervisor', 'README.txt',
    ... " ")

Create a buildout with a supervisor part::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop =
    ...     plone.recipe.zope2instance
    ...     plone.recipe.zeoserver
    ...     collective.recipe.supervisor
    ... parts = instance1 instance2 zeo supervisor deployment
    ...
    ... [instance1]
    ... recipe = plone.recipe.zope2instance
    ...
    ... [instance2]
    ... <= instance1
    ...
    ... [zeo]
    ... recipe = plone.recipe.zeoserver
    ...
    ... [supervisor]
    ... recipe = collective.recipe.supervisor
    ...
    ... [deployment]
    ... recipe = ftw.recipe.deployment
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Develop: '/sample-buildout/plone.recipe.zope2instance'
    Develop: '/sample-buildout/plone.recipe.zeoserver'
    Develop: '/sample-buildout/collective.recipe.supervisor'
    Updating instance1.
    Updating instance2.
    Updating zeo.
    Installing supervisor.
    Updating deployment.
    <BLANKLINE>

Verify the supervisor control script::

    >>> cat(sample_buildout, 'bin', 'rc-supervisor')
    #!/bin/sh
    <BLANKLINE>
    # chkconfig: 345 90 10
    # description: Starts supervisor
    <BLANKLINE>
    SUPERVISORCTL="/sample-buildout/bin/supervisorctl"
    SUPERVISORD="/sample-buildout/bin/supervisord"
    <BLANKLINE>
    [ -f $SUPERVISORD ] || exit 1
    [ -f $SUPERVISORCTL ] || exit 1
    <BLANKLINE>
    # Source function library.
    . /etc/init.d/functions
    <BLANKLINE>
    RETVAL=0
    <BLANKLINE>
    if [ $(whoami) != "root" ]; then
        echo "You must be root."
        exit 1
    fi
    <BLANKLINE>
    start() {
        echo -n "Starting supervisor: "
        su zope -c "$SUPERVISORD"
        RETVAL=$?
        if [ $RETVAL -eq 0 ]; then
            echo_success
        else
            echo_failure
        fi
        return $RETVAL
    }
    <BLANKLINE>
    stop() {
        echo -n "Stopping supervisor: "
        su zope -c "$SUPERVISORCTL shutdown"
        RETVAL=$?
        if [ $RETVAL -eq 0 ]; then
            echo_success
        else
            echo_failure
        fi
        return $RETVAL
    }
    <BLANKLINE>
    case "$1" in
        start)
            start
            ;;
    <BLANKLINE>
        stop)
            stop
            ;;
    <BLANKLINE>
        restart)
            stop
            start
            ;;
    esac
    <BLANKLINE>
    exit $REVAL
