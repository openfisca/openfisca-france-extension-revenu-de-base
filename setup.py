#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Revenu de base enfants reform for OpenFisca French tax-benefit system"""


from setuptools import setup, find_packages


classifiers = """\
Development Status :: 2 - Pre-Alpha
Environment :: Web Environment
License :: OSI Approved :: GNU Affero General Public License v3
Operating System :: POSIX
Programming Language :: Python
Topic :: Scientific/Engineering :: Information Analysis
"""

doc_lines = __doc__.split('\n')


setup(
    name = 'OpenFisca-France-Reform-Revenu-De-Base-Enfants',
    version = '0.1.dev0',

    author = 'Marc de Basquiat, Adrien Fabre',
    author_email = 'marc@de-basquiat.com',
    classifiers = [classifier for classifier in classifiers.split('\n') if classifier],
    description = doc_lines[0],
    keywords = 'benefit microsimulation server social tax user reform',
    license = 'http://www.fsf.org/licensing/licenses/agpl-3.0.html',
    long_description = '\n'.join(doc_lines[2:]),
    url = 'https://github.com/openfisca/openfisca-france-reform-revenu-de-base-enfants',

    install_requires = [
        'numpy >= 1.6,< 1.10',
        'OpenFisca-Core >= 0.5.3.dev0',
        'OpenFisca-France >= 0.5.4.dev0',
        ],
    packages = find_packages(),
    zip_safe = False,
    )
