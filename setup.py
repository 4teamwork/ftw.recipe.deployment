# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

version = '1.1'
tests_require = ['zope.testing']

setup(name='ftw.recipe.deployment',
      version=version,
      description="A zc.buildout recipe for Plone deployments which configures"
                  " various unix system services.",
      long_description=open("README.rst").read()
                       + "\n" +
                       open("HISTORY.txt").read()
                       + "\n" +
                       open(os.path.join("ftw", "recipe", "deployment",
                                         "README.txt")).read(),

      classifiers=[
        'Framework :: Buildout :: Recipe',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
        ],

      keywords='',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.recipe.deployment',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', 'ftw.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'zc.buildout',
        ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      test_suite='ftw.recipe.deployment.tests.test_docs.test_suite',
      entry_points = {
        'zc.buildout': ['default = ftw.recipe.deployment:Recipe']},
      )
