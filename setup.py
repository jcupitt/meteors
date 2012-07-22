# this is the setup file - run once only to make the package:
# python setup.py sdist
# will make the tarball. This can be unpacked then:
# python setup.py install --prefix=/usr/local/bin

from distutils.core import setup

setup(name='Meteors',
    version='1.1dev',
    packages=['meteors'],
    description='Small game', 
    requires=['pyglet'],
    long_description=open('README.md').read(),
)
