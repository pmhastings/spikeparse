"""
(NOTE: This version is less object-oriented than the previous so that I can
fiddle with it better.)

Parsing class with functions to create and run parsing.
It's really just a big FSA to deal with all the sentences.  The final
state is unique for each sentence considered.

Grammar is now moved to separate file.
"""

import pylab as pl
import re

from grammar_qa1 import *
from readInput import *     #for nest processing of text sentences

plot = False
#spikeServe= False
spikeServe= True

if plot:
    from pyNN.utility.plotting import Figure, Panel
    
# Just importing everything because it was a pain to check which to import
from pyNN.spiNNaker import *
from nest import *
if plot:
    import nest.raster_plot

#import for spike injection
oldSpinnaker = False
if  oldSpinnaker:
    import spynnaker_external_devices_plugin.pyNN as externaldevices
    from spinnman.messages.eieio.eieio_prefix_type import EIEIOPrefixType
else:
    import spynnaker_external_devices_plugin.pyNN as ExternalDevices
    import socket
    import spinnman.messages.eieio.create_eieio_data as parse_msg
    import spinnman.data.little_endian_byte_array_byte_reader as byte_reader
    UDP_IP = "0.0.0.0"
    UDP_PORT = 17895

    #import spynnaker_external_devices_plugin.pyNN as externaldevices


DELAY = 1.0

# simulator_name = ''
sentence = ''

WordsCells = []
StatesCells = []
inputWordSource = []
inputSources = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
multS = []
multW = []
multSp = []
pop_outputs = []
# gate_outputs = []

# def __init__(simName, sent):
#     simulator_name = simName
#     sentence = sent
        
#----helper functions
def nealProjection(preNeurons,postNeurons, connectorList,inhExc):
    if simulator_name == 'spiNNaker':
        Projection(preNeurons, postNeurons, connectorList,target=inhExc)
    elif simulator_name == 'nest':
        # Projection(preNeurons, postNeurons, connectorList)
        for connection in connectorList:
            Connect(preNeurons[connection[0]],postNeurons[connection[1]],
                {'weight':connection[2]})
    else:
        print 'bad simulator for nealProjection'

def peterProjection(preNeurons, postNeurons, connector, inhExc):
    if simulator_name == 'spiNNaker':
        excConnector = FromListConnector(connector)
        nealProjection(preNeurons, postNeurons, excConnector, inhExc)
    elif simulator_name == 'nest':
        nealProjection(preNeurons, postNeurons, connector, inhExc)


def makeCASynapses(CAsCells,numberCAs):
    print simulator_name
    synWeight = 0
    if simulator_name == 'spiNNaker':
        synWeight = 8.0 
    elif simulator_name == 'nest':
        synWeight = 25.0
    connector = []
    for cCA in range (0,numberCAs):
        for fromOff in range (0,5):
            for toOff in range (0,5):
                if (fromOff != toOff):
                    fromNeuron = cCA*5+fromOff
                    toNeuron = cCA*5+toOff
                    connector=connector+[(fromNeuron,toNeuron,synWeight,
                                          DELAY)]
    peterProjection(CAsCells,CAsCells, connector,'excitatory')

def makeWordCAs():
    makeCASynapses(WordsCells,NUMBER_WORDS)


def makeStateCAs():
    makeCASynapses(StatesCells,NUMBER_STATES)

    
#connect word to state
def connectWordCAToStateCA(fromNum,toNum,synWeight):
    connector = []
    for fromOff in range (0,5):
        for toOff in range (0,5):
            fromNeuron = fromNum*5 + fromOff
            toNeuron = toNum*5 + toOff
            connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
    peterProjection(WordsCells,StatesCells, connector,'excitatory')

#connect state to state
def connectStateCAToStateCA(fromNum,toNum,synWeight):
    connector = []
    for fromOff in range (0,5):
        for toOff in range (0,5):
            fromNeuron = fromNum*5 + fromOff
            toNeuron = toNum*5 + toOff
            connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
    peterProjection(StatesCells,StatesCells, connector,'excitatory')

#state stops word
def StateCAStopsWordCA(fromNum, toNum):
    synWeight = -10.0 
    connector = []
    for fromOff in range (0,5):
        for toOff in range (0,5):
            fromNeuron = fromNum*5+fromOff
            toNeuron = toNum*5 + toOff
            connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
    peterProjection(StatesCells,WordsCells, connector, 'inhibitory')

