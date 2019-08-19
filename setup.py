from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='H2O_getNLCD',
      version='0.0.1',
      packages=['test',
                'H2O_getNLCD'],
      install_requires=['requests'])
