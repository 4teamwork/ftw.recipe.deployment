.. contents::

Introduction
============

This recipe provides support for configuring various unix services when
deploying Plone/Zope2 with buildout.

As for now the following features are provided:

* Create Logrotate configuration for all Zope 2 instance and ZEO parts,
  as well as ``ftw.structlog`` logfiles.

* Create RedHat-like run-control scripts.

* Create packall script for packing of all storages.

* Create filebeat prospector configs for ``ftw.structlog`` and
  ``ftw.contentstats`` logs.


Supported options
=================

The recipe supports the following options:

logrotate-directory
    The directory where the logrotate configuration file will be created.
    Defaults to ``${buildout:directory}/etc/logrotate.d``. Add this parameter
    with no arguments to supress generation of logrotate configuration.

    If this parameter is set, this recipe will create logrotate configs for
    all Zope 2 instance and ZEO parts that are present, and (unconditionally)
    a logrotate config for ``ftw.structlog`` logfiles.

logrotate-options
    A list of logrotate options that should be added to the logrotate
    configuration.

    Configuration for reopening rotated logfiles is added automatically if
    ``postrotate`` is not specified in ``logrotate-options``.

    Example::

     logrotate-options =
         rotate 4
         weekly
         missingok
         notifempty
         nomail

    The logrotate config for ``ftw.structlog`` logfiles will be created with
    settings similar to the other logfiles, except:

    * No ``postrotate`` script will be automatically inserted if not already
      present in ``logrotate-options``
    * ``missingok`` will always be included
    * Rotation mode will always be ``copytruncate``, and ``nocopytruncate``
      will be ignored

startup-directory
    If specified, a start script is created in the given directory.
    Generation of run-control scripts is disabled if this option is present.

shutdown-directory
    If specified, a shutdown script is created in the given directory.
    Generation of run-control scripts is disabled if this option is present.

rc-directory
    The directory where run-control scripts should be installed.
    Defaults to ``${buildout:directory}/bin``. Add this parameter with no
    arguments to supress generation of run-control scripts.

rc-prefix
    Name prefix for run-control scripts. Defaults to ``rc-``.

rc-user
    The name of the user used to start processes by run-control scripts.
    Defaults to ``zope``.

has-supervisor
    Boolean indication whether supervisor is beeing used. If true, a run
    control script is generated for supervisor only. If false, run control
    scripts are generated for all zope and zeo parts. By default, the recipe
    tries to automatically determine if supervisor is beeing used.

zopes
    A list of Zope 2 instance parts. Defaults to all parts using the
    ``plone.recipe.zope2instance`` recipe.

zeos
    A list of ZEO server parts. Defaults to all parts using either the
    ``plone.recipe.zeoserver`` or ``plone.recipe.zope2zeoserver`` recipe.

packall-symlink-directory
    Creates a symlink to the packall script in the given directory. Can
    be used to automate packing for multiple deployments.

create-filebeat-config
    Boolean to indicate whether a filebeat config should be created for this
    deployment. Defaults to true. Set to ``false`` to suppress creation of
    a filebeat config.


Links
=====

- Github: https://github.com/4teamwork/ftw.recipe.deployment
- Issues: https://github.com/4teamwork/ftw.recipe.deployment/issues
- Pypi: http://pypi.python.org/pypi/ftw.recipe.deployment
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.recipe.deployment


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.recipe.deployment`` is licensed under GNU General Public License, version 2.