#state stops state
def StateCAStopsStateCA(fromNum,toNum):
    if simulator_name == 'spiNNaker':
        synWeight = -10.0
    elif simulator_name == 'nest':
        synWeight = -25.0
    connector = []
    for fromOff in range (0,5):
        for toOff in range (0,5):
            fromNeuron = fromNum*5 + fromOff
            toNeuron = toNum*5 + toOff
            connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
    peterProjection(StatesCells,StatesCells, connector,'inhibitory')

def CAStopsCA2(fromCA,toCA,toNum):
    synWeight = -10.0
    connector = []
    for fromNeuron in range (0,5):
        for toOff in range (0,5):
            toNeuron = toNum*5 + toOff
            connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
    peterProjection(fromCA,toCA, connector,'inhibitory')

def CAStopsCA(fromCA,toCA):
    synWeight = -10.0
    connector = []
    for fromNeuron in range (0,5):
        for toNeuron in range (0,5):
            connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
    peterProjection(fromCA,toCA, connector,'inhibitory')


###---create the neurons for the CAs
def allocateInputs():
    global inputWordSource
    if simulator_name == 'spiNNaker':
        if oldSpinnaker:
            cell_params_spike_injector_with_prefix = {'host_port_number' : 12345,
                        'host_ip_address'  : "localhost",
                        'virtual_key'      : 0x70800,
                        'prefix'           : 7,
                        'prefix_type': EIEIOPrefixType.UPPER_HALF_WORD}
            inputWordSource = Population(NUMBER_WORDS+3,
                        externaldevices.ReverseIpTagMultiCastSource,
                        cell_params_spike_injector_with_prefix, 
                        label='spike_injector_1')
        else:
            print 'nop'
            #cell_params_spike_injector_with_prefix = {'port' : 12345,
            #            'virtual_key'      : 0x70800}
            #inputWordSource = Population(NUMBER_WORDS+3,
            #            externaldevices.SpikeInjector,
            #            cell_params_spike_injector_with_prefix, 
            #            label='wordSpikesToBoard')

    elif simulator_name == 'nest':
        inputWordSource = Create('iaf_cond_exp', n=NUMBER_WORDS+3,
                        params = {'C_m':50.0,'V_th': -60.0, 'V_reset': -71.0, 't_ref':1.0})
    

def allocateWords():
    global WordsCells
    cell_params = {'tau_refrac' : 3.0, 'v_rest' : -65.0,
                    'v_thresh' : -51.0,  'tau_syn_E'  : 2.0, 
                    'tau_syn_I': 5.0,    'v_reset'    : -70.0, 
                    'i_offset' : 0.0}
    
    if simulator_name == 'spiNNaker':
        WordsCells=Population(NUMBER_WORDS*5,IF_curr_exp,cell_params)
    elif simulator_name == 'nest':
        WordsCells=Create('iaf_cond_exp', n=NUMBER_WORDS*5,
             params = {'C_m':50.0,'V_th': -60.0, 'V_reset': -71.0, 't_ref':1.0})


def allocateStates():
    global StatesCells
    cell_params = {'tau_refrac' : 3.0, 'v_rest' : -65.0,
           'v_thresh' : -51.0,  'tau_syn_E'  : 2.0, 
           'tau_syn_I': 5.0,    'v_reset'    : -70.0, 
           'i_offset' : 0.0}
#               'i_offset' : 0.1}

    if simulator_name == 'spiNNaker':
        StatesCells=Population(NUMBER_STATES*5,IF_curr_exp,cell_params)
        #StatesCells.set_mapping_constraint({'x':0, 'y':0, 'p': 11}) #48 board
    elif simulator_name == 'nest':
        StatesCells=Create('iaf_cond_exp',n=NUMBER_STATES*5,
           params = {'C_m':50.0,'V_th': -60.0, 'V_reset': -71.0, 't_ref':1.0})

# gating of the output spike: mod from Sergio's parser_synaptic_learning.py
# This does the work of Population for spinnaker and Create for nest
def createOutputPop(N,label=''):
    if simulator_name  == 'spiNNaker':
        cell_params_lif = {'cm'        : 0.25, # nF
                            'i_offset'  : 0.0,
                            'tau_m'     : 20.0,
                            'tau_refrac': 2.0,
                            'tau_syn_E' : 5.0,
                            'tau_syn_I' : 5.0,
                            'v_reset'   : -70.0,
                            'v_rest'    : -65.0,
                            'v_thresh'  : -50.0
                        }
    elif simulator_name  == 'nest':
        cell_params_lif = {'C_m':50.0,'V_th': -60.0, 'V_reset': -71.0, 't_ref':1.0} # , 'i_offset':0.0}

    if simulator_name == 'spiNNaker':
        return Population(N, IF_curr_exp, cell_params_lif, label=label)
    elif simulator_name == 'nest':
        return Create('iaf_cond_exp',n=N, params = cell_params_lif)

