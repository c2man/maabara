User Guide
**********

This guide will give a short overview of the basic functions in maabara package.
For further details you may check the `reference guide`_ as well. 

Basic setup
^^^^^^^^^^^
First and foremost all the magic requires an import: ::

    import maabara as ma

If you only need propagation of uncertainty you may reduce import: ::

    from maabara import uncertainty


Basic error propagation
^^^^^^^^^^^^^^^^^^^^^^^

To begin a computation you have to initialize a calculation object and assign it
to a variable of your choice. ::

    ekin = ma.uncertainty.Sheet()

Next it is necessary to specify an equation for the following calculation. ::

    ekin.set_equation("Rational(1,2)*m*V**2")
    
You may use fundamental functions like ``sin, exp, sqrt, atan`` etc. and ``Rational(a,b)``
to define a fraction a/b.

.. note:: 
    Allowed variable names are alphanumeric and use ``_`` only. They must 
    be specifed by :func:`~maabara.uncertainty.Sheet.set_value`. 
    Avoid using ``I`` as variable name since it will be interpreted as imaginary unit.

Additionaly you may specify a name for the so described term. ::

    ekin.set_name("E_{kin}")

Abbreviatory it is possible to set an equation and name during init. ::

    ekin = ma.uncertainty.Sheet("Rational(1,2)*m*V**2", "E_{kin}")

Each variable used in equation has to be specified in value through 
``set_value`` command. It takes symbol name, value and its deviation. You may 
also set an optional Latex markup replacement. If given, all symbol occurrences
in equations will be replaced by the more complex Latex expression. ::

    ekin.set_value('m',5,0.1)
    ekin.set_value('V',1,tex='\\nu_{A}')

That's it, time to get the results. ::

    >>> ekin.print_result()
    2.5+/-0.05
    
``print_result``-function will return the result as ufloat and print out the 
corresponding Latex markup:

    :math:`E_{kin}=\frac{m}{2} \cdot \nu_{A}^{2}`

    ``E_{kin}=\frac{m}{2} \cdot \nu_{A}^{2}``

    :math:`E_{kin}=2.50 \pm 0.05`

    ``E_{kin}=2.50 \pm 0.05``

    :math:`\sigma_{E_{kin}}=\frac{\sigma_{m}}{2} \cdot \nu_{A}^{2}`

    ``\sigma_{E_{kin}}=\frac{\sigma_{m}}{2} \cdot \nu_{A}^{2}``

You might change multipler symbol by passing a Latex code for it to 
``print_result``-function. 

To sum up see a more complex and subsumed example below. ::

    phi = ma.uncertainty.Sheet("atan(w*L/(Ro+Ra+Rl))")
    phi.set_value("w",1272,4,"\\omega_R")
    phi.set_value("L",0.36606,0.00004,"L")
    phi.set_value("Ro",9.9,0.05,"R_\\Omega")
    phi.set_value("Ra",10.5,1,"R_A")
    phi.set_value("Rl",65.4,0.1,"R_L")
    phi.print_result()
    
.. math::

    \operatorname{atan}{\left (\frac{L \cdot \omega_R}{R_A + R_L + R_\Omega} \right )} = 1.3886 \pm 0.0022
    
You'll be happy it is a computer which does computation of uncertainty in this case ...

Abbreviations
^^^^^^^^^^^^^

But still life can be easier. The frequently used methods provide short 
alias names to save time.

==============  ============  
Method          Abbreviation      
==============  ============  
set_equation()  eq()
set_name()      n()
set_value()     v()
print_result()  p() or ps()
==============  ============ 


Batch data
^^^^^^^^^^

But what if you want to process a bunch of values in equal expressions? 
In this case it is recommend to use the ``batch``-method which will 
efficiently iterate the calculations and result in a numpy array.

If not yet happend retrieve a computation object and set equation. ::

    stack = ma.uncertainty.Sheet('a*x**3')
    
The multiple data should be given by an array wherein 
the datasets to compute are specified row-by-row. ::

             #  a   x   x_error
    data =  [ [0.5, 1. , 0.1],  
              [0.3, 2. ,0.15] ]    

It is possible to set constant values or errors before calling
batch method. The batch method will automaticly use the constant values,
if not overridden by the array data. ::

        stack.set_value('a', error=0.05)    # set constant error for a
        
