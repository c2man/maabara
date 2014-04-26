from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='maabara',
      version='1.0.0',
      description='Maabara allows you to compute and document error propagation fast and easy through Latex',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
      ],
      long_description=readme(),
      keywords='propagation uncertainties symbolic latex fitting error',
      url='https://github.com/dudheit314/maabara',
      author='Frithjof Gressmann',
      author_email='hello@nocio.de',
      license='BSD',
      packages=['maabara'],
      install_requires=[
          'numpy','sympy','uncertainties','scipy'
      ],
      include_package_data=True,
      zip_safe=False)