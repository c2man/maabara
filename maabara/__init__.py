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