
from setuptools import find_packages, setup

import termconf


version = termconf.__version__

with open('README.md') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    dependencies = [l.strip() for l in f.readlines() if not l.startswith('#')]

setup(
    name='termconf',
    version=version,
    author='iuvbio',
    author_email='cryptodemigod@protonmail.com',
    description='Generates gnome-terminal profiles based on an image',
    long_description_content_type="text/markdown",
    long_description=long_description,
    keywords="""\
    colorscheme gnome-terminal profiles terminal-emulators \
    changing-colorschemes\
    """,
    packages=find_packages(),
    entry_points={'console_scripts': ['tconf=termconf.main:cli']},
    install_requires=dependencies,
    extras_require={
        'imgpal': []
    }
)
