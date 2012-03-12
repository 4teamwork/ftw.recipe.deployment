# -*- coding: utf-8 -*-
"""Recipe deployment"""
import os.path
from ftw.recipe.deployment.logrotate import create_logrotate_conf
from ftw.recipe.deployment.rc import create_rc_scripts

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        part_names = [p.strip() for p in self.buildout['buildout']['parts']
                      .split()]

        # Figure out zope instance parts
        self.zope_parts = options.get('zopes', '').split()
        if len(self.zope_parts) == 0:
            for part_name in part_names:
                part = self.buildout[part_name]
                if part.get('recipe', None) == 'plone.recipe.zope2instance':
                    self.zope_parts.append(part_name)

        # Figure out zeo server parts
        self.zeo_parts = options.get('zeos', '').split()
        if len(self.zeo_parts) == 0:
            for part_name in part_names:
                part = self.buildout[part_name]
                if part.get('recipe', None) in ['plone.recipe.zope2zeoserver',
                                                'plone.recipe.zeoserver']:
                    self.zeo_parts.append(part_name)

        # Figure out if supervisor is beeing used
        self.has_supervisor = options.get('has-supervisor', None)
        if self.has_supervisor is None:
            self.has_supervisor = False
            for part_name in part_names:
                part = self.buildout[part_name]
                if part.get('recipe', None) == 'collective.recipe.supervisor':
                    self.has_supervisor = True
                    break
        else:
            if self.has_supervisor.lower() == 'false':
                self.has_supervisor = False
            else:
                self.has_supervisor = True

        self.buildout_dir = self.buildout['buildout']['directory']
        self.buildout_name = os.path.basename(self.buildout_dir)

    def install(self):
        """Installer"""
        files = []

        # Create logrotate configuration
        logrotate_conf = create_logrotate_conf(self)
        if logrotate_conf:
            files.append(logrotate_conf)

        rc_scripts = create_rc_scripts(self)
        files.extend(rc_scripts)

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        return files

    def update(self):
        """Updater"""
        return self.install()
