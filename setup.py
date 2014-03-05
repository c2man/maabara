from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='maabara',
      version='0.2',
      description='Tools for evaluation of scientific experiments',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
      ],
      long_description=readme(),
      keywords='uncertainties symbolic latex',
      url='http://www.nocio.de',
      author='Frithjof Gressmann',
      author_email='hello@nocio.de',
      license='MIT',
      packages=['maabara'],
      install_requires=[
          'numpy','sympy','uncertainties'
      ],
      include_package_data=True,
      zip_safe=False)