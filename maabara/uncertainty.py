import re
import logging
import sympy as sy
import numpy as np
import uncertainties as uc

class Sheet(object):
    """Symbolic propagation of uncertainty

    Arguments:
    equation -- see this.set_equation
    data -- see this.set_data
    name -- (string) type name
    """

    def __init__(self, equation = "0", name = "", data = []):
    	self.reset()
        self.set_equation(equation)
        self.name = name
        self.set_data(data)
	
    def reset(self):
        """Clear all settings
        """
        self.name = ""
	
        self.equation = "0"
        self.eq_expr = 0
        self.err_expr = 0
    
        self.data = []
    
        self.nominal = 0
        self.deviation = 0
        self.ufloat = False
        
    	self.messages = []
        
        return True
    
    def set_name(self,name):
        """Set a name for this result
            You can use any Latex markup
        Arguments:
        name -- (string) Latex name
        """
        self.name = name
        return True
    
    def n(self, name):
        """Set a name for this result
            You can use any Latex markup
        Arguments:
            name -- (string) Latex name
        """
    	return self.set_name(name)
    
    def set_equation(self,equation, name = ""):
        """Set sympy equation string
            Only use symbols you have defined by set_value!
        Arguments:
        equation -- Sympy equation string; note: 1/2 -> Rational(1,2)
        name -- (optional) see set_name function
        """
        if (isinstance(equation, str) & (equation != "")):
            self.changed_equation = True
            equation = equation.replace('_','')
            self.equation = equation
            self.eq_expr = sy.sympify(equation)
            if name != "":
            	self.name = name
            return True
            
    def eq(self,equation,name = ""):
        """Set sympy equation string
            Only use symbols you have defined by set_value!
        Arguments:
        equation -- Sympy equation string; note: 1/2 -> Rational(1,2)
        name -- (optional) see set_name function
        """
    	return self.set_equation(equation, name)
            
    def set_data(self, data):
        """Set data

        Arguments:
        data -- list of tuples: ( string Variable , float Value, float Error = 0, tex = "")
        """
        if (len(data) > 0):
        	self.data = data
        	return True
            
    def get_data(self, line = False, element = False):
    	"""Returns data
    	
    	Arguments
    	line --- (mixed, optional) 
    	element --- (string) val, dev, tex
    	"""
    	if (line != False):
    		index = self._find_in_list(self.data, line)
    		if (index == -1):
    			return False
    		else:
    			if(index[1] == 0):
    				if (element == "val"):
    					return self.data[index[0]][1]
    				elif (element == "dev"):
    					return self.data[index[0]][2]
    				elif (element == "tex"):
    					return self.data[index[0]][3]	
    				else:
    					return self.data[index[0]]
    			else:
    				return False
    	else:
    		return self.data

    def _msg(self, message, mode = 'default'):
        # avoid multiple messages
    	try:
            self.messages.index(message)
            return
    	except:
            self.messages.append(message)
    	
    	if (mode == 'warning'):
            logging.warning(message)
        else:
            logging.info(message)
            
    def run(self, equation = False, data = []):
        """Symbolic error propagation from data

        Arguments:
        equation -- see this.set_equation
        data -- see this.set_data
        Returns tuple ( sympy equation, sympy error_equation, float value, float, error_value)
        """
        
        self.set_equation(equation)
        self.set_data(data)
        
        no_deviation = []
        
        if (self.changed_equation):
            self.err_expr = 0

            for var in self.data:
                #define symbol
                exec(var[0] + " = sy.Symbol('" + var[0] + "')")


                if len(var) >= 2 and isinstance(var[2], bool) and var[2] == False:
                    no_deviation.append(var[0])
                else:
                    # get derivative
                    exec(var[0] + "_der = sy.diff(self.eq_expr,var[0])")

                    # set error variable
                    exec(var[0] + "_err = sy.Symbol('sigma_" + var[0] + "')")
                    exec(var[0] + "_der = " + var[0] + "_der * " + var[0] + "_err")

                    # chunk
                    exec("self.err_expr = self.err_expr + (" + var[0] + "_der)**2")

            # square root
            self.err_expr = sy.simplify(sy.sqrt(self.err_expr))

            # force rooting
            self.err_expr = sy.powdenest(self.err_expr, force=True)
            
            self.changed_equation = False

        # error propagation if given
        nominal = self.eq_expr
        deviation = self.err_expr
        for var in self.data:
	    if (len(var) != 4):
		var = (var[0],False, False, False)
	    if isinstance(float(var[1]), (int,float,long)):
                try:
                    exec("nominal = nominal.subs('" + var[0] + "'," + str(var[1]) + ")")
                except:
                    pass
                try:
                    exec("deviation = deviation.subs('" + var[0] + "', +" + str(var[1]) + ")")
                except:
                    pass
  	    if isinstance(float(var[2]), (int,float,long)):
		try:
                   exec("deviation = deviation.subs('sigma_" + var[0] + "', " + str(var[2]) + ")")	
                except:
                    pass

        try:
            self.nominal = float(nominal)
        except:
	    self._msg("Could not finish nominal evalution due to missing values, stopped in at \n" + str(nominal), 'warning')
            self.nominal = 0
            
        try:
            self.deviation = float(deviation)
        except:
	    self._msg("Could not finish deviation evalution due to missing values, stopped in at \n" + str(deviation), 'warning')
            self.deviation = 0
            
        if (len(no_deviation) > 0):
            self._msg("No deviation for " + ', '.join(no_deviation))
        
        # cast to uncertainties
        self.ufloat = uc.ufloat(self.nominal,self.deviation)
        
        return

    def print_result(self,mode = "default", multiply = "dot"):
        """Print symbolic error propagation

        Arguments:
        mode -- (string) default, short
        multiply -- (optional) tex code for multiply, use None for no multipliers
        """
        
        self.run()
        
        # outs
        result_tex = '{:L}'.format(self.ufloat)
        if (self.name != ""):
            result_tex = self.name + "=" + result_tex

        eq_tex = sy.latex(self.eq_expr, mul_symbol=multiply)
        if (self.name != ""):
            eq_tex = self.name + "=" + eq_tex

        error_tex = sy.latex(self.err_expr, mul_symbol=multiply)
        if (self.name != ""):
            error_tex = "\sigma_{" + self.name + "}" + "=" + error_tex

	# replace alias
	for var in self.data:
 	    if (len(var) == 4):
		if (var[3] != False):
		    var0 = sy.latex(sy.sympify(str(var[0])))
                    # secure replacement
                    subs = var[3]
                    eq_tex = re.sub(r'\b' + var0 + r'\b', subs.encode('string-escape'), eq_tex)
		    error_tex = re.sub(r'\b' + var0 + r'\b', subs.encode('string-escape'), error_tex)

        def pdisplay(tex):
            IPython.display.display((IPython.display.Math(tex)))
            print tex + '\n'
            

        if (mode == "short"):
            print eq_tex + '\n'
            print result_tex + '\n'
            print error_tex + '\n'
        elif (mode == "default"):
            try:
                import IPython.display
                pdisplay(eq_tex)
                pdisplay(result_tex)
                pdisplay(error_tex)
            except:
                logging.warn('Could not import IPython.display to render Latex')
        else:
            raise ValueError('Invalid Mode')
            
        return self.ufloat

    def p(self,mode = "default", multiply = "dot"):
        """Print symbolic error propagation alias

        Arguments:
        mode -- (string) default, short
        multiply -- (optional) tex code for multiply, use None for no multipliers
        """
    	return self.print_result(mode, multiply)

    def ps(self):
        """Print symbolic error propagation in short mode
        (alias for print_result)
        """
    	return self.print_result("short")

    def get_result(self,mode = "default"):
        """Get error propagation

        Arguments:
        mode -- (string) tex, ufloat, exact, default

        Returns:
            mixed
        """
        self.run()
        
        if (mode.find("tex",0,3) != -1):
        	tex = '{:L}'.format(self.ufloat)
        	if (str.find(mode,"tex:") == 0):
        		tex = mode[4:] + "=" + tex
        	display(Math(tex))
        	print tex
        	return tex
        elif (mode == "ufloat"):
            return self.ufloat
        elif (mode == "exact"):
	    tmp = "{:10}".format(self.ufloat)
	    tmp = str.split(tmp,'+/-')
            return (float(tmp[0]), float(tmp[1]))
	elif (mode == "print"):
	    print str(self.nominal) + "\t" + str(self.deviation)
	    return (self.nominal, self.deviation)
        elif (mode == "default"):
            return (self.nominal, self.deviation)

        return

    def set_value(self,symbol, value = False, error = False, tex = False):
        """Set uncertain value

        Arguments:
        symbol -- (string) symbol string used in equation
        value -- (float) value
        error -- (float) deviation
        tex -- (string) latex replace string (optional)
        """

	symbol_replaced = symbol.replace('_','')
        
	symbol_clear = ''.join(e for e in symbol_replaced if e.isalnum())
	
	if (symbol_replaced != symbol_clear):
		raise ValueError("Invalid symbol name, only underscore alphanumeric expression allowed (eg. Example_1). You might use 'tex'-parameter to set more complex expression names")

	if (symbol_replaced != symbol) & (tex == False):
		tex = sy.latex(sy.sympify(symbol))

        val = (symbol_replaced, value, error, tex)
        
        index = self._find_in_list(self.data, symbol)
        if (index == -1):
            self.data.append(val)
        else:
            if(index[1] == 0):
                self.data[index[0]] = val
            else:
                self.data.append(val)
                
    def v(self,symbol, value = False, error = False, tex = False):
        """Set uncertain value

        Arguments:
        symbol -- (string) symbol string used in equation
        value -- (float) value
        error -- (float) deviation
        tex -- (string) latex replace string (optional)
        """
    	return self.set_value(symbol, value, error, tex)
    
    def set_error(self, symbol, error):
    	return self.set_value(symbol, False, error)
    
    def batch(self,data, fields, mode = "default"):
        """Multiple numeric error propagation

        Arguments:
        data -- numpy array or tuple of columns
        fields --   (string) list of columns divided by |
                    deviations columns must be suffix by '%'
                    write * to ignore column
                    
                    Example:
                    E|E%|*|t
                    
        mode -- (string) exact, ufloat, default
        """

        if(isinstance(data,tuple)):
            data = np.column_stack(data)
        
    	# if not a column, transpose it
    	if (len(data.shape) == 1):
    		data = np.column_stack((data[:],))
    	
    	#reset messages
    	self.messages = []
    
        fields = str.split(fields.strip(),"|")

        # require same size
        if (len(fields) != len(data[0])):
            return False

        if (mode == 'ufloat'):
            result = range(len(data))
        else:
            result = np.zeros([len(data),2])
            
        i = 0
        for line in data:
            for field in fields:
                if(field == "*"):
                    continue
                
                if (field.find("%") != -1):
                    continue
                
                try:
                	val = line[fields.index(field)]
                except:
                	val = self.get_data(field,'val')
                	
                	
                try:
                	dev = line[fields.index(field + '%')]
                except:
                	dev = self.get_data(field,'dev')
                
                tex = self.get_data(field,'tex')
    	
                self.set_value(field, val, dev, tex)
            
            if (mode == 'ufloat'):
                result[i] = [self.get_result(mode)]
                
            else:
                nominal, deviation = self.get_result(mode)

                result[i][0] = nominal
                result[i][1] = deviation
            
            i += 1
        
        if (mode == 'ufloat'):
            return np.array(result)
        
        return result
    
    def _find_in_list(self,l, elem):
        for row, i in enumerate(l):
            try:
                column = i.index(elem)
            except ValueError:
                continue
            return row, column
        return -1