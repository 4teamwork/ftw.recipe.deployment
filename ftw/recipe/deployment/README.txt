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
    ... #doctest: -NORMALIZE_WHITESPACE
    /sample-buildout/var/log/instance1.log
    /sample-buildout/var/log/instance1-Z2.log {
        sharedscripts
        postrotate
            /bin/kill -SIGUSR2 `cat /sample-buildout/var/instance1.pid 2>/dev/null` >/dev/null 2>&1 || true
        endscript
    }
    /sample-buildout/var/log/instance1-json.log {
        copytruncate
        missingok
    }

We should also have a run-control script for instance1::

    >>> ls(sample_buildout, 'bin')
    - buildout
    - rc-instance1

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

We should also have a filebeat prospectors config for your deployment::

    >>> cat(sample_buildout, 'etc', 'filebeat.d', 'sample-buildout.yml')
    ... #doctest: -NORMALIZE_WHITESPACE
    - type: log
      fields:
        event_type: contentstats
        deployment: sample-buildout
      fields_under_root: true
      json.keys_under_root: true
      json.add_error_key: true
      paths:
        - /sample-buildout/var/log/contentstats-json.log
    - type: log
      fields:
        event_type: structlog
        deployment: sample-buildout
      fields_under_root: true
      json.keys_under_root: true
      json.add_error_key: true
      paths:
        - /sample-buildout/var/log/instance1-json.log