def allocateOutputGate():
    global OutputGateCells
    if simulator_name  == 'spiNNaker':
        cell_params_lif = {'cm'        : 0.25, # nF
                            'i_offset'  : 0.0,
                            'tau_m'     : 20.0,
                            'tau_refrac': 2.0,
                            'tau_syn_E' : 5.0,
                            'tau_syn_I' : 5.0,
                            'v_reset'   : -70.0,
                            'v_rest'    : -65.0,
                            'v_thresh'  : -50.0
                        }
    elif simulator_name  == 'nest':
        cell_params_lif = {'C_m':50.0,'V_th': -60.0, 'V_reset': -71.0, 't_ref':1.0} # , 'i_offset':0.0}

    if simulator_name == 'spiNNaker':
        OutputGateCells = Population(5, IF_curr_exp, cell_params_lif )
    elif simulator_name == 'nest':
        OutputGateCells = Create('iaf_cond_exp',n=5, params = cell_params_lif)


##----This is called from main
def allocateParseNeurons():
    allocateInputs()  # inputs = the starter
    allocateWords()
    allocateStates()
    #createOutputPop called from configureOutput in synapse creation
    allocateOutputGate()

# create spikers (inputSources) for up to 8 words
def setInputs():
    global inputSources
    if spikeServe:
        global playCells
        external_conns_params = {
            'virtual_key':      0x80800,
            'port':             12346}
        inputSourcePop = Population(NUMBER_WORDS+1, 
                    ExternalDevices.SpikeInjector, external_conns_params, 
                                 'external_conn_pop')
        cell_params = {'tau_refrac' : 3.0, 'v_rest' : -65.0,
           'v_thresh' : -51.0,  'tau_syn_E'  : 2.0, 
           'tau_syn_I': 5.0,    'v_reset'    : -70.0, 
           'i_offset' : 0.0}
        playCells=Population(NUMBER_WORDS+1,IF_curr_exp,cell_params)
        connector = []
        for i in range (0,NUMBER_WORDS+1):
            connector=connector+[(i,i,20.0,DELAY)]
        peterProjection(inputSourcePop,playCells,connector,
                            'excitatory')


    if spikeServe:
        #connect 0 spikeserver neuron to state 0
        connector = []
        for toNeuron in range (0,5):
            connector=connector+[(0,toNeuron,10.0,DELAY)]
        peterProjection(inputSourcePop,StatesCells,connector,
                            'excitatory')

        #connect the remaining spikeserver neruons to words
        connector = []
        for word in range (0,NUMBER_WORDS):
            fromNeuron = word + 1
            for toOff in range (0,5):
                toNeuron = (word*5)+toOff
                connector=connector+[(fromNeuron,toNeuron,10.0,DELAY)]
        peterProjection(inputSourcePop,WordsCells,connector,
                            'excitatory')

    elif ((simulator_name == 'spiNNaker') and (not spikeServe)):
        for i in range(0,7): 
            spikes = [[(i+1)*50]]
            inputSources[i]=Population(1,SpikeSourceArray,{'spike_times':spikes})       
        for i in range(7,14): 
            spikes = [[(i+3)*50]]
            inputSources[i]=Population(1,SpikeSourceArray,{'spike_times':spikes})
        for i in range(14,19): 
            spikes = [[(i+5)*50]]
            inputSources[i]=Population(1,SpikeSourceArray,{'spike_times':spikes})

    elif simulator_name == 'nest':
        #print "crh", sentence, " ", len (sentence)
        inputSources = []
        for i in range (0,len(sentence)+15):
            inputSources = inputSources+[i]

        inpSource = 0
        time = 7.0
        sentOff = 0
        for sent in range (0,15):
            inputSources[inpSource]=Create('spike_generator',
                                params={'spike_times': [time, time+3.0]})
            inpSource = inpSource+1
            time = time + 20.0
            while ((sentence[sentOff] != ".") and (sentence[sentOff] != "?")):
                inputSources[inpSource]=Create('spike_generator',
                                params={'spike_times': [time, time+3.0]})
                inpSource = inpSource+1
                time = time + 20.0
                sentOff = sentOff+1

            inputSources[inpSource]=Create('spike_generator',
                                params={'spike_times': [time, time+3.0]})
            inpSource = inpSource+1
            sentOff = sentOff+1
            time = time + 60.0
            sent = sent+1      
            


