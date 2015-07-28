import pyNN.nest as p
from nest import Connect
#import pyNN.spiNNaker as p
#import spynnaker_external_devices_plugin.pyNN as ExternalDevices
import pylab as pl

input_reps = 5
delay_reps = 2

subjects = 10
locations = 10
objects = 10

weight_to_spike = 2.0
weight_to_gate = weight_to_spike * 0.06
weight_to_control = weight_to_spike * 0.5
weight_to_inhibit = weight_to_spike * 5
max_delay = 100.0

p.setup(timestep=1.0, min_delay = 1.0, max_delay = max_delay)

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

external_conns_params = {
    'virtual_key':      0x70800,
    'port':             12345}

pop_subject = p.Population(subjects, p.IF_cond_exp, cell_params_lif, label='pop_subject')
pop_locations = p.Population(locations, p.IF_cond_exp, cell_params_lif, label='pop_locations')
pop_object = p.Population(objects, p.IF_cond_exp, cell_params_lif, label='pop_object')

query_pop_subject = p.Population(subjects, p.IF_cond_exp, cell_params_lif, label='query_pop_subject')
query_pop_locations = p.Population(locations, p.IF_cond_exp, cell_params_lif, label='query_pop_locations')
query_pop_object = p.Population(objects, p.IF_cond_exp, cell_params_lif, label='query_pop_object')

who_gate = p.Population(subjects, p.IF_cond_exp, cell_params_lif, label='who_gate')
where_gate = p.Population(locations, p.IF_cond_exp, cell_params_lif, label='where_gate')
what_gate = p.Population(objects, p.IF_cond_exp, cell_params_lif, label='what_gate')

#symmetric STDP rule
# Plastic Connection between pre_pop and post_pop
# PH: the A_plus, minus params seem to have moved from Additive.. to SpikePair...
t_rule = p.SpikePairRule(tau_plus=0.5, tau_minus=0.5, A_plus=weight_to_spike, A_minus=-weight_to_spike)
w_rule = p.AdditiveWeightDependence(w_min=0.0, w_max=weight_to_spike) # , A_plus=weight_to_spike, A_minus=-weight_to_spike)
stdp_model = p.STDPMechanism(
    timing_dependence = t_rule,
    weight_dependence = w_rule,
    weight=0, delay=1
)

# s_d = p.SynapseDynamics(slow = stdp_model)

# would have to check type of connector.  If it's AllToAllConnector, then make the list
# def peterProjection(preNeurons,postNeurons, connector, synapse_type = None, receptor_type="excitatory"):
#     if simulator_name == 'spiNNaker':
#         Projection(preNeurons, postNeurons, connector, synapse_type = synapse_type, receptor_type=receptor_type)
#     elif simulator_name == 'nest':
#         # Projection(preNeurons, postNeurons, connectorList)
#         if isinstance(connector,p.AllToAllConnector):
#             Connect(preNeurons,postNeurons, 'all_to_all', ) # need syn_spec
#         elif isinstance(connector,p.OneToOneConnector):
#             Connect(preNeurons,postNeurons, 'one_to_one', ) # need syn_spec
#         elif isinstance(connector,p.FromListConnector):
#             for connection in connector.conn_list:
#                 Connect(preNeurons[connection[0]],postNeurons[connection[1]],
#                         {'weight':connection[2]}, receptor_type=receptor_type)
#         else:
#             print 'bad connection type for peterProjection'
#     else:
#         print 'bad simulator for peterProjection'

        

statement_binding_sub_loc = p.Projection(pop_subject, pop_locations, p.AllToAllConnector(), synapse_type = stdp_model, receptor_type="excitatory")
statement_binding_loc_sub = p.Projection(pop_locations, pop_subject, p.AllToAllConnector(), synapse_type = stdp_model, receptor_type="excitatory")
statement_binding_sub_obj = p.Projection(pop_subject, pop_object, p.AllToAllConnector(), synapse_type = stdp_model, receptor_type="excitatory")
statement_binding_obj_sub = p.Projection(pop_object, pop_subject, p.AllToAllConnector(), synapse_type = stdp_model, receptor_type="excitatory")
statement_binding_obj_loc = p.Projection(pop_object, pop_locations, p.AllToAllConnector(), synapse_type = stdp_model, receptor_type="excitatory")
statement_binding_loc_obj = p.Projection(pop_locations, pop_object, p.AllToAllConnector(), synapse_type = stdp_model, receptor_type="excitatory")

