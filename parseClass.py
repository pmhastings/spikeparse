"""
Parsing class with functions to create and run parsing.
It's really just a big FSA to deal with all the sentences.  The final
state is unique for each sentence considered.
It's tested by messing about with setInputs words.
You can see the output in the results/AllStates.sp file.
If you tail it, it should end with the neurons for the final 
state

To add a new sentence,
    add a new word CA in allocateWords
    add new state CAs in allocateStates
    for this test, change inputs in setInputConnections
    make the word a CA in makeWordCAs
    make the state CAs in makeStateCAs
    make the state transitions in makeTransitions
    record
    print
"""
# Grammar:
# S <- PN VP .
# PN: Person -> states(Person(i))
# VP <- "is in" LNP
#    <- "has" ONP
# LNP: (the) Loc: Loc -> states(Loc(i))
# ONP: the|a Obj: Obj -> states(Object(i))

# As a graph
# 0 -PN-> 1 PN ->Sem(pers(i))
# 1 -is-> 2
#   -has-> 7
# 2 -in-> 3
# 3 -Loc-> 9: Sem(loc(j))
#   -the-> 5
# 5 -Loc-> 9: Sem(loc(j))
# 7 -the|a-> 8
# 8 -Obj-> 9: Sem(obj(k))

import pylab as pl

from pyNN.utility.plotting import Figure, Panel

#imports for PyNN
# from pyNN.spiNNaker import *
#from nest import *
#simulator_name = "nest"

# from pyNN.utility import get_script_args
# simulator_name = get_script_args(1)[0]  
# if simulator_name in ('spinnaker', 'spin'):
#     simulator_name = 'spiNNaker'
# if simulator_name == 'spiNNaker':
#     from pyNN.spiNNaker import *
# elif simulator_name == 'nest':
#     from nest import *
#     import nest.raster_plot

# Just importing everything because it was a pain to check which to import
from pyNN.spiNNaker import *
from nest import *
import nest.raster_plot

#import for spike injection
# Ian doesn't think we really need these
# On second thought, we do
import spynnaker_external_devices_plugin.pyNN as externaldevices
from spinnman.messages.eieio.eieio_prefix_type import EIEIOPrefixType

#NEAL files and functions
# from nealParams import *
# I think this is the only thing from nealParams that was used
DELAY = 1.0

