from __init__ import *

import numpy as np
import uncertainties as uc
from scipy.optimize import curve_fit

def literature_value(lit, value, dev = 0, mode="default"):
    """Comparision with literature value
    Arguments:
            lit -- (float) literature value
            value -- (float) nominal value
            dev -- (float) optional deviation
            mode -- (string) default, ufloat, tex, tex!, print, print:Latex name

    Returns:
            (float) relative deviation
    """

    value = (value/float(lit) - 1)
    deviation = (dev/float(lit))

    if (deviation < 0):
            deviation *= -1
            
    if(mode == "ufloat"):
        return uc.ufloat(value, deviation)

    if (dev != 0):
        percent = "{:LS}".format(uc.ufloat(value*100, deviation*100)) 
    else:
        percent = "{0:.1f}".format(value*100)       


    if(mode == "tex!"):
        return percent
    
    percent += " \%"
    
    if(mode == "tex"):
        return "$" + percent + "$"

    if (mode.find("print",0,5) != -1):
        tex = " Abweichung vom Literaturwert"
        if (str.find(mode,"print:") == 0):
            tex = " Abweichung vom " + mode[6:] + "-Literaturwert"

        print "$" + percent + "$" + tex
        return
        
    return  value, deviation

def weighted_average(data, mode = "default"):
        """Weighted avarage

        Arguments:
            data -- numpy array with 2 columns (first value, second deviation)
            mode -- (string) default, ufloat, print, print:Latex name

        Returns:
            (float) value, (float) deviation
        """
        value = np.average(data[:,0], weights=(1/((data[:,1])**2)))
        deviation = np.sqrt(1/np.sum(1/((data[:,1])**2)))
        
        if(mode == "ufloat"):
        	return uc.ufloat(value, deviation)
        elif (mode.find("print",0,5) != -1):
        	u = uc.ufloat(value, deviation)
        	tex = ""
        	if (str.find(mode,"print:") == 0):
        		tex = mode[6:]
        	print_ufloat(u, tex)
        	return u
        else:
        	return  value, deviation

def statistic_values(x):
	"""Returns mean with deviation of statistical data set

        Arguments:
            x -- numpy array with statistical values

        Returns:
            if x is linear array:
            	(float) mean, (float) deviation, (float) deviation for a single value in set
            if x is 2-dimensional:
            	numpy array with two columns for mean and deviation and row count like in given set
      """
	dimensions = x.shape
      
 	if len(dimensions) == 1:
		mean = np.mean(x)
		n = float(len(x))
		value_deviation = np.sqrt(1/(n-1)*np.sum((x-mean)**2))
		set_deviation = value_deviation/(np.sqrt(n))
	
		return mean, set_deviation, value_deviation
	elif len(dimensions) == 2:
		result = np.empty((dimensions[0],2))
		for i in range(0,dimensions[0]):
			r = statistic_values(x[i,:])
			result[i,0] = r[0]
			result[i,1] = r[1]
		return result
	else:
		return False

def student_t(x):
	"""Returns mean with deviation of statistical data set based on student t

        Arguments:
            x -- numpy array with statistical values

        Returns:
            if x is linear array:
            	(float) mean, (float) deviation
            if x is 2-dimensional:
            	numpy array with two columns for mean and deviation and row count like in given set
      """
	stat_values = statistic_values(x)
	n = len(x)
	if (n <= 3):
		tp = 1.32
	elif (n <= 5):
		tp = 1.15
	elif (n <= 10):
		tp = 1.06
	else:
		tp = 1.0
		
	if len(x.shape) == 1:
		return stat_values[0], stat_values[1]*tp
	elif len(x.shape) == 2:
		stat_values[:,1] *= tp
		return stat_values
	else:
		return False