query_subject = p.Projection(query_pop_subject, pop_subject, p.OneToOneConnector(), synapse_type=p.StaticSynapse(weight=weight_to_spike, delay=1))
query_locations = p.Projection(query_pop_locations, pop_locations, p.OneToOneConnector(), synapse_type=p.StaticSynapse(weight=weight_to_spike, delay=1))
query_object = p.Projection(query_pop_object, pop_object, p.OneToOneConnector(), synapse_type=p.StaticSynapse(weight=weight_to_spike, delay=1))

input_subjects = p.Population(subjects, p.IF_cond_exp, cell_params_lif, label='input_subjects')
input_locations = p.Population(locations, p.IF_cond_exp, cell_params_lif, label='input_locations')
input_objects = p.Population(objects, p.IF_cond_exp, cell_params_lif, label='input_objects')

network_stabilizer = p.Population(1, p.IF_cond_exp, cell_params_lif, label='network_stabilizer')

stabilize_subjects = p.Projection(network_stabilizer, pop_subject, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -weight_to_inhibit, delay = 1), receptor_type = "inhibitory")
stabilize_locations = p.Projection(network_stabilizer, pop_locations, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -weight_to_inhibit, delay = 1), receptor_type = "inhibitory")
stabilize_objects = p.Projection(network_stabilizer, pop_object, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -weight_to_inhibit, delay = 1), receptor_type = "inhibitory")

list_connector = [[i, i+1, weight_to_spike, delay_reps] for i in xrange (input_reps-1)]

input_pop_subject = list()
input_pop_subject_int_conn = list()
input_subject_conn = list()
input_subject_injection = list()
input_subject_inh_locations = list()
input_subject_inh_conn = list()
for i in xrange (subjects):
    input_pop_subject.append( p.Population(input_reps, p.IF_cond_exp, cell_params_lif, label='pop_subject_input_{0:d}'.format(i)) )
    input_pop_subject_int_conn.append( p.Projection(input_pop_subject[i], input_pop_subject[i], p.FromListConnector(list_connector)) )
    list_connector2 = list()
    for j in xrange (input_reps):
        list_connector2.append([j, i, 1.5*weight_to_spike, 1])
    print "Subjects {0:d}: {1:s}".format(i, list_connector2)
    input_subject_conn.append( p.Projection(input_pop_subject[i], pop_subject, p.FromListConnector(list_connector2)) )
    input_subject_injection.append( p.Projection(input_subjects, input_pop_subject[i], p.FromListConnector([[i, 0, weight_to_spike, 1]])) )
    input_subject_inh_locations = p.Projection(input_pop_subject[i], pop_locations, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -0.5*weight_to_spike, delay = 1), receptor_type='inhibitory')
    input_subject_inh_objects = p.Projection(input_pop_subject[i], pop_object, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -0.5*weight_to_spike, delay = 1), receptor_type='inhibitory')
    input_subject_inh_conn.append( p.Projection(input_pop_subject[i], network_stabilizer, p.FromListConnector([[input_reps-1, 0, weight_to_spike, 1]])) )

input_pop_location = list()
input_pop_location_int_conn = list()
input_location_conn = list()
input_location_injection = list()
input_location_inh_conn = list()
for i in xrange (locations):
    input_pop_location.append( p.Population(input_reps, p.IF_cond_exp, cell_params_lif, label='pop_location_input_{0:d}'.format(i)) )
    input_pop_location_int_conn.append( p.Projection(input_pop_location[i], input_pop_location[i], p.FromListConnector(list_connector)) )
    list_connector2 = list()
    for j in xrange (input_reps):
        list_connector2.append([j, i, 1.5*weight_to_spike, 1])
    print "Locations {0:d}: {1:s}".format(i, list_connector2)
    input_location_conn.append( p.Projection(input_pop_location[i], pop_locations, p.FromListConnector(list_connector2)) )
    print "loc injection"
    input_location_injection.append( p.Projection(input_locations, input_pop_location[i], p.FromListConnector([[i, 0, weight_to_spike, 1]])) )
    print "loc inhib subj"
    input_location_inh_subjects = p.Projection(input_pop_location[i], pop_subject, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -0.5*weight_to_spike, delay = 1), receptor_type='inhibitory')
    print "loc inhib obj"
    input_location_inh_objects = p.Projection(input_pop_location[i], pop_object, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -0.5*weight_to_spike, delay = 1), receptor_type='inhibitory')
    print "stabilizer"
    input_location_inh_conn.append( p.Projection(input_pop_location[i], network_stabilizer, p.FromListConnector([[input_reps-1, 0, weight_to_spike, 1]])) )