#The start state, and each word have an input connection
#link those to the appropriate (state) words

# called from set connections
def setInputConnections():
    # setSentence()
    # words = len(sentence)

    if simulator_name == 'spiNNaker':
        synWeight = 20.0
    elif simulator_name == 'nest':
        synWeight = 40.0

    # starter
    if spikeServe:
        print 'nop'
    elif simulator_name == 'spiNNaker':
        connector = []
        for toNeuron in range (0,5):
            connector=connector+[(0,toNeuron,synWeight,DELAY)]
            peterProjection(inputSources[0],StatesCells,
                                connector,'excitatory') 
            #start second sentence
            peterProjection(inputSources[7],StatesCells, connector,'excitatory') 
            #start third sentence
            peterProjection(inputSources[14],StatesCells, connector,'excitatory') 

        # for the words
        #2 six word sentences, 1 four word sentence, plus three new starts
        for i in range(0,6): 
            connector = []
            for toOff in range (0,5):
                toNeuron = lookupWord(sentence[i])*5 + toOff
                connector=connector+[(0,toNeuron,synWeight,DELAY)]
            peterProjection(inputSources[i+1],WordsCells,connector,'excitatory')

            for i in range(6,12): 
                connector = []
                for toOff in range (0,5):
                    toNeuron = lookupWord(sentence[i])*5 + toOff
                    connector=connector+[(0,toNeuron,synWeight,DELAY)]
            peterProjection(inputSources[i+2],WordsCells,connector,'excitatory')

            for i in range(12,16): 
                connector = []
                for toOff in range (0,5):
                    toNeuron = lookupWord(sentence[i])*5 + toOff
                    connector=connector+[(0,toNeuron,synWeight,DELAY)]
            peterProjection(inputSources[i+3],WordsCells,connector,'excitatory')
    elif simulator_name == 'nest':
        newParseStateConnector = []
        for toNeuron in range (0,5):
            newParseStateConnector=newParseStateConnector+[(0,toNeuron,synWeight,DELAY)]

        inpSource = 0
        sentOff = 0
        for sent in range (0,15):
            #make connections to start state
            peterProjection(inputSources[inpSource],StatesCells,
                            newParseStateConnector,'excitatory') 
            inpSource = inpSource+1

            #make connections to words
            while ((sentence[sentOff] != ".") and (sentence[sentOff] != "?")):
                connector = []
                for toOff in range (0,5):
                    toNeuron = lookupWord(sentence[sentOff])*5 + toOff
                    connector=connector+[(0,toNeuron,synWeight,DELAY)]
                peterProjection(inputSources[inpSource],WordsCells,
                                    connector,'excitatory')

                inpSource = inpSource+1
                sentOff = sentOff+1

            #period or question mark and next sentence
            connector = []
            for toOff in range (0,5):
                toNeuron = lookupWord(sentence[sentOff])*5 + toOff
                connector=connector+[(0,toNeuron,synWeight,DELAY)]
            peterProjection(inputSources[inpSource],WordsCells,
                                    connector,'excitatory')
            
            inpSource = inpSource+1
            sentOff = sentOff+1
            sent = sent+1


def lookupWord(word):
    try:
        ind = words.index(word)
    except KeyError:
        ind = NUMBER_WORDS-1
    return ind


# Use a state and an input to change states.
# Allow optional person, location, object results
# I'd like to make every other word go to error state to show a mis-parse,
# but what happens when there's a branch?
# I could do it explicitly
def makeTransition(preNum, catWords, postNum,
                   person=False, location=False, object=False, question=False):
    # global simulator_name
    if simulator_name == 'spiNNaker':
        stateToStateWeight = 0.2 
        wordToStateWeight = 0.3 
        wordToSemStateWeight = 0.7 # Thursday #6.0 
    elif simulator_name == 'nest':
        stateToStateWeight = 2.0
        wordToStateWeight = 2.0        
        wordToSemStateWeight = 5.0
    else:
        raise NotImplementedError(simulator_name)
    connectStateCAToStateCA(preNum,postNum,stateToStateWeight)
    StateCAStopsStateCA(postNum,preNum)
    for word in catWords:
        connectWordCAToStateCA(lookupWord(word),postNum,wordToStateWeight)
        StateCAStopsWordCA(postNum,lookupWord(word))
        # activate relevant semantic state
        if person:
            connectWordCAToStateCA(lookupWord(word),NUMBER_SYNSTATES + people.index(word),
                                        wordToSemStateWeight)
        if location:
            connectWordCAToStateCA(lookupWord(word),
                                        NUMBER_SYNSTATES + NUMBER_PEOPLE + locations.index(word),
                                        wordToSemStateWeight)
        if object:
            connectWordCAToStateCA(lookupWord(word),
                                        NUMBER_SYNSTATES + NUMBER_PEOPLE +
                                        NUMBER_LOCS + objects.index(word),
                                        wordToSemStateWeight)

        if question:
            connectWordCAToStateCA(lookupWord(word),
                                        NUMBER_SYNSTATES + NUMBER_PEOPLE +
                                        NUMBER_LOCS + NUMBER_OBJS +
                                        questions.index(word),
                                        wordToSemStateWeight)
        
