from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='maabara',
      version='0.8',
      description='Symbolic propagation of uncertainties latex interfaced',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
      ],
      long_description=readme(),
      keywords='propagation uncertainties symbolic latex',
      url='https://github.com/dudheit314/maabara',
      author='Frithjof Gressmann',
      author_email='hello@nocio.de',
      license='MIT',
      packages=['maabara'],
      install_requires=[
          'numpy','sympy','uncertainties','scipy'
      ],
      include_package_data=True,
      zip_safe=False)