# print "after"
input_pop_object = list()
input_pop_object_int_conn = list()
input_object_conn = list()
input_object_injection = list()
input_object_inh_conn = list()
## print "xrange"
for i in xrange (objects):
    input_pop_object.append( p.Population(input_reps, p.IF_cond_exp, cell_params_lif, label='pop_object_input_{0:d}'.format(i)) )
    #print "p2"
    input_pop_object_int_conn.append( p.Projection(input_pop_object[i], input_pop_object[i], p.FromListConnector(list_connector)) )
    list_connector2 = list()
    for j in xrange (input_reps):
        list_connector2.append([j, i, 1.5*weight_to_spike, 1])
    #print "Objects {0:d}: {1:s}".format(i, list_connector2)
    #print "p3"
    input_object_conn.append( p.Projection(input_pop_object[i], pop_object, p.FromListConnector(list_connector2)) )
    #print "p4"
    input_object_injection.append( p.Projection(input_objects, input_pop_object[i], p.FromListConnector([[i, 0, weight_to_spike, 1]]), receptor_type="excitatory"))
    #print "p5"
    input_object_inh_subjects = p.Projection(input_pop_object[i], pop_subject, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -0.5*weight_to_spike, delay = 1), receptor_type='inhibitory') 
    #print "p6"
    input_object_inh_locations = p.Projection(input_pop_object[i], pop_locations, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -0.5*weight_to_spike, delay = 1), receptor_type='inhibitory') 
    # print "p7"
    input_object_inh_conn.append( p.Projection(input_pop_object[i], network_stabilizer, p.FromListConnector([[input_reps-1, 0, weight_to_spike, 1]])) )

who = p.Population(1, p.IF_cond_exp, cell_params_lif, label='who')
where = p.Population(1, p.IF_cond_exp, cell_params_lif, label='where')
what = p.Population(1, p.IF_cond_exp, cell_params_lif, label='what')

# print "gating Connectors"
who_gating = p.Projection(pop_subject, who_gate, p.OneToOneConnector(), synapse_type=p.StaticSynapse(weight = weight_to_gate, delay = 1))
where_gating = p.Projection(pop_locations, where_gate, p.OneToOneConnector(), synapse_type=p.StaticSynapse(weight = weight_to_gate, delay = 1))
what_gating = p.Projection(pop_object, what_gate, p.OneToOneConnector(), synapse_type=p.StaticSynapse(weight = weight_to_gate, delay = 1))

# print "control Connectors"
who_control = p.Projection(who, who_gate, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = weight_to_control, delay = 1))
where_control = p.Projection(where, where_gate, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = weight_to_control, delay = 1))
what_control = p.Projection(what, what_gate, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = weight_to_control, delay = 1))

#once the output is given, stabilize the network
who_gate_inh_conn = list()
where_gate_inh_conn = list()
what_gate_inh_conn = list()

# print "self inhibit"
who_self_inh = p.Projection(who_gate, who_gate, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight=-2*weight_to_inhibit, delay=1), receptor_type="inhibitory")
where_self_inh = p.Projection(where_gate, where_gate, p.OneToOneConnector(), synapse_type=p.StaticSynapse(weight=-2*weight_to_inhibit, delay=1), receptor_type="inhibitory")
what_self_inh = p.Projection(what_gate, what_gate, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight=-2*weight_to_inhibit, delay=1), receptor_type="inhibitory")

