.. contents::

Introduction
============

This recipe provides support for configuring various unix services when
deploying Plone/Zope2 with buildout.

As for now the following features are provided:

* Create Logrotate configuration for all Zope 2 instance and ZEO parts.

* Create RedHat-like run-control scripts.


Supported options
=================

The recipe supports the following options:

logrotate-directory
    The directory where the logrotate configuration file will be created.
    Defaults to ``${buildout:directory}/etc/logrotate.d``. Add this parameter
    with no arguments to supress generation of logrotate configuration.

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

rc-directory
    The directory where run-control scripts should be installed.
    Defaults to ``${buildout:directory}/bin``. Add this parameter with no
    arguments to supress generation of run-control scripts.

rc-prefix
    Name prefix for run-control scripts. Defaults to ``rc-``.

has-supervisor
    Boolean indication whether supervisor is beeing used. If true, a run
    control script is generate for supervisor only. If false, run control
    scripts are generated for all zope and zeo parts. By default, the recipe
    tries to automatically determine if supervisor is beeing used.

zopes
    A list of Zope 2 instance parts. Defaults to all parts using the
    ``plone.recipe.zope2instance`` recipe.

zeos
    A list of ZEO server parts. Defaults to all parts using either the
    ``plone.recipe.zeoserver`` or ``plone.recipe.zope2zeoserver`` recipe.



Links
=====

- Main github project repository: https://github.com/4teamwork/ftw.recipe.deployment
- Issue tracker: https://github.com/4teamwork/ftw.recipe.deployment/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.recipe.deployment
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.recipe.deployment


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.recipe.deployment`` is licensed under GNU General Public License, version 2.
