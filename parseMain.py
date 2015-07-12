"""
Just the stub to call parsing on its own.
I'm trying to get this running for nest2.6
"""

#imports for PyNN
from pyNN.utility import get_script_args
#from pyNN.utility.plotting import Figure, Panel
import numpy as np
import re

simulator_name = get_script_args(2,"Booboo! Please supply simulator (nest|spin), and sentence")[0]
sentence = get_script_args(2)[1]

if sentence == '':
    print("What's the sentence? ")
    sentence = raw_input()

sentence = re.findall(r"[\w']+|[.,!?;]", sentence)
print(sentence)

# canonicalize sim_name
if simulator_name in ('spinnaker', 'spin', ''):
    simulator_name = 'spiNNaker'
    
if simulator_name == 'spiNNaker':
    from pyNN.spiNNaker import *
elif simulator_name == 'nest':
    from nest import *
#exec("from pyNN.%s import *" % simulator_name)

# from nest import *
DELAY = 1.0
# simulator_name = "nest"
#simulator_name = "spiNNaker"

#NEAL files and functions
#from nealParams import *
from  parseClass import parseArea

#------------Main Body---------------
#simulator_name = get_script_args(1)[0]  
#exec("from pyNN.%s import *" % simulator_name)
SIM_LENGTH=750
SUB_POPULATION_SIZE=5
intervalAction=100
#setup(timestep=DELAY,min_delay=DELAY,max_delay=DELAY,db_name='if_cond.sqlite')

if simulator_name == 'spiNNaker':
    setup(timestep=DELAY,min_delay=DELAY,max_delay=DELAY)
elif simulator_name == 'nest':
    ResetKernel()


#import pylab as plt

#----------------create neurons
parse = parseArea(simulator_name, sentence)
parse.allocateParseNeurons()

#turn on the inputs
parse.setInputs()

#---------setup connections
parse.setConnections()

#-------------------setup recording
parse.setRecording()


if simulator_name == 'spiNNaker':
    run(SIM_LENGTH)
elif simulator_name == 'nest':
    Simulate(200)


#--------------print results

if simulator_name == 'spiNNaker':
    parse.spinPlot()
elif simulator_name == 'nest':
    #parse.printResults()
    parse.nestPlot()