def connectSemToOutputGate():
    if simulator_name == 'spiNNaker':
        synWeight = 0.025 #0.02 too little 0.06 one does it.
    elif simulator_name == 'nest':
        synWeight = 2.0  #1.2 is too little  2.0 pops at second sem second spike
    connector = []
    semCAStart = NUMBER_SYNSTATES 
    semCAFinish = NUMBER_SYNSTATES + NUMBER_PEOPLE + NUMBER_LOCS + NUMBER_OBJS + NUMBER_QUES 
    for fromSemCA in range (semCAStart,semCAFinish):
        for fromOff in range (0,5):
            for toNeuron in range (0,5):
                fromNeuron = fromSemCA*5 + fromOff
                connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
    peterProjection(StatesCells,OutputGateCells, connector,'excitatory')


#The output gate comes on when two semantics are on.  
#The output gate is needed to make output fire, so
#both of the outputs come in the same cycle
def connectOutputGateToOutput():
    if simulator_name == 'spiNNaker':
        synWeight = 0.13 
    elif simulator_name == 'nest':
        synWeight = 2.0 #.13 too low 
    connector = []
    outputCAs = NUMBER_PEOPLE + NUMBER_LOCS + NUMBER_OBJS + NUMBER_QUES 
    for fromNeuron in range (0,5):
        for toOutputCA in range (0,outputCAs):
            for toOff in range (0,5):
                toNeuron = toOutputCA*5 + toOff
                connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
    peterProjection(OutputGateCells,pop_outputs, connector,'excitatory')

def dictComp(wlist):
    #print(list(set(words) - set(wlist)))
    return list(set(words) - set(wlist))

def makeTransitions():
    for [args, kwargs] in TRANSITIONS:
        makeTransition(*args, **kwargs)        

def configureOutput():
    global pop_outputs #, gate_outputs
    numOuts = NUMBER_PEOPLE+NUMBER_LOCS+NUMBER_OBJS+NUMBER_QUES 
    # Outputs
    # sergio suggested 1 neuron could be a problem, so I'll try 5 like others
    pop_outputs = createOutputPop((numOuts)*5, label='pop_outputs') 

    # Gates

    #weight_to_spike = 2.0
    if simulator_name == 'spiNNaker':
        weight_to_spike = 10.0
        weight_sem_to_out = 0.02 
    elif simulator_name == 'nest':
        weight_to_spike = 10.0
        weight_sem_to_out = 0.8 #Aug 3

    # weight_to_gate = weight_to_spike * 0.05
    weight_to_control = weight_to_spike * 0.2
    weight_to_inhibit = weight_to_spike * 0.05 # 1 # 2 # 5
    weight_to_turnoff = weight_to_spike * 0.5 # 1 # 2 # 5

    # excitatory: weight_to_controls - allToAll -
    # from all the semantic neurons - to the output population
    if simulator_name == 'spiNNaker':
        weight_to_control = 0.001 #This is a bit dodgy.  Syntax no
                                  #longer stops the parse.  Could increase
                                  #to help semantics (2 sems) stop it.

    connectors = []
    for semNum in range (0, numOuts):
        for fromOff in range (0,5):
            fromNeuron = (NUMBER_SYNSTATES + semNum)*5 + fromOff
            for toOff in range (0,5):
                toNeuron = semNum*5 + toOff
                connectors=connectors+[(fromNeuron,toNeuron,weight_sem_to_out,DELAY)]
    peterProjection(StatesCells, pop_outputs, connectors,'excitatory')
    

    # Control: - excitatory: weight_to_control - allToAll (5 * 30*5)
    # - from syn state 9 - to the outputs
    connectors = []
    for fromOff in range (0,5):
        fromNeuron = finalSynStateAssertion*5 + fromOff
        for semNum in range (0, numOuts):
            for toOff in range (0, 5):
                toNeuron = semNum*5 + toOff
                connectors=connectors+[(fromNeuron,toNeuron,weight_to_control,DELAY)]
    peterProjection(StatesCells, pop_outputs, connectors,'excitatory')

    # Adding activate pop_out for the end of the query
    connectors = []
    for fromOff in range (0,5):
        fromNeuron = finalSynStateQuery*5 + fromOff
        for semNum in range (0, numOuts):
            for toOff in range (0, 5):
                toNeuron = semNum*5 + toOff     
                connectors=connectors+[(fromNeuron,toNeuron,weight_to_control,DELAY)]
    peterProjection(StatesCells, pop_outputs, connectors,'excitatory')

   
    # turnOffSem: - inhibitory - allToAll 30 * (5 * 5)
    # - from the outputs - to the semantic neurons
    if simulator_name == 'spiNNaker':
        stopAllStatesWeight = -0.5
    elif simulator_name == 'nest':
        stopAllStatesWeight = -12.0 #8.0 stops syn not sem
    connectors = []
    for fromNeuron in range (0,numOuts*5):
        for toNeuron in range (0,NUMBER_STATES*5):
            connectors=connectors+[(fromNeuron,toNeuron,stopAllStatesWeight,
                                    DELAY)]
    peterProjection(pop_outputs, StatesCells, connectors,'inhibitory')

        
