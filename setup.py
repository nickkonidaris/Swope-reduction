import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "Swoper",
    version = "0.0.1",
    author = "Nicholas P. Konidaris",
    author_email = "npk@carnegiescience.edu",
    description = ("Swope data reduction"),
    license = "GNU General Public License v3.0",
    keywords = "Python",
    url = "https://github.com/nickkonidaris/Swope-reduction",
    packages=['Swoper'],
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python',
    ],
)
