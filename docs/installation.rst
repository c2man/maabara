Installation
************

Installation is very easy through `pip`_. Maabara depends on `uncertainties`_, `sympy`_ and `numpy`_ packages. It is recommend to use it in an `IPython notebook`_ environment which enables Latex rendering and helps remarkable in keeping the overview.

Ubuntu
^^^^^^
See an setup example of Ubuntu 14.04 below. :: 

    sudo apt-get install python-pip                 # install pip manager
    sudo pip install uncertainties sympy numpy      # install dependencies
    sudo pip install maabara                        # install maabara package
    
To install the optional ipython shell type ::

    sudo pip install ipython
    
Other operation systems
^^^^^^^^^^^^^^^^^^^^^^^
Check `pip`_-Website to find setup instructions for your operation system and contribute it to this documentation when suitable.
    
Test your installation
^^^^^^^^^^^^^^^^^^^^^^
You may test your installation. Open a terminal and start a new IPython notebook by typing ::

    ipython notebook
    
Paste the following to a cell and press [Shift]+[Enter] ::

    import maabara as ma
    import uncertainties as uc
    ma.print_ufloat(uc.ufloat(1,0), 'Maabara')
    
If you see uncertainty printing you're ready to go ahead.

.. _pip: http://www.pip-installer.org/
.. _uncertainties: http://pythonhosted.org/uncertainties/
.. _sympy: http://sympy.org/en/index.html
.. _numpy: http://www.numpy.org/
.. _IPython notebook: http://ipython.org/notebook.html