## this is called from Main
def setConnections():
    setInputConnections()
    makeWordCAs()
    makeStateCAs()
    makeTransitions()
    connectSemToOutputGate()
    configureOutput()
    connectOutputGateToOutput() 

##--- record---

# this is called from Main
def setRecording():
    global multS, multW, multOut, multOutGate,multSp
    if simulator_name == 'spiNNaker':
        WordsCells.record()
        StatesCells.record()
        pop_outputs.record()
        OutputGateCells.record()
    elif simulator_name == 'nest':
        multS = Create('multimeter', params = {'withtime': True, 
                      'interval': 1.0,
                      'record_from': ['V_m']})
        Connect(multS, StatesCells)

        multW= Create('multimeter', params = {'withtime': True, 
                      'interval': 1.0,
                      'record_from': ['V_m']})
        Connect(multW, WordsCells)

        multOut= Create('multimeter', params = {'withtime': True, 
                      'interval': 1.0,
                      'record_from': ['V_m']})
        Connect(multOut, pop_outputs)

        multOutGate= Create('multimeter', params = {'withtime': True, 
                      'interval': 1.0,
                      'record_from': ['V_m']})
        Connect(multOutGate, OutputGateCells)

        multSp = Create('spike_detector')
        Connect(pop_outputs, multSp)
        Connect(StatesCells, multSp)
        Connect(WordsCells, multSp)

        # multSpW = Create('spike_detector')
        # Connect(StatesCells, multSp)
                                                         
        #WordsCells.record('spikes')
        #StatesCells.record('spikes')

#-----printing and plotting
def nestPrint(printText,CA):
        print printText
        outAssembly = Assembly(CA[(0,1)])
        outDat = outAssembly.get_data()
        for seg in outDat.segments:
            print(seg.spiketrains)
            #    print(seg.analogsignalarrays)

def plotSpikes(spikes,filename):
    if spikes is not None:
        print'======= spikes ========'
        print spikes
        pl.figure()
        pl.plot([i[1] for i in spikes], [i[0] for i in spikes], ".")
        pl.xlabel('Time/ms')
        pl.ylabel('spikes')
        pl.title('spikes %s'%filename)
        pl.savefig("spikes_%s.png"%filename)
        pl.show()
    else:
        print "No spikes received"
        
def spinPlot():
    WordSpikes = WordsCells.getSpikes(compatible_output=True)
    StateSpikes= StatesCells.getSpikes(compatible_output=True)
    OutSpikes= pop_outputs.getSpikes(compatible_output=True)

    plotSpikes(StateSpikes,'TR_states')
    plotSpikes(OutSpikes,'TR_Outputs')
    plotSpikes(WordSpikes,'TR_words')
    '''
    n_panels = 2
    pl.subplot(n_panels, 1, 1)
    plot_spiketrains(getStates().get_data().segments[0], "States")
    pl.subplot(n_panels,  1, 2)
    plot_spiketrains(getWords().get_data().segments[0], "Words")
    pl.savefig('wordandState_plot')
    pl.show()
    '''
    end()