# print "gate inhibit"
who_gate_inh_conn.append( p.Projection(who_gate, pop_subject, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -weight_to_inhibit, delay = 1), receptor_type="inhibitory") )
who_gate_inh_conn.append( p.Projection(who_gate, pop_locations, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -weight_to_inhibit, delay = 1), receptor_type="inhibitory") )
who_gate_inh_conn.append( p.Projection(who_gate, pop_object, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -weight_to_inhibit, delay = 1), receptor_type="inhibitory") )

where_gate_inh_conn.append( p.Projection(where_gate, pop_subject, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -weight_to_inhibit, delay = 1), receptor_type="inhibitory") )
where_gate_inh_conn.append( p.Projection(where_gate, pop_locations, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -weight_to_inhibit, delay = 1), receptor_type="inhibitory") )
where_gate_inh_conn.append( p.Projection(where_gate, pop_object, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -weight_to_inhibit, delay = 1), receptor_type="inhibitory") )

what_gate_inh_conn.append( p.Projection(what_gate, pop_subject, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -weight_to_inhibit, delay = 1), receptor_type="inhibitory") )
what_gate_inh_conn.append( p.Projection(what_gate, pop_locations, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -weight_to_inhibit, delay = 1), receptor_type="inhibitory") )
what_gate_inh_conn.append( p.Projection(what_gate, pop_object, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = -weight_to_inhibit, delay = 1), receptor_type="inhibitory") )

# print "gate to stabilizer"
who_network_stabilize = p.Projection(who_gate, network_stabilizer, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = weight_to_spike, delay = 1), receptor_type="excitatory")
where_network_stabilize = p.Projection(where_gate, network_stabilizer, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = weight_to_spike, delay = 1), receptor_type="excitatory")
what_network_stabilize = p.Projection(what_gate, network_stabilizer, p.AllToAllConnector(), synapse_type=p.StaticSynapse(weight = weight_to_spike, delay = 1), receptor_type="excitatory")


'''
#external input population

total_input_neurons = 2 * (subjects + locations + objects) + 3
external_conn_pop = p.Population(total_input_neurons, ExternalDevices.SpikeInjector, external_conns_params, 'external_conn_pop')

current_input_neuron = 0
list_connector_subject = [[current_input_neuron + i, i, weight_to_spike, 1] for i in xrange(subjects)]
current_input_neuron += subjects
list_connector_location = [[current_input_neuron + i, i, weight_to_spike, 1] for i in xrange(locations)]
current_input_neuron += locations
list_connector_object = [[current_input_neuron + i, i, weight_to_spike, 1] for i in xrange(objects)]
current_input_neuron += objects
list_connector_query_subject = [[current_input_neuron + i, i, weight_to_spike, 1] for i in xrange(subjects)]
current_input_neuron += subjects
list_connector_query_location = [[current_input_neuron + i, i, weight_to_spike, 1] for i in xrange(locations)]
current_input_neuron += locations
list_connector_query_object = [[current_input_neuron + i, i, weight_to_spike, 1] for i in xrange(objects)]
current_input_neuron += objects
list_connector_query_who = [[current_input_neuron, 0, weight_to_spike, 6]]
current_input_neuron += 1
list_connector_query_where = [[current_input_neuron, 0, weight_to_spike, 6]]
current_input_neuron += 1
list_connector_query_what = [[current_input_neuron, 0, weight_to_spike, 6]]

external_injection_proj = list()
p.Projection(external_conn_pop, input_subjects, p.FromListConnector(list_connector_subject), receptor_type='excitatory')
p.Projection(external_conn_pop, input_locations, p.FromListConnector(list_connector_location), receptor_type='excitatory')
p.Projection(external_conn_pop, input_objects, p.FromListConnector(list_connector_object), receptor_type='excitatory')
p.Projection(external_conn_pop, query_pop_subject, p.FromListConnector(list_connector_query_subject), receptor_type='excitatory')
p.Projection(external_conn_pop, query_pop_locations, p.FromListConnector(list_connector_query_location), receptor_type='excitatory')
p.Projection(external_conn_pop, query_pop_object, p.FromListConnector(list_connector_query_object), receptor_type='excitatory')
p.Projection(external_conn_pop, who, p.FromListConnector(list_connector_query_who), receptor_type='excitatory')
p.Projection(external_conn_pop, where, p.FromListConnector(list_connector_query_where), receptor_type='excitatory')
p.Projection(external_conn_pop, what, p.FromListConnector(list_connector_query_what), receptor_type='excitatory')

ExternalDevices.activate_live_output_for(who_gate)
ExternalDevices.activate_live_output_for(where_gate)
ExternalDevices.activate_live_output_for(what_gate)
'''