Except if we specifically disable creation of the filebeat config::

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
    ... create-filebeat-config = false
    ... """)

And then run buildout again::

    >>> print system(buildout)
    Develop: '/sample-buildout/plone.recipe.zope2instance'
    Uninstalling deployment.
    Updating instance1.
    Installing deployment.
    <BLANKLINE>

We should NOT have a filebeat config for our deployment::

    >>> import os
    >>> os.path.isfile(os.path.join(sample_buildout, 'etc', 'filebeat.d', 'sample-buildout.yml'))
    False

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
    ...         self.storage_number = options.get('storage-number', '1')
    ...         self.blob_storage = options.get('blob-storage', '')
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
    Uninstalling deployment.
    Updating instance1.
    Installing instance2.
    Installing zeo.
    Installing deployment.
    <BLANKLINE>

Verify the contents of the logrotate configuration file::

    >>> cat(sample_buildout, 'etc', 'logrotate.d', 'sample-buildout')
    /sample-buildout/var/log/instance1.log
    /sample-buildout/var/log/instance1-Z2.log {
        sharedscripts
        postrotate
            /bin/kill -SIGUSR2 `cat /sample-buildout/var/instance1.pid 2>/dev/null` >/dev/null 2>&1 || true
        endscript
    }
    /sample-buildout/var/log/instance2.log
    /sample-buildout/var/log/instance2-Z2.log {
        sharedscripts
        postrotate
            /bin/kill -SIGUSR2 `cat /sample-buildout/var/instance2.pid 2>/dev/null` >/dev/null 2>&1 || true
        endscript
    }
    /sample-buildout/var/log/zeo.log {
        copytruncate
    }
    /sample-buildout/var/log/instance1-json.log {
        copytruncate
        missingok
    }
    /sample-buildout/var/log/instance2-json.log {
        copytruncate
        missingok
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

We should also have a packall script for packing all databases::

    >>> cat(sample_buildout, 'bin', 'packall')
    #!/bin/sh
    /sample-buildout/bin/zeopack -S 1 -B /sample-buildout/var/blobstorage \
        && echo `date +%Y-%m-%dT%H:%M:%S%z` "packed Data (blobstorage)" >> /sample-buildout/var/log/pack.log

We can specify the user that should be used to run processes::

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
    ... rc-user = plone
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Develop: '/sample-buildout/plone.recipe.zope2instance'
    Develop: '/sample-buildout/plone.recipe.zeoserver'
    Uninstalling deployment.
    Updating instance1.
    Updating instance2.
    Updating zeo.
    Installing deployment.
    <BLANKLINE>

Verify the run control script for instance 1::

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
            su plone -c "$START_SCRIPT $*" </dev/null
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
            su plone -c "$START_SCRIPT $*" </dev/null
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
    ... rc-user = plone
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
        su plone -c "$SUPERVISORD"
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
        su plone -c "$SUPERVISORCTL shutdown"
        RETVAL=$?
        if [ $RETVAL -eq 0 ]; then
            echo_success
        else
            echo_failure
        fi
        return $RETVAL
    }
    <BLANKLINE>
    status() {
        su plone -c "$SUPERVISORCTL status"
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
    <BLANKLINE>
        status)
            status
            ;;
    esac
    <BLANKLINE>
    exit $REVAL

We can provide some additional logrotate options::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop =
    ...     plone.recipe.zope2instance
    ...     plone.recipe.zeoserver
    ...     collective.recipe.supervisor
    ...
    ... parts = instance1 deployment
    ...
    ... [instance1]
    ... recipe = plone.recipe.zope2instance
    ...
    ... [deployment]
    ... recipe = ftw.recipe.deployment
    ... logrotate-options =
    ...     rotate 4
    ...     weekly
    ...     missingok
    ...     notifempty
    ...     nomail
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Develop: '/sample-buildout/plone.recipe.zope2instance'
    Develop: '/sample-buildout/plone.recipe.zeoserver'
    Develop: '/sample-buildout/collective.recipe.supervisor'
    Uninstalling deployment.
    Uninstalling supervisor.
    Uninstalling zeo.
    Uninstalling instance2.
    Updating instance1.
    Installing deployment.
    <BLANKLINE>

Verify that the file contains our logrotate options::

    >>> cat(sample_buildout, 'etc', 'logrotate.d', 'sample-buildout')
    ... #doctest: -NORMALIZE_WHITESPACE
    /sample-buildout/var/log/instance1.log
    /sample-buildout/var/log/instance1-Z2.log {
        rotate 4
        weekly
        missingok
        notifempty
        nomail
        sharedscripts
        postrotate
            /bin/kill -SIGUSR2 `cat /sample-buildout/var/instance1.pid 2>/dev/null` >/dev/null 2>&1 || true
        endscript
    }
    /sample-buildout/var/log/instance1-json.log {
        rotate 4
        weekly
        missingok
        notifempty
        nomail
        copytruncate
    }

We can provide custom storage options::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop = plone.recipe.zope2instance plone.recipe.zeoserver
    ... parts = instance1 zeo deployment
    ...
    ... [instance1]
    ... recipe = plone.recipe.zope2instance
    ...
    ... [zeo]
    ... recipe = plone.recipe.zeoserver
    ... storage-number = main
    ... blob-storage = blobstorage-main
    ...
    ... [deployment]
    ... recipe = ftw.recipe.deployment
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Develop: '/sample-buildout/plone.recipe.zope2instance'
    Develop: '/sample-buildout/plone.recipe.zeoserver'
    Uninstalling deployment.
    Updating instance1.
    Installing zeo.
    Installing deployment.
    <BLANKLINE>

Our packall script should contain the correct storage parameters::

    >>> cat(sample_buildout, 'bin', 'packall')
    #!/bin/sh
    /sample-buildout/bin/zeopack -S main -B /sample-buildout/var/blobstorage-main \
        && echo `date +%Y-%m-%dT%H:%M:%S%z` "packed main (blobstorage-main)" >> /sample-buildout/var/log/pack.log

Let's add a filestorage part. Thus we first need a fake ``collective.recipe.filestorage``
recipe::

    >>> mkdir(sample_buildout, 'collective.recipe.filestorage')
    >>> write(sample_buildout, 'collective.recipe.filestorage', 'filestorage.py',
    ... """
    ... import os, zc.buildout
    ...
    ... class Recipe(object):
    ...
    ...     def __init__(self, buildout, name, options):
    ...         self.name, self.options = name, options
    ...         self.subparts = options.get('parts', '').split()
    ...
    ...     def install(self):
    ...         return tuple()
    ...
    ...     def update(self):
    ...         pass
    ... """)
    >>> write(sample_buildout, 'collective.recipe.filestorage', 'setup.py',
    ... """
    ... from setuptools import setup
    ...
    ... setup(
    ...     name = "collective.recipe.filestorage",
    ...     entry_points = {'zc.buildout': ['default = filestorage:Recipe']},
    ...     )
    ... """)
    >>> write(sample_buildout, 'collective.recipe.filestorage', 'README.txt', " ")

Create a buildout with a filestorage part::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop = plone.recipe.zope2instance plone.recipe.zeoserver collective.recipe.filestorage
    ... parts = instance1 zeo filestorage deployment
    ...
    ... [instance1]
    ... recipe = plone.recipe.zope2instance
    ...
    ... [zeo]
    ... recipe = plone.recipe.zeoserver
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... parts = storage1
    ...
    ... [deployment]
    ... recipe = ftw.recipe.deployment
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Develop: '/sample-buildout/plone.recipe.zope2instance'
    Develop: '/sample-buildout/plone.recipe.zeoserver'
    Develop: '/sample-buildout/collective.recipe.filestorage'
    Uninstalling zeo.
    Updating instance1.
    Installing zeo.
    Installing filestorage.
    Updating deployment.
    <BLANKLINE>

Our packall script should contain pack commands for all storages::

    >>> cat(sample_buildout, 'bin', 'packall')
    #!/bin/sh
    /sample-buildout/bin/zeopack -S 1 -B /sample-buildout/var/blobstorage  \
        && echo `date +%Y-%m-%dT%H:%M:%S%z` "packed Data (blobstorage)" >> /sample-buildout/var/log/pack.log
    /sample-buildout/bin/zeopack -S storage1 \
        && echo `date +%Y-%m-%dT%H:%M:%S%z` "packed storage1" >> /sample-buildout/var/log/pack.log

Let's create a buildout with multiple filestorages and blobs::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop = plone.recipe.zope2instance plone.recipe.zeoserver collective.recipe.filestorage
    ... parts = instance1 zeo filestorage deployment
    ...
    ... [instance1]
    ... recipe = plone.recipe.zope2instance
    ...
    ... [zeo]
    ... recipe = plone.recipe.zeoserver
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... parts = storage1 storage2
    ... blob-storage = var/blobstorage-%(fs_part_name)s
    ... zeo-storage = %(fs_part_name)s_storage
    ...
    ... [deployment]
    ... recipe = ftw.recipe.deployment
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Develop: '/sample-buildout/plone.recipe.zope2instance'
    Develop: '/sample-buildout/plone.recipe.zeoserver'
    Develop: '/sample-buildout/collective.recipe.filestorage'
    Uninstalling filestorage.
    Updating instance1.
    Updating zeo.
    Installing filestorage.
    Updating deployment.
    <BLANKLINE>

Our packall script should contain pack commands for all storages::

    >>> cat(sample_buildout, 'bin', 'packall')
    #!/bin/sh
    /sample-buildout/bin/zeopack -S 1 -B /sample-buildout/var/blobstorage  \
        && echo `date +%Y-%m-%dT%H:%M:%S%z` "packed Data (blobstorage)" >> /sample-buildout/var/log/pack.log
    /sample-buildout/bin/zeopack -S storage1_storage -B /sample-buildout/var/blobstorage-storage1 \
        && echo `date +%Y-%m-%dT%H:%M:%S%z` "packed storage1_storage (blobstorage-storage1)" >> /sample-buildout/var/log/pack.log
    /sample-buildout/bin/zeopack -S storage2_storage -B /sample-buildout/var/blobstorage-storage2 \
        && echo `date +%Y-%m-%dT%H:%M:%S%z` "packed storage2_storage (blobstorage-storage2)" >> /sample-buildout/var/log/pack.log

Create a buildout with the packall-symlink-directory option::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop = plone.recipe.zope2instance plone.recipe.zeoserver collective.recipe.filestorage
    ... parts = instance1 zeo deployment
    ...
    ... [instance1]
    ... recipe = plone.recipe.zope2instance
    ...
    ... [zeo]
    ... recipe = plone.recipe.zeoserver
    ...
    ... [deployment]
    ... recipe = ftw.recipe.deployment
    ... packall-symlink-directory = etc/zodbpack.d
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Develop: '/sample-buildout/plone.recipe.zope2instance'
    Develop: '/sample-buildout/plone.recipe.zeoserver'
    Develop: '/sample-buildout/collective.recipe.filestorage'
    Uninstalling deployment.
    Uninstalling filestorage.
    Updating instance1.
    Updating zeo.
    Installing deployment.
    <BLANKLINE>

We should now have a symlink in the given directory::

    >>> ls(sample_buildout, 'etc', 'zodbpack.d')
    l  sample-buildout

Create a buildout with startup/shutdown directory option::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop = plone.recipe.zope2instance plone.recipe.zeoserver collective.recipe.supervisor
    ... parts = instance1 zeo supervisor deployment
    ...
    ... [instance1]
    ... recipe = plone.recipe.zope2instance
    ...
    ... [zeo]
    ... recipe = plone.recipe.zeoserver
    ...
    ... [supervisor]
    ... recipe = collective.recipe.supervisor
    ...
    ... [deployment]
    ... recipe = ftw.recipe.deployment
    ... startup-directory = etc/startup.d
    ... shutdown-directory = etc/shutdown.d
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Develop: '/sample-buildout/plone.recipe.zope2instance'
    Develop: '/sample-buildout/plone.recipe.zeoserver'
    Develop: '/sample-buildout/collective.recipe.supervisor'
    Uninstalling deployment.
    Updating instance1.
    Updating zeo.
    Installing supervisor.
    Installing deployment.

Verify the startup script::

    >>> cat(sample_buildout, 'etc', 'startup.d', 'sample-buildout')
    #!/bin/sh
    /sample-buildout/bin/supervisord

Verify the shutdown script::

    >>> cat(sample_buildout, 'etc', 'shutdown.d', 'sample-buildout')
    #!/bin/sh
    /sample-buildout/bin/supervisorctl shutdown