def nestPlot():
    #print printText
    #outAssembly = Assembly(CA[(0,1)])
    #nest.raster_plot.from_device(multSp) # hist=True
    pl.scatter(nest.GetStatus(multSp)[0]['events']['times'],
               nest.GetStatus(multSp)[0]['events']['senders'],
               s=1, color='b')
    pl.ylim([0,(5 + NUMBER_WORDS + NUMBER_STATES)*5+(NUMBER_PEOPLE+NUMBER_LOCS+NUMBER_OBJS+NUMBER_QUES)*5])
    pl.xlim([0,SIM_LENGTH*0.5])
    pl.yticks(pl.yticks()[0],[str(int(a/5)) for a in pl.yticks()[0]])
    pl.show()


def printWords():
    print "words"
    if simulator_name == 'spiNNaker':
        WordsCells.printSpikes('results/parseWords.sp')
    elif simulator_name == 'nest':
        events = GetStatus(multW)[0]['events']
        volts=events.items()[0]
        volts=volts[1]
        count = 0
        numNeurons = NUMBER_WORDS*5
        for outp in volts:
            print count/numNeurons, ' ' , count % numNeurons, ' ' ,outp
            count = count + 1

def printStates():
    print "states"
    if simulator_name == 'spiNNaker':
        StatesCells.printSpikes('results/parseStates.sp')
    elif simulator_name == 'nest':
        events = GetStatus(multS)[0]['events']
        volts=events.items()[0]
        volts=volts[1]
        count = 0
        numNeurons = NUMBER_STATES*5
        for outp in volts:
            print count/numNeurons, ' ' , count % numNeurons, ' ' ,outp
            count = count + 1
        

def printOutputs():
    print "outputs"
    if simulator_name == 'spiNNaker':
        print 'nop'
        pop_outputs.printSpikes('results/parseOutputs.sp')
    elif simulator_name == 'nest':
        events = GetStatus(multOut)[0]['events']
        volts=events.items()[0]
        volts=volts[1]
        count = 0
        numNeurons = (NUMBER_PEOPLE+NUMBER_LOCS+NUMBER_OBJS+NUMBER_QUES)*5
        for outp in volts:
            print count/numNeurons, ' ' , count % numNeurons, ' ' ,outp
            count = count + 1

def printOutputGate():
    if simulator_name == 'spiNNaker':
        OutputGateCells.printSpikes('results/parseOutputGate.sp')
    elif simulator_name == 'nest':
        events = GetStatus(multOutGate)[0]['events']
        volts=events.items()[0]
        volts=volts[1]
        count = 0
        numNeurons = 5
        for outp in volts:
            print count/numNeurons, ' ' , count % numNeurons, ' ' ,outp
            count = count + 1
        print 'nop'


def printResults():
    #return
    #printWords()
    #printStates()
    printOutputs()
    #printOutputGate()

def getStates():
    return StatesCells

def parse(sim, sent):
    global sentence, simulator_name

    if isinstance(sent,basestring):
        sentence = re.findall(r"[\w']+|[.,!?;]", sent)
    else:
        sentence = sent

    # canonicalize sim_name
    simulator_name = sim
    print 'Simulator: '+ simulator_name + ', Sentence: ' + sent

    # print simulator_name
    
    if simulator_name in ('spinnaker', 'spin', ''):
        simulator_name = 'spiNNaker'

    if simulator_name == 'spiNNaker':
        setup(timestep=DELAY,min_delay=DELAY,max_delay=DELAY)
    elif simulator_name == 'nest':
        ResetKernel()

    #----------------create neurons
    # parse = parseArea(simulator_name, sentence)
    allocateParseNeurons()

    #turn on the inputs
    setInputs()

    #---------setup connections
    setConnections()

    #-------------------setup recording
    setRecording()

    if simulator_name == 'spiNNaker':
        run(SIM_LENGTH)
    elif simulator_name == 'nest':
        Simulate(4050)

    #--------------print results
    if simulator_name == 'spiNNaker':
        #spinPlot()
        printStates()
        printOutputs()
    elif simulator_name == 'nest':
        if plot:
            nestPlot()
        else:
            printResults()