class parseArea:

    #sentence = "John is in the kitchen."
    #sentence = ['John', 'is', 'in', 'the', 'kitchen', '.']

    locations = ["kitchen", "classroom1", "classroom2", "lecture_room"]
    objects = ["ball", "dog", "cube", "hyperplane", "spike"]
    people = ["John", "Sergio", "Peter", "Guido", "Ritwik", "Eric", "Philip", "Kan", "Shashi", "Pam"]
    locVerbs = ["is in", "are in"]
    words = {'.': 0,
            'unknown': 1,
            '2': 2,
            'Eric': 3,
            'Guido': 4,
            'John': 5,
            'Kan': 6,
            'Pam': 7,
            'Peter': 8,
            'Philip': 9,
            'Ritwik': 10,
            'Sergio': 11,
            'Shashi': 12,
            'a': 13,
            'ball': 14,
            'classroom1': 15,
            'classroom2': 16,
            'cube': 17,
            'dog': 18,
            'has': 19,
            'hyperplane': 20,
            'in': 21,
            'is': 22,
            'kitchen': 23,
            'lecture_room': 24,
            'pointer': 25,
            'spike': 26,
            'the': 27,
            'where': 28,
            'who': 29}

    NUMBER_WORDS = 30

    NUMBER_SYNSTATES = 10
    NUMBER_PEOPLE = 10
    NUMBER_LOCS = 10
    NUMBER_OBJS = 10
    NUMBER_STATES = NUMBER_SYNSTATES + NUMBER_PEOPLE + NUMBER_LOCS + NUMBER_OBJS


    def __init__(self, simName, sent):
        self.simulator_name = simName
        self.sentence = sent

    #----helper functions
    def nealProjection(self,preNeurons,postNeurons, connectorList,inhExc):
        if self.simulator_name == 'spiNNaker':
            Projection(preNeurons, postNeurons, connectorList,target=inhExc)
        elif self.simulator_name == 'nest':
            # Projection(preNeurons, postNeurons, connectorList)
            for connection in connectorList:
                Connect(preNeurons[connection[0]],postNeurons[connection[1]],
                        {'weight':connection[2]})
        else:
            print 'bad simulator for nealProjection'

    def peterProjection(self, preNeurons, postNeurons, connector, inhExc):
        if self.simulator_name == 'spiNNaker':
            excConnector = FromListConnector(connector)
            self.nealProjection(preNeurons, postNeurons, excConnector, inhExc)
        elif self.simulator_name == 'nest':
            self.nealProjection(preNeurons, postNeurons, connector, inhExc)


    def makeCASynapses(self,CAsCells,numberCAs):
        if self.simulator_name == 'spiNNaker':
            synWeight = 8.0
        elif self.simulator_name == 'nest':
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
        self.peterProjection(CAsCells,CAsCells, connector,'excitatory')
    
    #connect word to state
    def connectWordCAToStateCA(self,fromNum,toNum,synWeight):
        connector = []
        for fromOff in range (0,5):
            for toOff in range (0,5):
                fromNeuron = fromNum*5 + fromOff
                toNeuron = toNum*5 + toOff
                connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
        self.peterProjection(self.WordsCells,self.StatesCells, connector,'excitatory')

    #connect state to state
    def connectStateCAToStateCA(self,fromNum,toNum,synWeight):
        connector = []
        for fromOff in range (0,5):
            for toOff in range (0,5):
                fromNeuron = fromNum*5 + fromOff
                toNeuron = toNum*5 + toOff
                connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
        self.peterProjection(self.StatesCells,self.StatesCells, connector,'excitatory')

    #state stops word
    def StateCAStopsWordCA(self,fromNum, toNum):
        synWeight = -10.0
        connector = []
        for fromOff in range (0,5):
            for toOff in range (0,5):
                fromNeuron = fromNum*5+fromOff
                toNeuron = toNum*5 + toOff
                connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
        self.peterProjection(self.StatesCells,self.WordsCells, connector, 'inhibitory')

    #state stops state
    def StateCAStopsStateCA(self,fromNum,toNum):
        if self.simulator_name == 'spiNNaker':
            synWeight = -10.0
        elif self.simulator_name == 'nest':
            synWeight = -25.0
        connector = []
        for fromOff in range (0,5):
            for toOff in range (0,5):
                fromNeuron = fromNum*5 + fromOff
                toNeuron = toNum*5 + toOff
                connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
        self.peterProjection(self.StatesCells,self.StatesCells, connector,'inhibitory')

    def CAStopsCA2(self,fromCA,toCA,toNum):
        synWeight = -10.0
        connector = []
        for fromNeuron in range (0,5):
            for toOff in range (0,5):
                toNeuron = toNum*5 + toOff
                connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
        self.peterProjection(fromCA,toCA, connector,'inhibitory')

    def CAStopsCA(self,fromCA,toCA):
        synWeight = -10.0
        connector = []
        for fromNeuron in range (0,5):
            for toNeuron in range (0,5):
                connector=connector+[(fromNeuron,toNeuron,synWeight,DELAY)]
        self.peterProjection(fromCA,toCA, connector,'inhibitory')

    #-----functions called externally and their subfunctions
    #---create the neurons for the CAs
    def allocateInputs(self):
        cell_params_spike_injector_with_prefix = {'host_port_number' : 12345,
                            'host_ip_address'  : "localhost",
                            'virtual_key'      : 0x70800,
                            'prefix'           : 7,
                            'prefix_type': EIEIOPrefixType.UPPER_HALF_WORD}
        if self.simulator_name == 'spiNNaker':
            self.inputWordSource = Population(self.NUMBER_WORDS+3,
                            externaldevices.ReverseIpTagMultiCastSource,
                            cell_params_spike_injector_with_prefix, 
                            label='spike_injector_1')
        elif self.simulator_name == 'nest':
            self.inputWordSource = Create('iaf_cond_exp', n=self.NUMBER_WORDS+3,
                            params = {'C_m':50.0,'V_th': -60.0, 'V_reset': -71.0, 't_ref':1.0})
        

    def allocateWords(self):
        cell_params = {'tau_refrac' : 3.0, 'v_rest' : -65.0,
                        'v_thresh' : -51.0,  'tau_syn_E'  : 2.0, 
                        'tau_syn_I': 5.0,    'v_reset'    : -70.0, 
                        'i_offset' : 0.0}
        
        if self.simulator_name == 'spiNNaker':
            self.WordsCells=Population(self.NUMBER_WORDS*5,IF_curr_exp,cell_params)
        elif self.simulator_name == 'nest':
            self.WordsCells=Create('iaf_cond_exp', n=self.NUMBER_WORDS*5,
                 params = {'C_m':50.0,'V_th': -60.0, 'V_reset': -71.0, 't_ref':1.0})


    def allocateStates(self):
        cell_params = {'tau_refrac' : 3.0, 'v_rest' : -65.0,
               'v_thresh' : -51.0,  'tau_syn_E'  : 2.0, 
               'tau_syn_I': 5.0,    'v_reset'    : -70.0, 
               'i_offset' : 0.0}