#simulate a sentence to link first subject and first location
#and then ask for the location of the first subject
injection1a = {'spike_times' : [50]}

injection1b = {'spike_times' : [250]}

injection1c = {'spike_times' : [450]}

injection2 = {'spike_times' : [800]}

injection3 = {'spike_times' : [806]}

ss1a = p.Population(1, p.SpikeSourceArray, injection1a)

ss1b = p.Population(1, p.SpikeSourceArray, injection1b)

ss1c = p.Population(1, p.SpikeSourceArray, injection1c)

ss2 = p.Population(1, p.SpikeSourceArray, injection2)

ss3 = p.Population(1, p.SpikeSourceArray, injection3)

#john has a ball
# print "john has a ball"
# ss1a_inj_1 = p.Projection(ss1a, input_subjects, p.FromListConnector([[0, 0, weight_to_spike, 1]]))
# print "jhab2"
# ss1a_inj_2 = p.Projection(ss1a, input_objects, p.FromListConnector([[0, 0, weight_to_spike, 1]]))

# print "john has a ball"
ss1a_inj_1 = p.Projection(ss1a, input_subjects, p.FromListConnector([[0, 0, weight_to_spike, 1]]),
                          synapse_type=p.StaticSynapse())
# print "jhab2"
ss1a_inj_2 = p.Projection(ss1a, input_objects, p.FromListConnector([[0, 0, weight_to_spike, 1]]),
                          synapse_type=p.StaticSynapse())

#john is in the kitchen
# print "john is in the kitchen"
ss1b_inj_1 = p.Projection(ss1b, input_subjects, p.FromListConnector([[0, 0, weight_to_spike, 1]]))
ss1b_inj_1 = p.Projection(ss1b, input_locations, p.FromListConnector([[0, 0, weight_to_spike, 1]]))

#sergio is in the kitchen
# print "sergio is in the kitchen"
ss1c_inj_1 = p.Projection(ss1c, input_subjects, p.FromListConnector([[0, 1, weight_to_spike, 1]]))
ss1c_inj_1 = p.Projection(ss1c, input_locations, p.FromListConnector([[0, 0, weight_to_spike, 1]]))

#who has the ball
#ss2_inj = p.Projection(ss2, query_pop_object, p.FromListConnector([[0, 0, weight_to_spike, 1]]))

#who is in the kitchen
# print "who is in the kitchen"
ss2_inj = p.Projection(ss2, query_pop_locations, p.FromListConnector([[0, 0, weight_to_spike, 1]]))

# print "ss3"
ss3_inj = p.Projection(ss3, who, p.FromListConnector([[0, 0, weight_to_spike, 1]]))

print "record"
who_gate.record('v')
where_gate.record('v')
what_gate.record('v')

'''
#recording section

input_subjects.record()
input_locations.record()
input_objects.record()

#for i in xrange(subjects):
#    input_pop_subject[i].record()
#
#for i in xrange(locations):
#    input_pop_location[i].record()
#
#for i in xrange(objects):
#    input_pop_object[i].record()

pop_subject.record()
pop_locations.record()
pop_object.record()

#pop_subject.record_v()
#pop_subject.record_gsyn()

#pop_locations.record_v()
#pop_locations.record_gsyn()

network_stabilizer.record()

who.record()
where.record()
what.record()

who_gate.record_v()

#where_gate.record_v()
#where_gate.record_gsyn()

query_pop_locations.record()
query_pop_object.record()
query_pop_subject.record()
'''

p.run(1 * 1000)
#p.run(2.5 * 60 * 1000)

who_gate_spikes = who_gate.getSpikes(compatible_output=True)
where_gate_spikes = where_gate.getSpikes(compatible_output=True)
what_gate_spikes = what_gate.getSpikes(compatible_output=True)

