from __init__ import *

import numpy as np
import uncertainties as uc

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

def linear_regression(x, y, yerr, name = "r"):
    x = np.array(x)
    y = np.array(y)
    yerr = np.array(yerr)
    fit, covmat = np.polyfit(x, y, 1, w=1/yerr, cov=True)
    variances = covmat.diagonal()
    std_devs = np.sqrt(variances)
    
    m = uc.ufloat(fit[0],std_devs[0])
    b = uc.ufloat(fit[1],std_devs[1])
    
    tex = name + "(x) = " + "{:LS}".format(m) + " \cdot x + " + "{:LS}".format(b)
        
    return m, b, tex

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