#               'i_offset' : 0.1}

        if self.simulator_name == 'spiNNaker':
            self.StatesCells=Population(self.NUMBER_STATES*5,IF_curr_exp,cell_params)
            #self.StatesCells.set_mapping_constraint({'x':0, 'y':0, 'p': 11}) #48 board
        elif self.simulator_name == 'nest':
            self.StatesCells=Create('iaf_cond_exp',n=self.NUMBER_STATES*5,
               params = {'C_m':50.0,'V_th': -60.0, 'V_reset': -71.0, 't_ref':1.0})

    def allocateParseNeurons(self):
        self.allocateInputs()  # inputs = the starter
        self.allocateWords()
        self.allocateStates()

    # create spikers (inputSources) for up to 8 words
    def setInputs(self):
        self.inputSources = [0,1,2,3,4,5,6,7,8]
        if self.simulator_name == 'spiNNaker':
            for i in range(0,9):
                spikes = [[(i+1)*50]]
                self.inputSources[i]=Population(1,SpikeSourceArray,{'spike_times':spikes})
        elif self.simulator_name == 'nest':
            # why the diff in params? I don't know
            for i in range(0,9):
                self.inputSources[i]=Create('spike_generator',
                                            params={'spike_times': [(i*20)+7.0,(i*20)+10.0]})

    #----Make Synapses
    #The start state, and each word have an input connection
    #link those to the appropriate (state) words

    # called from set connections
    def setInputConnections(self):
        # self.setSentence()
        # self.words = len(self.sentence)

        if self.simulator_name == 'spiNNaker':
            synWeight = 20.0
        else:
            synWeight = 40.0

        # starter
        connector = []
        for toNeuron in range (0,5):
            connector=connector+[(0,toNeuron,synWeight,DELAY)]
            self.peterProjection(self.inputSources[0],self.StatesCells,
                                    connector,'excitatory') 

        # for the words
        for i in range(0,len(self.sentence)):
            connector = []
            for toOff in range (0,5):
                toNeuron = self.lookupWord(self.sentence[i])*5 + toOff
                connector=connector+[(0,toNeuron,synWeight,DELAY)]
            self.peterProjection(self.inputSources[i+1],self.WordsCells,connector,
                                'excitatory')


    def makeWordCAs(self):
        self.makeCASynapses(self.WordsCells,self.NUMBER_WORDS)


    def makeStateCAs(self):
        self.makeCASynapses(self.StatesCells,self.NUMBER_STATES)

        
    def lookupWord(self,word):
        try:
            ind = self.words[word]
        except KeyError:
            ind = self.words['unknown']
        return ind
    

    # Use a state and an input to change states.
    # Allow optional person, location, object results
    # I'd like to make every other word go to error state to show a mis-parse,
    # but what happens when there's a branch?
    # I could do it explicitly
    def makeTransition(self, preNum, catWords, postNum,
                       person=False, location=False, object=False):
        if self.simulator_name == 'spiNNaker':
            stateToStateWeight = 0.2
            wordToStateWeight = 0.3
            wordToSemStateWeight = 0.5
        elif self.simulator_name == 'nest':
            stateToStateWeight = 2.0
            wordToStateWeight = 2.0        
            wordToSemStateWeight = 5.0        
        self.connectStateCAToStateCA(preNum,postNum,stateToStateWeight)
        self.StateCAStopsStateCA(postNum,preNum)
        for word in catWords:
            self.connectWordCAToStateCA(self.lookupWord(word),postNum,wordToStateWeight)
            self.StateCAStopsWordCA(postNum,self.lookupWord(word))
            # activate relevant semantic state
            if person:
                self.connectWordCAToStateCA(self.lookupWord(word),self.NUMBER_SYNSTATES + self.people.index(word),
                                            wordToSemStateWeight)
            if location:
                self.connectWordCAToStateCA(self.lookupWord(word),
                                            self.NUMBER_SYNSTATES + self.NUMBER_PEOPLE + self.locations.index(word),
                                            wordToSemStateWeight)
            if object:
                self.connectWordCAToStateCA(self.lookupWord(word),
                                            self.NUMBER_SYNSTATES + self.NUMBER_PEOPLE +
                                            self.NUMBER_LOCS + self.objects.index(word),
                                            wordToSemStateWeight)
            

    def dictComp(self, wlist):
        #print(list(set(self.words) - set(wlist)))
        return list(set(self.words) - set(wlist))

    # Grammar graph as above
    def makeTransitions(self):
        # 0 -PN-> 1 PN ->Sem(pers(i))
        self.makeTransition(0,self.people,1,person=True)
        # 0 -^PN-> 6  (error)
        self.makeTransition(0,self.dictComp(self.people),6)
        # 1 -is-> 2
        self.makeTransition(1,['is'],2)
        #   -has-> 7
        self.makeTransition(1,['has'],7)
        # 1 -^(is|has)-> 6 PN  (error)
        #self.makeTransition(1,self.dictComp(['is','has']),6)
        # 2 -in-> 3
        self.makeTransition(2,['in'],3)
        # 2 -^in-> 6  (error)
        #self.makeTransition(2,self.dictComp(['in']),6)
        # 3 -Loc-> 9: Sem(loc(j))
        self.makeTransition(3,self.locations,9,location=True)
        #   -the-> 5
        self.makeTransition(3,['the'],5)
        # 3 -^(loc|the)-> 6  (error)
        #self.makeTransition(3,self.dictComp(self.locations+['the']),6)
        # 5 -Loc-> 9: Sem(loc(j))
        self.makeTransition(5,self.locations,9,location=True)
        # 5 -^Loc-> 6  (error)
        #self.makeTransition(5,self.dictComp(self.locations),6)
        # 7 -the|a-> 8
        self.makeTransition(7,['the','a'],8)
        # 7 -^(the|a)-> 6  (error)
        #self.makeTransition(7,self.dictComp(['the','a']),6)
        # 8 -Obj-> 9: Sem(obj(k))
        self.makeTransition(8,self.objects,9,object=True)
        # 8 -^Obj-> 6  (error)
        #self.makeTransition(8,self.dictComp(self.objects),6)


    # this is called from Main
    def setConnections(self):
        self.setInputConnections()
        self.makeWordCAs()
        self.makeStateCAs()
        self.makeTransitions()
        self.configureOutput()

    # this is called from Main
    def setRecording(self):
        if self.simulator_name == 'spiNNaker':
			self.WordsCells.record()
			self.StatesCells.record()
			self.pop_outputs.record()
        elif self.simulator_name == 'nest':
            self.multS = Create('multimeter', params = {'withtime': True, 
                          'interval': 1.0,
                          'record_from': ['V_m']})
            Connect(self.multS, self.StatesCells)

            self.multW= Create('multimeter', params = {'withtime': True, 
                          'interval': 1.0,
                          'record_from': ['V_m']})
            Connect(self.multW, self.WordsCells)

            self.multSp = Create('spike_detector')
            Connect(self.pop_outputs, self.multSp)
            Connect(self.StatesCells, self.multSp)
            Connect(self.WordsCells, self.multSp)

            # self.multSpW = Create('spike_detector')
            # Connect(self.StatesCells, self.multSp)

                                                             
            #self.WordsCells.record('spikes')
            #self.StatesCells.record('spikes')

    #-----printing
    def nestPrint(self,printText,CA):
            print printText
            outAssembly = Assembly(CA[(0,1)])
            outDat = outAssembly.get_data()
            for seg in outDat.segments:
                print(seg.spiketrains)
                #    print(seg.analogsignalarrays)

    def plotSpikes(self,spikes,filename):
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
            
    def spinPlot(self):
        WordSpikes = self.WordsCells.getSpikes(compatible_output=True)
        StateSpikes= self.StatesCells.getSpikes(compatible_output=True)
        OutSpikes= self.pop_outputs.getSpikes(compatible_output=True)

        self.plotSpikes(StateSpikes,'TR_states')
        self.plotSpikes(OutSpikes,'TR_Outputs')
        self.plotSpikes(WordSpikes,'TR_words')
        '''
        n_panels = 2
        pl.subplot(n_panels, 1, 1)
        plot_spiketrains(self.getStates().get_data().segments[0], "States")
        pl.subplot(n_panels,  1, 2)
        plot_spiketrains(self.getWords().get_data().segments[0], "Words")
        pl.savefig('wordandState_plot')
        pl.show()
        '''
        end()

    def nestPlot(self):
        #print printText
        #outAssembly = Assembly(CA[(0,1)])
        #nest.raster_plot.from_device(self.multSp) # hist=True
        pl.scatter(nest.GetStatus(self.multSp)[0]['events']['times'],
                   nest.GetStatus(self.multSp)[0]['events']['senders'],
                   s=1, color='b')
        pl.ylim([0,(self.NUMBER_WORDS + self.NUMBER_STATES)*5+self.NUMBER_PEOPLE+self.NUMBER_LOCS+self.NUMBER_OBJS])
        pl.xlim([0,200])
        pl.yticks(pl.yticks()[0],[str(int(a/5)) for a in pl.yticks()[0]])
        pl.show()


    def printWords(self):
        if self.simulator_name == 'spiNNaker':
            self.WordsCells.printSpikes('results/AllWords.sp')
        elif self.simulator_name == 'nest':
            print "nop"
            events = GetStatus(self.multW)[0]['events']
            volts=events.items()[0]
            volts=volts[1]
            count = 0
            numNeurons = self.NUMBER_WORDS*5
            for outp in volts:
                print count/numNeurons, ' ' , count % numNeurons, ' ' ,outp
                count = count + 1

    def printStates(self):
        if self.simulator_name == 'spiNNaker':
            self.StatesCells.printSpikes('results/parseStates.sp')

        elif self.simulator_name == 'nest':
            print "nop"
            events = GetStatus(self.multS)[0]['events']
            volts=events.items()[0]
            volts=volts[1]
            count = 0
            numNeurons = self.NUMBER_STATES*5
            for outp in volts:
                print count/numNeurons, ' ' , count % numNeurons, ' ' ,outp
                count = count + 1
            
    def printInputs(self):
        self.InputSources[1].printSpikes('results/Inps.sp')


    def printResults(self):
        #self.printInputs()
        #self.printWords()
        self.printStates()

    def getStates(self):
        return self.StatesCells


    # gating of the output spike: mod from Sergio's parser_synaptic_learning.py
    # This does the work of Population for spinnaker and Create for nest
    def createPop(self,N,label=''):
        if self.simulator_name  == 'spiNNaker':
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
        elif self.simulator_name  == 'nest':
            cell_params_lif = {'C_m':50.0,'V_th': -60.0, 'V_reset': -71.0, 't_ref':1.0}
        if self.simulator_name == 'spiNNaker':
            return Population(N, IF_curr_exp, cell_params_lif, label=label)
        elif self.simulator_name == 'nest':
            return Create('iaf_cond_exp',n=N, params = cell_params_lif)

    def configureOutput(self):
        numOuts = self.NUMBER_PEOPLE+self.NUMBER_LOCS+self.NUMBER_OBJS
        finalSynState = 9

        # Populations

        # Outputs
        self.pop_outputs = self.createPop(numOuts, label='pop_outputs')
        #self.pop_locations = createPop(NUMBER_LOCS, label='pop_locations')
        #self.pop_objects = createPop(, label='pop_object')

        # Gates
        self.gate_outputs = self.createPop(numOuts, label='gate_outputs')
        #self.gate_subjects = createPop(NUMBER_PEOPLE, label='gate_subject')
        #self.gate_locations = createPop(NUMBER_LOCS, label='gate_locations')
        #self.gate_objects = createPop(NUMBER_OBJS, label='gate_object')
        
        #weight_to_spike = 2.0
        if self.simulator_name == 'spiNNaker':
            weight_to_spike = 10.0
        elif self.simulator_name == 'nest':
            weight_to_spike = 10.0

        weight_to_gate = weight_to_spike * 0.05
        weight_to_control = weight_to_spike * 0.5
        weight_to_inhibit = weight_to_spike * 0.05 # 1 # 2 # 5
        inhDelay=5
        # max_delay = 100.0

        # sem to Gating: 30*5 connections
        connectors = []
        for semNum in range (0, numOuts):
            for fromOff in range (0,5):
                fromNeuron = (self.NUMBER_SYNSTATES + semNum)*5 + fromOff
                connectors=connectors+[(fromNeuron,semNum,weight_to_spike,DELAY)]
        #print connectors
        self.peterProjection(self.StatesCells, self.pop_outputs, connectors,'excitatory')
        
        # control: 5*30 connections
        connectors = []
        for fromOff in range (0,5):
            for semNum in range (0, numOuts):
                fromNeuron = finalSynState*5 + fromOff
                connectors=connectors+[(fromNeuron,semNum,weight_to_control,DELAY)]
        self.peterProjection(self.StatesCells, self.gate_outputs, connectors,'excitatory')

        # Gates: 30 connections
        connectors = []
        for semNum in range (0, numOuts):
            connectors=connectors+[(semNum,semNum,weight_to_gate,DELAY)]
        self.peterProjection(self.gate_outputs, self.pop_outputs, connectors,'excitatory')

        # Global Inhibition: 5 * (words+synStates+semStates)*5 connections
        # Also to self, and outputs and gates?
        for fromOff in range (0,5):
            fromNeuron = finalSynState*5 + fromOff
            # words
            connectors = []
            for toNeuron in range (0, self.NUMBER_WORDS*5):
                connectors=connectors+[(fromNeuron,toNeuron,weight_to_inhibit,inhDelay)]
            self.peterProjection(self.StatesCells, self.WordsCells, connectors,'inhibitory')
            # synStates and semStates
            connectors = []
            for toNeuron in range (0, self.NUMBER_STATES*5):
                connectors=connectors+[(fromNeuron,toNeuron,weight_to_inhibit,inhDelay)]
            self.peterProjection(self.StatesCells, self.StatesCells, connectors,'inhibitory')
            # gating pops
            connectors = []
            for semNum in range (0, numOuts):
                connectors=connectors+[(fromNeuron,semNum,weight_to_inhibit,inhDelay)]
            self.peterProjection(self.StatesCells, self.pop_outputs, connectors,'inhibitory')
            self.peterProjection(self.StatesCells, self.gate_outputs, connectors,'inhibitory')