'''
pop_subject_spikes = pop_subject.getSpikes(compatible_output=True)
pop_locations_spikes = pop_locations.getSpikes(compatible_output=True)
pop_object_spikes = pop_object.getSpikes(compatible_output=True)

who_gate_v = who_gate.get_v()

thefile = open('v_file', 'w')
for item in who_gate_v:
    if item[0] == 0:
        thefile.write("%s\n" % item)
thefile.close()

#print where_gate_v[8100:8600]

#print "pop subjects:"
#print pop_subject_spikes
#
#print "pop locations:"
#print pop_locations_spikes
#
#print "pop object:"
#print pop_object_spikes
#
'''

print "Who:"
print who_gate_spikes

print "Where:"
print where_gate_spikes

print "What:"
print what_gate_spikes

'''
#retrieving section
pop_subject_spikes = pop_subject.getSpikes(compatible_output=True)
pop_subject_v = pop_subject.get_v()
pop_subject_i = pop_subject.get_gsyn()
pop_locations_spikes = pop_locations.getSpikes(compatible_output=True)
pop_object_spikes = pop_object.getSpikes(compatible_output=True)
who_spikes = who.getSpikes(compatible_output=True)
where_spikes = where.getSpikes(compatible_output=True)
what_spikes = what.getSpikes(compatible_output=True)

who_gate_spikes = who_gate.getSpikes(compatible_output=True)
where_gate_spikes = where_gate.getSpikes(compatible_output=True)
what_gate_spikes = what_gate.getSpikes(compatible_output=True)
where_gate_v = where_gate.get_v()
where_gate_gsyn = where_gate.get_gsyn()
query_pop_locations_spikes = query_pop_locations.getSpikes(compatible_output=True)
query_pop_object_spikes = query_pop_object.getSpikes(compatible_output=True)
query_pop_subject_spikes = query_pop_subject.getSpikes(compatible_output=True)

network_stabilizer_spikes = network_stabilizer.getSpikes(compatible_output=True)

input_pop_subject_spikes = list()
input_pop_subject_spikes.append(input_pop_subject[0].getSpikes(compatible_output=True))
input_pop_subject_spikes.append(input_pop_subject[1].getSpikes(compatible_output=True))
input_pop_subject_spikes.append(input_pop_subject[2].getSpikes(compatible_output=True))
input_pop_subject_spikes.append(input_pop_subject[3].getSpikes(compatible_output=True))
input_pop_subject_spikes.append(input_pop_subject[4].getSpikes(compatible_output=True))

input_pop_location_spikes = list()
input_pop_location_spikes.append(input_pop_location[0].getSpikes(compatible_output=True))
input_pop_location_spikes.append(input_pop_location[1].getSpikes(compatible_output=True))
input_pop_location_spikes.append(input_pop_location[2].getSpikes(compatible_output=True))
input_pop_location_spikes.append(input_pop_location[3].getSpikes(compatible_output=True))
input_pop_location_spikes.append(input_pop_location[4].getSpikes(compatible_output=True))

input_pop_object_spikes = list()
input_pop_object_spikes.append(input_pop_object[0].getSpikes(compatible_output=True))
input_pop_object_spikes.append(input_pop_object[1].getSpikes(compatible_output=True))
input_pop_object_spikes.append(input_pop_object[2].getSpikes(compatible_output=True))
input_pop_object_spikes.append(input_pop_object[3].getSpikes(compatible_output=True))
input_pop_object_spikes.append(input_pop_object[4].getSpikes(compatible_output=True))

print pop_subject_i[800:820]
print pop_subject_i[1800:1820]

w_sub_loc = statement_binding_sub_loc.getWeights()
w_loc_sub = statement_binding_loc_sub.getWeights()
w_sub_obj = statement_binding_sub_obj.getWeights()
w_obj_sub = statement_binding_obj_sub.getWeights()
w_obj_loc = statement_binding_obj_loc.getWeights()
w_loc_obj = statement_binding_loc_obj.getWeights()
'''

'''
a = p.get_spynnaker.func_globals
b = a['_spinnaker']
for i in range(len(b.partitionable_graph.edges)):
    if b.partitionable_graph.edges[i].post_vertex.label=='pop_subject':
        c=b.partitionable_graph.edges[i] 
        d=c.synapse_list.get_rows()[0].synapse_types
        print i, c.pre_vertex.label, d




'''
