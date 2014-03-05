from __init__ import *

def is_float(string):
    try:
        float(string)
        return True
    except:
        return False

class Table(object):
    """Creating Latex Tables
    """
    
    def __init__(self):
        self.reset()
        
    def reset(self):
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
    
    def placement(self, placement = '[!htb]'):
    	self.placement = placement
    
    def no_environment(self):
        self.set('embedding', False)
    
    def no_headline(self):
        self.set('headline', False)
    
    def set_label(self, label):
        self.set('label',label)
        
    def set_caption(self, caption):
        self.set('caption',caption)
            
    def set(self, option, value):
        setattr(self, option, value)
        
    def dimensions(self, array_return = False):
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
    
    def add_column(self, data, function = False, title = ''):
        """Add a column to table

        Arguments:
        data -- array like data set
        function -- instructions how to render data into cell
        
            Examples:
            num($0) -- format data from first column in data as number 
            num($0,0.1) -- format number with constant uncertainty 0.1
            num($0,$1) -- dynamic uncertainty from second column of data
            $0,$1 -- num will be default if not function given
            
            lit(3.141, $0) -- compare with literature value of pi
            lit(3.141, $0,$1) -- compare with deviation
            
            rnd($0,3) -- round numbers in 3 digits
            
        title -- column caption
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

        def num(nominal, deviation = 'False', layout = '{:L}'):
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
        """Set data

        Arguments:
        data -- array
        """
        if (len(data) > 0):
            self.data = data
            return True

    def latex(self, data = []):
        """Returns latex result
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
        if self.circline == True:
            circ = '\n \\hline\n'
        else:
            circ = ''

        # head
        head = '\\begin{table} \n'
        
        if self.center:
            head += '\\centering\n'
    
        head += '\\begin{tabular}' + self.placement
    
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

    def get_data(self):
        return self.data

    
    def export(self, file = False, mode = 'default'):
        """
        Saves latex table to file
        
        Arguments:
        
        file -- filename
        mode -- mode (default)
        
        Returns:
        Latex code or prints include command 
        
        """
        if (mode == 'default'):
            result = self.latex()
        else:
            raise ValueError('Invalid mode:' + mode)
        
        if (file != False):
            text_file = open(file, "w")
            text_file.write(result)
            text_file.close()
            
            if (mode == 'default'):
                return '\\input{' + file + '}'
            
            return True
        
        return result
