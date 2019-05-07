Deeptracy plugins
=================

The dependency extraction proccess is carried out by Buildbot. It leverages on a plugin architecture in which separated components, the plugins, provide different ways, called tasks, of doing de extraction. Each plugin gives support for a particular programming language.


Available plugins
-----------------

Currently Deeptracy offers several plugins to do dependency extraction that give support to the main programming languages.

Dependencycheck
~~~~~~~~~~~~~~~

This plugin is intended for java projects, and uses the OWASP Dependencycheck utility (version 4.0.2) to do the dependency extraction.

It publishes one task 'dependency_check'.

Maven
~~~~~

A set of plugins intended for java projects that use Maven to do the dependency extraction, each plugin gives support for a specific version of Maven.

Each plugin publishes one task 'mvn_dependencytree'

Npm
~~~

A set of plugins intended for javascript projects that use Npm to do the dependency extraction, each plugin gives support for a specific version of Npm.

Each plugin publishes one task 'npm_install'


python
~~~~~~

A set of plugins intended for Python project, each plugin gives support for a specific version of Python.

Each plugin publishes two task:
- 'requirement_file', for doing the dependency extraction by analyzing the project's requirements.txt file.
- 'pip_install',  for doing the dependency extraction by using the pip utility.