def parseNestSMem(sim):
    global simulator_name, sentence
    simulator_name = sim
    if simulator_name != 'nest':
        print 'parseNestSMem should only be called with nest'
        return

    testNum = 0  #undone add support for calling different tests
    hugeSentenceList = getSentences("train.txt")
    sentence = ""
    for sentenceNum in range ((testNum*15),(testNum+1)*15):
        inputTuple = hugeSentenceList[sentenceNum]
        Sentence = inputTuple[1]
        lSentence = Sentence.lower()
        sentence = sentence + " " + lSentence

    sentence = re.findall(r"[\w']+|[.,!?;]", sentence)

    grammar = "grammar_qa1"    
    exec("from %s import *" % grammar)

    ResetKernel()

    #----------------create neurons
    # parse = parseArea(simulator_name, sentence)
    allocateParseNeurons()

    #turn on the inputs
    setInputs()

    #---------setup connections
    setConnections()

    #-------------------setup recording
    setRecording()

    if simulator_name == 'spiNNaker':
        run(SIM_LENGTH)
    elif simulator_name == 'nest':
        Simulate(4050)

    #--------------print results
    if simulator_name == 'spiNNaker':
        #spinPlot()
        printStates()
        printOutputs()
    elif simulator_name == 'nest':
        if plot:
            nestPlot()
        else:
            printResults()

def parseNestSMemNoRun(sim):
    global simulator_name, sentence
    simulator_name = sim
    if simulator_name != 'nest':
        print 'parseNestSMem should only be called with nest'
        return

    testNum = 0  #undone add support for calling different tests
    hugeSentenceList = getSentences("train.txt")
    sentence = ""
    for sentenceNum in range ((testNum*15),(testNum+1)*15):
        inputTuple = hugeSentenceList[sentenceNum]
        Sentence = inputTuple[1]
        lSentence = Sentence.lower()
        sentence = sentence + " " + lSentence

    sentence = re.findall(r"[\w']+|[.,!?;]", sentence)

    grammar = "grammar_qa1"    
    exec("from %s import *" % grammar)

    #----------------create neurons
    # parse = parseArea(simulator_name, sentence)
    allocateParseNeurons()

    #turn on the inputs
    setInputs()

    #---------setup connections
    setConnections()

    #-------------------setup recording
    setRecording()

#To use with memory
def parse_no_run(sim, sent):
    global sentence, simulator_name

    print 'pnr'
 
    #exec("from %s import *" % grammar)
 
    SIM_LENGTH=450
    SUB_POPULATION_SIZE=5
    intervalAction=100

    print sent
    if isinstance(sent,basestring):
        sentence = re.findall(r"[\w']+|[.,!?;]", sent)
    else:
        sentence = sent

    # canonicalize sim_name
    simulator_name = sim
    print simulator_name
    
    if simulator_name in ('spinnaker', 'spin', ''):
        simulator_name = 'spiNNaker'

    #----------------create neurons
    # parse = parseArea(simulator_name, sentence)
    allocateParseNeurons()

    #turn on the inputs
    setInputs()

    #---------setup connections
    setConnections()

    #-------------------setup recording
    setRecording()
    if spikeServe:
        playCells.record()

def parse_no_run2(sim):
    global simulator_name

    print 'pnr2'
 
    #exec("from %s import *" % grammar)
 
    SIM_LENGTH=450
    SUB_POPULATION_SIZE=5
    intervalAction=100

    #print sent
    #sentence = re.findall(r"[\w']+|[.,!?;]", sent)

    # canonicalize sim_name
    simulator_name = sim
    print simulator_name
    
    if simulator_name in ('spinnaker', 'spin', ''):
        simulator_name = 'spiNNaker'

    #----------------create neurons
    # parse = parseArea(simulator_name, sentence)
    allocateParseNeurons()

    #turn on the inputs
    setInputs()

    #---------setup connections
    setConnections()

    #-------------------setup recording
    setRecording()
    if spikeServe:
        playCells.record()

#------------Main Body---------------
if __name__ == "__main__":
    global simulator_name
    import sys
    inputArgLength = len (sys.argv)
    if inputArgLength != 4:
        simulator_name = "nest"
        testNum = 0
        hugeSentenceList = getSentences("train.txt")
        sentence = ""
        for sentenceNum in range ((testNum*15),(testNum+1)*15):
            inputTuple = hugeSentenceList[sentenceNum]
            Sentence = inputTuple[1]
            lSentence = Sentence.lower()
            sentence = sentence + " " + lSentence
        grammar = "grammar_qa1"    
    else:
        simulator_name = sys.argv[1]
        sentence = sys.argv[2]
        grammar = sys.argv[3]

    #from pyNN.utility import get_script_args
    #simulator_name = get_script_args(3,"Booboo! Please supply simulator (nest|spin), sentence, and grammar")[0]
    #sentence = get_script_args(3)[1]
    #grammar = get_script_args(3)[2]  

    exec("from %s import *" % grammar)

    SIM_LENGTH=1500
    SUB_POPULATION_SIZE=5
    intervalAction=100

    parse(simulator_name,sentence)