def linear_fit(xdata, ydata, ysigma=None, name="r"):
    """
    Performs a linear fit to data.

    Arguments
        xdata -- array like
        ydata -- array like
        ysigma -- None or array like
            If provided, it is the standard-deviation of ydata.
            This vector, if given, will be used as weights in the fit.
        name -- (optional) Latex name

    Returns
        m  -- ufloat 
        b --  ufloat
        tex -- Latex code of linear polynom
    """
    
    xdata = np.array(xdata)
    ydata = np.array(ydata)
    ysigma = np.array(ysigma)
    
    if ysigma is None:
        w = ones(len(ydata)) # Each point is equally weighted.
    else:
        w=1.0/(ysigma**2)

    sw = sum(w)
    wx = w*xdata # this product gets used to calculate swxy and swx2
    swx = sum(wx)
    swy = sum(w*ydata)
    swxy = sum(wx*ydata)
    swx2 = sum(wx*xdata)

    a = (sw*swxy - swx*swy)/(sw*swx2 - swx*swx)
    b = (swy*swx2 - swx*swxy)/(sw*swx2 - swx*swx)
    sa = np.sqrt(sw/(sw*swx2 - swx*swx))
    sb = np.sqrt(swx2/(sw*swx2 - swx*swx))

    if ysigma is None:
        chi2 = sum(((a*xdata + b)-ydata)**2)
    else:
        chi2 = sum((((a*xdata + b)-ydata)/ysigma)**2)
    dof = len(ydata) - 2
    rchi2 = chi2/dof
    print 'results of linear_fit:'
    print '   chi squared = ', chi2
    print '   degrees of freedom = ', dof
    print '   reduced chi squared = ', rchi2

    m = uc.ufloat(a,sa)
    b = uc.ufloat(b,sb)
    
    opr = '+'
    if (b < 0):
        opr = '-'
    tex = name + "(x) = " + "{:.1uLS}".format(m) + " \cdot x " + opr + " {:.1uLS}".format(b)

    return m, b, tex



def general_fit(f, xdata, ydata, p0=None, sigma=None, **kw):
    """
    Use non-linear least squares to fit a function, f, to data.

    Assumes ``ydata = f(xdata, *params) + eps``

    Parameters
    ----------
    f : callable
        The model function, f(x, ...).  It must take the independent
        variable as the first argument and the parameters to fit as
        separate remaining arguments.
    xdata : An N-length sequence or an (k,N)-shaped array
        for functions with k predictors.
        The independent variable where the data is measured.
    ydata : N-length sequence
        The dependent data --- nominally f(xdata, ...)
    p0 : None, scalar, or M-length sequence
        Initial guess for the parameters.  If None, then the initial
        values will all be 1 (if the number of parameters for the function
        can be determined using introspection, otherwise a ValueError
        is raised).
    sigma : None or N-length sequence
        If not None, it represents the standard-deviation of ydata.
        This vector, if given, will be used as weights in the
        least-squares problem.

    Returns
    -------
    array of two columns: parameter and deviation

    Notes
    -----
    The algorithm uses the Levenburg-Marquardt algorithm through `leastsq`.
    Additional keyword arguments are passed directly to that algorithm.

    Examples
    --------
    >>> def func(x, a, b, c):
    ...     return a*np.exp(-b*x) + c

    >>> x = np.linspace(0,4,50)
    >>> y = func(x, 2.5, 1.3, 0.5)
    >>> yn = y + 0.2*np.random.normal(size=len(x))

    >>> r = general_fit(func, x, yn)
    """
    xdata = np.array(xdata)
    ydata = np.array(ydata)
    sigma = np.array(sigma)
    
    popt, pcov = curve_fit(f, xdata, ydata, p0, sigma, **kw)

    if sigma is None:
        chi2 = sum(((f(xdata,*popt)-ydata))**2)
    else:
        chi2 = sum(((f(xdata,*popt)-ydata)/sigma)**2)
    dof = len(ydata) - len(popt)
    rchi2 = chi2/dof
    print 'results of general_fit:'
    print '   chi squared = ', chi2
    print '   degrees of freedom = ', dof
    print '   reduced chi squared = ', rchi2

    # The uncertainties are the square roots of the diagonal elements
    punc = np.zeros(len(popt))
    for i in np.arange(0,len(popt)):
        punc[i] = np.sqrt(pcov[i,i])

    result = np.column_stack((popt, punc))

    return result

class Ix(object):
    def __init__(self, n = False, s = False, e = False, b = False):
        self.n = n
        self.s = s
        self.e = e
        if (not isinstance(e, (int, float, bool))):
            # try find last value
            try:
                for i in range(0, len(e[:,n])):
                    x = len(e[:,n]) - i - 1
                    if (e[x,n] != 0):
                        self.e = x + 1
                        break
            except:
                self.e = len(e[:,n])

        self.b = b
