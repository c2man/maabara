from maabara.uncertainty import *
from maabara.data import *
from maabara.latex import *

def hr():
    try:
        import IPython.display
        IPython.display.display(IPython.display.HTML('<hr />'))
    except:
        pass
    
def print_ufloat(ufloat, name = '',layout = '{:.1uL}'):
    prefix = ""
    if name != "":
        prefix = name + " = "

    tex = prefix + layout.format(ufloat)
    
    try:
        import IPython.display
        IPython.display.display((IPython.display.Math(tex)))
    except:
        logging.warn('Could not import IPython.display to render Latex')
    print tex + '\n'
    
    
#@remove
def ufloat2tex_(ufloat, name = "", mode = "default"):
	prefix = ""
	if name != "":
		prefix = name + " = "
		
	if (mode == "short"):
		mode = "{:LS}"
	else:
		mode = "{:L}"
	return prefix + mode.format(ufloat)

def u2tex_(ufloat, name = "", mode = "short"):
	return ufloat2tex(ufloat, name, mode)