To run the computation you have to pass the data array and a 
list of columns fields divided by ``|`` to ``batch``-method. 
Deviations columns must be suffix by ``%``. :: 

        >>> stack.batch(data, 'a|x|x%')
        array([[ 0.5       ,  0.15811388],
               [ 2.4       ,  0.6720119 ]])     # line-by-line result with uncertainty            

It will return an numpy array wherein each row represents an input-corresponding 
value-deviation result.  By passing ``exact`` to ``mode`` parameter it will be
rounded to significant digits. Moreover ``ufloat``-mode will result in an ufloated array: ::

        >>> stack.set_value('a',1., 0.05)          # define constant a value
        >>> stack.batch(data, '*|x|x%', 'ufloat')  # rerun computation ignoring first data column
        array([[1.0+/-0.30000000000000004],
               [8.0+/-1.7999999999999998]], dtype=object)

As you might conjectured ``*`` denotes a data column to be ignored in computation. 

Generate Latex Tables
^^^^^^^^^^^^^^^^^^^^^

But how to document a bunch of calculated values cleverly? Latex Table class 
will help you to generate tables functional and fast.

Assign to a Table object first. ::

    tbl = ma.latex.Table()

You can add columns easily with ``add_column`` function. ::

    tbl.add_column( ['Example', 1.0] )
    
The arbitrative feature is that you can render data in a special way. 
Let's say you stored the computation results from :func:`~maabara.uncertainty.Sheet.batch`
in a ``results`` variable. ::

    results = [[ 0.5       ,  0.15811388],
               [ 2.4       ,  0.6720119 ]]
           
To format these results in an appropiate form you can use ``function`` instruction.
Moreover you might set a column ``title``. ::

    tbl.add_column(results, 'num($0,$1)', 'Results')

``$x`` will link to x. column of dataset. Without ``$`` the value will be interpreted 
as constant in each row. Available functions are:
            
    ``num(value, deviation, format)`` : Number formating
        ``num($0)`` -- Format first column in data as number
        
        ``num($0,0.1)`` -- Format numbers with constant uncertainty 0.1
        
        ``num($0,$1)`` -- Dynamic uncertainty from second column of data
        
        ``num($0,$1,{:L})`` -- Optional format for ufloat printing

    ``uc(ufloat, format)`` : Number formating alias
        Like ``num`` function but with ufloat argument

    ``lit(reference, value, deviation)`` : Compare to literature value, see :func:`~maabara.data.literature_value`
        ``lit(3.141, $0)`` -- Compare with literature value of pi
        
        ``lit(3.141, $0,$1)`` -- Compare including deviation

    ``rnd(value, digits)`` : rounding
        ``rnd($0,3)`` -- round numbers in 3 digits
            
            


.. note::

    ``num`` will be default if no function name was specified: ``$0,$1`` will be interpreted as ``num($0,$1)``.
    You can use shorthand alias ``c()`` instead of ``add_column()``

Before you generate the final Latex markup, you might customize some settings. ::

    tbl.set_caption('My table')
    tbl.set_label('tbl:label1')
    tbl.set_placement('[htb]')
    
Read the `function reference`_ to get a more detailed overview of provided functionality.

What you will get is a copyable Latex table. ::

    >>> print tbl.latex()
    \begin{table}[htb]
    \centering
    \begin{tabular}{|l|l|}
    \hline
     & Results\\
    \hline
    Example & $0,50 \pm 0,16$\\
    \hline
    1.0 & $2,4 \pm 0,7$\\
    \hline
    \end{tabular}
    \caption{My table}\label{tbl:label1}\end{table}

It most cases it makes sense to save it directly to a file so you can 
include it trought ``\input`` directive in your Latex document. ::

    >>> print tbl.export('table1.tex')
    \input{table1.tex}

Handling experimental data
^^^^^^^^^^^^^^^^^^^^^^^^^^

Maabara provides a set of helper functions which allow to process experimental 
data, e.g. calculate weighted average, statistical deviation or 
linear regressions.

For a detailed documentation you might read the `data reference documentation`_.

.. _reference guide: api.html
.. _function reference: latex.html
.. _data reference documentation: data.html