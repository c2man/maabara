Introduction
************

In scientific computations it is a quite common pastime to `propagate uncertainty`_.

The Python Package `uncertainties`_ does this sport really catchy. But its propagation yields a numeric result only. It's great if you only need the final value, but what if you have to document the underlying computation?

.. math::

    \sigma_y=\sqrt{ \sum_{i=1}^m \left(\frac{\partial y}{\partial x_i}\cdot u_i\right)^2}

Maabara extends *uncertainties* package and allows you to calculate and document error propagation in one step. Type your equation once, get the result and its uncertainty including calculation specification - ready in Latex markup.
Moreover the data module provides functions for estimation of uncertainty, fitting with error bars, comparison with literature values and more.

.. note::
    At its current state of development Maabara does not support correlations.

A short example
^^^^^^^^^^^^^^^

Let's do something prominent to see how it works: Mass–energy equivalence ::

    import maabara as ma   # import maabara package

    einstein = ma.uncertainty.Sheet()           # retrieve computation object
    einstein.set_equation('m*c**2', 'E')        # set the equation and name
    einstein.set_value('m', 1., 0.1)            # set mass value and its uncertainty
    einstein.set_value('c', 28E3, tex='c_0')    # set light speed and its Latex symbol

    einstein.print_result()

In default setting you'll get result, equation and propagation of uncertainty like

.. math::

        E=\left(7.8 \pm 0.8\right) \times 10^{8}

        E=c_0^{2} \cdot m

        \sigma_{E}=c_0^{2} \cdot \sigma_{m}


Of course everything will be copyable Latex markup. Well, it is not too impressing. But add some trigonometric functions, calculate a hundreds of values or generate Latex tables from result and it will get more exciting. 
Continue reading the `User Guide`_ for such pleasures.


.. _propagate uncertainty: http://en.wikipedia.org/wiki/Propagation_of_uncertainty
.. _uncertainties: http://pythonhosted.org/uncertainties/
.. _User Guide: user_guide.html
