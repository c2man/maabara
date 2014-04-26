from __init__ import *

def is_float(string):
    try:
        float(string)
        return True
    except:
        return False

class Table(object):
    """
    
    Generating Latex Tables
    
    """
    
    def __init__(self):
        self.reset()
        
    def reset(self):
        """
        
        Clear all settings
        
        Returns
        -------
        out : boolean
            True on success.
        """
        self.data = []
        self.header = []
        
        #options
        self.caption = ''
        self.label = ''
        self.headline = True
        self.align = 'l'
        self.center = True
        self.circline = True
        self.embedding = True
        self.placement = '[!htb]'
        
        return True
    
    def set_placement(self, placement = '[!htb]'):
        """
        
        Set a placement
        
        Parameters
        ----------
        placement : string, default ``[!htb]``
            Latex placement to align table.
            
        Returns
        -------
        out : boolean
            True on success.
        """
    	self.placement = placement
        
        return True
    
    def no_environment(self):
        """
        
        Disables Table environment. Export will result in table body only.
        
        """
        self.set('embedding', False)
    
    def no_headline(self):
        """
        
        Disables head row. Export won't add headers to table columns.
        
        """
        self.set('headline', False)
    
    def set_label(self, label):
        """
        
        Set a Latex label
        
        """
        self.set('label',label)
        
    def set_caption(self, caption):
        """
        
        Set a Latex caption
        
        """
        self.set('caption',caption)
            
    def set(self, option, value):
        setattr(self, option, value)
        
    def dimensions(self, array_return = False):
        """
        
        Returns a the dimensions of the current table data
        
        Parameters
        ----------
        array_return : boolean, optional
            If True method will return and empty row and column array
            
        Returns
        -------
        out : mixed
            By default method will return row and col count, if array_return
            two empty arrays with the corresponding dimensions are returned.
        
        """
        rows = len(self.data)
        try:
            cols = len(self.data[0])
        except:
            cols = 0
            
        if (array_return):
            e = ''
            x = []
            y = []
            for i in range(cols):
                x.append(e)
            for i in range(rows):
                y.append([e])

            return x,y
            
        return rows, cols
    
    def _args_from_string(self,string, default_func_name = ''):
        #@todo allow inner function calls with eval
        string = string.split(")")[0]
        if (len(string) == 0):
            return ("",)
        args = string.split(",")
        func = args[0].split("(")
        if (len(func) == 1):
            args.insert(0, default_func_name)
        elif (len(func) >= 2):
            args[0] = func[1]
            args.insert(0, func[0])
        return args
    
    def _function_from_string(self, function, default = 'num'):
        if (function == False):
            return False, []
        
        args = self._args_from_string(function, default) 
        
        #if (not args[0] in ['num','lit', 'rnd']):
            #raise ValueError('Unknown function name: ' + name)
        
        return str(args[0]), args[1:]
    
    def c(self, data, function = False, title = ''):
        """
        
        Alias of :func:`~maabara.latex.Table.add_column`
        
        """
        self.add_column(data, function, title);
    
    def add_column(self, data, function = False, title = ''):
        """
        
        Add a column to table

        Parameters
        ----------
        data : array_like
            Data set
        function : mixed
            If False ``data`` will be added unchanged.
        
            If String it sets instructions how to render ``data`` into each cell, 
            e.g. ``example($0,1)``. ``$x`` will link to x. column of dataset.
            
            Available functions:
            
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
            
            
            Note that ``num`` will be default if no function name was specified: ``$0,$1`` will be interpreted as ``num($0,$1)``
            
        title : string, optional
            Sets a column caption
        
        """
        def dynamic_value(arg, row):
            if (str(arg)[0] == "$"):
                try:
                    col = int(str(arg)[1:])
                    return data[row][col]
                except:
                    raise ValueError("Given column index does not exists: " + str(col))
            else:
                # cast if numeric
                dot = arg.find('.')
                if is_float(arg):
                    if dot == -1:
                        arg = int(arg)
                    else:
                        arg = float(arg)
                        
                return arg

        def num(nominal, deviation = 'False', layout = '{:.1uL}'):
            result = '\\num{' + str(nominal) + '}'
            if (is_float(deviation)):
                import uncertainties as uc
                tmp = uc.ufloat(float(nominal), float(deviation))
                result = "$" + layout.format(tmp) + "$"

            return result.replace('.', ',')

        def lit(lit, value, dev = 0):
            from maabara.data import literature_value
            return literature_value(lit, value, dev, "tex!")
        
        def rnd(value, digits):
            return num(round(value, digits))
        
        def uc(value, layout = '{:.1uL}'):
            return num(value.n, value.s, layout)

        # transpose to column
        try:
            data[0][0]
            if (isinstance(data[0],str)):
                raise
        except:
            data = [[data[i]] for i in range(len(data))]
        
        rows, cols = self.dimensions()
        function, args = self._function_from_string(function)

        for row in range(len(data)):
            # generate cell content
            if (function == False):
                cell = data[row][0]
            else:
                tmp = [dynamic_value(args[i],row) for i in range(len(args))]
                cell = eval(function + "(*tmp)")
            
            # expand array if needed
            space = []
            for i in range(cols):
                space.append('')
                
            if (row >= len(self.data)):
                self.data.append(space)
            
            self.data[row].append(str(cell))
        
        # fill up with empty cells if needed
        if (len(self.data) > len(data)):
            for i in range(len(data),len(self.data)):
                self.data[i].append('')
        
        # set title
        self.header.append(title)

    def set_data(self, data):
        """
        
        Set data

        Parameters
        ----------
        data : array_like
        
        Returns
        -------
        out : boolean
            True on success
        
        """
        if (len(data) > 0):
            self.data = data
            return True

    def get_data(self):
        """
        
        Get data
        
        Returns
        -------
        out : array
            Data
        
        """
        return self.data

    def latex(self, data = []):
        """
        
        Get Latex table markup
        
        Parameters
        ----------
        data : array_like, optional
            See :func:`~maabara.latex.set_data`
        
        Returns
        -------
        out : string
            Latex table markup
        
        """
        
        self.set_data(data)

        result = ""

        # header
        if self.headline:
            result += ' & '.join(self.header) + "\\\\\n\\hline\n"

        # process the lines
        for row in range(len(self.data)):
            
            result += ' & '.join(self.data[row])
            
            if (row < len(self.data) - 1):
                result += '\\\\\n\\hline\n'
            else:
                result += "\\\\\n"


        if (self.embedding):
                head, foot = self.environment()	
                result = head + result + foot

        return result
    
    def environment(self): 
        """
        
        Get Latex table environment markup
        
        Returns
        -------
        out : string header, string footer
            Latex table environment header and footer
        
        """
        if self.circline == True:
            circ = '\n \\hline\n'
        else:
            circ = ''

        # head
        head = '\\begin{table}' + self.placement + '\n'
        
        if self.center:
            head += '\\centering\n'
    
        head += '\\begin{tabular}'
    
        pos = ''
        sep = ''
        
        try:
            length = len(self.data[0])
        except:
            length = 0
        
        for i in range(length):
            pos += sep + self.align
            sep = '|'
            
        if pos != '':
            head += '{|' + pos + '|}'
            
        head += circ
    
        # foot
        foot = circ + '\\end{tabular}\n'
        
        if (self.caption != ''):
            foot += '\\caption{' + self.caption + '}'
        
        if (self.label != ''):
            foot += '\\label{' + self.label + '}'

        foot += '\\end{table}'

        return head, foot

    
    def export(self, file):
        """
        
        Saves Latex table markup to file
        
        Parameters
        ----------
        file : string
            Filename
        
        Returns
        -------
        out : mixed
            Latex ``\input`` command or ``False`` on failure
        
        """

        result = self.latex()
        
        try:
            text_file = open(file, "w")
            text_file.write(result)
            text_file.close()
        except:
            return False
            

        return '\\input{' + file + '}'