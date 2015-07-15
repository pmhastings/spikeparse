import pyNN.spiNNaker as p
import spynnaker_external_devices_plugin.pyNN as ExternalDevices
#import pylab as pl

input_reps = 5
delay_reps = 2

weight_to_spike = 2.0
weight_to_gate = weight_to_spike * 0.1
weight_to_control = weight_to_spike * 0.5
weight_to_inhibit = weight_to_spike * 5

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

def memory(subjects, locations, objects):

    pop_subject = p.Population(subjects, p.IF_curr_exp, cell_params_lif, label='pop_subject')
    pop_locations = p.Population(locations, p.IF_curr_exp, cell_params_lif, label='pop_locations')
    pop_object = p.Population(objects, p.IF_curr_exp, cell_params_lif, label='pop_object')

    query_pop_subject = p.Population(subjects, p.IF_curr_exp, cell_params_lif, label='query_pop_subject')
    query_pop_locations = p.Population(locations, p.IF_curr_exp, cell_params_lif, label='query_pop_locations')
    query_pop_object = p.Population(objects, p.IF_curr_exp, cell_params_lif, label='query_pop_object')

    who_gate = p.Population(subjects, p.IF_curr_exp, cell_params_lif, label='who_gate')
    where_gate = p.Population(locations, p.IF_curr_exp, cell_params_lif, label='where_gate')
    what_gate = p.Population(objects, p.IF_curr_exp, cell_params_lif, label='what_gate')

    #symmetric STDP rule
    # Plastic Connection between pre_pop and post_pop
    t_rule = p.SpikePairRule(tau_plus=0.5, tau_minus=0.5)
    w_rule = p.AdditiveWeightDependence(w_min=0.0, w_max=weight_to_spike, A_plus=weight_to_spike, A_minus=-weight_to_spike)
    stdp_model = p.STDPMechanism(
        timing_dependence = t_rule,
        weight_dependence = w_rule
    )

    s_d = p.SynapseDynamics(slow = stdp_model)

    statement_binding_sub_loc = p.Projection(pop_subject, pop_locations, p.AllToAllConnector(weights=0, delays=1), synapse_dynamics = s_d, target="excitatory")
    statement_binding_loc_sub = p.Projection(pop_locations, pop_subject, p.AllToAllConnector(weights=0, delays=1), synapse_dynamics = s_d, target="excitatory")
    statement_binding_sub_obj = p.Projection(pop_subject, pop_object, p.AllToAllConnector(weights=0, delays=1), synapse_dynamics = s_d, target="excitatory")
    statement_binding_obj_sub = p.Projection(pop_object, pop_subject, p.AllToAllConnector(weights=0, delays=1), synapse_dynamics = s_d, target="excitatory")
    statement_binding_obj_loc = p.Projection(pop_object, pop_locations, p.AllToAllConnector(weights=0, delays=1), synapse_dynamics = s_d, target="excitatory")
    statement_binding_loc_obj = p.Projection(pop_locations, pop_object, p.AllToAllConnector(weights=0, delays=1), synapse_dynamics = s_d, target="excitatory")

    query_subject = p.Projection(query_pop_subject, pop_subject, p.OneToOneConnector(weights=weight_to_spike, delays=1))
    query_locations = p.Projection(query_pop_locations, pop_locations, p.OneToOneConnector(weights=weight_to_spike, delays=1))
    query_object = p.Projection(query_pop_object, pop_object, p.OneToOneConnector(weights=weight_to_spike, delays=1))

    input_subjects = p.Population(subjects, p.IF_curr_exp, cell_params_lif, label='input_subjects')
    input_locations = p.Population(locations, p.IF_curr_exp, cell_params_lif, label='input_locations')
    input_objects = p.Population(objects, p.IF_curr_exp, cell_params_lif, label='input_objects')

    network_stabilizer = p.Population(1, p.IF_curr_exp, cell_params_lif, label='network_stabilizer')

    stabilize_subjects = p.Projection(network_stabilizer, pop_subject, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target = "inhibitory")
    stabilize_locations = p.Projection(network_stabilizer, pop_locations, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target = "inhibitory")
    stabilize_objects = p.Projection(network_stabilizer, pop_object, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target = "inhibitory")

    list_connector = [[i, i+1, weight_to_spike, delay_reps] for i in xrange (input_reps-1)]

    input_pop_subject = list()
    input_pop_subject_int_conn = list()
    input_subject_conn = list()
    input_subject_injection = list()
    input_subject_inh_locations = list()
    input_subject_inh_conn = list()
    for i in xrange (subjects):
        input_pop_subject.append( p.Population(input_reps, p.IF_curr_exp, cell_params_lif, label='pop_subject_input_{0:d}'.format(i)) )
        input_pop_subject_int_conn.append( p.Projection(input_pop_subject[i], input_pop_subject[i], p.FromListConnector(list_connector)) )
        list_connector2 = list()
        for j in xrange (input_reps):
            list_connector2.append([j, i, 1.5*weight_to_spike, 1])
        print "Subjects {0:d}: {1:s}".format(i, list_connector2)
        input_subject_conn.append( p.Projection(input_pop_subject[i], pop_subject, p.FromListConnector(list_connector2)) )
        input_subject_injection.append( p.Projection(input_subjects, input_pop_subject[i], p.FromListConnector([[i, 0, weight_to_spike, 1]])) )
        input_subject_inh_locations = p.Projection(input_pop_subject[i], pop_locations, p.AllToAllConnector(weights = 0.5*weight_to_spike, delays = 1), target='inhibitory')
        input_subject_inh_objects = p.Projection(input_pop_subject[i], pop_object, p.AllToAllConnector(weights = 0.5*weight_to_spike, delays = 1), target='inhibitory')
        input_subject_inh_conn.append( p.Projection(input_pop_subject[i], network_stabilizer, p.FromListConnector([[input_reps-1, 0, weight_to_spike, 1]])) )

    input_pop_location = list()
    input_pop_location_int_conn = list()
    input_location_conn = list()
    input_location_injection = list()
    input_location_inh_conn = list()
    for i in xrange (locations):
        input_pop_location.append( p.Population(input_reps, p.IF_curr_exp, cell_params_lif, label='pop_location_input_{0:d}'.format(i)) )
        input_pop_location_int_conn.append( p.Projection(input_pop_location[i], input_pop_location[i], p.FromListConnector(list_connector)) )
        list_connector2 = list()
        for j in xrange (input_reps):
            list_connector2.append([j, i, 1.5*weight_to_spike, 1])
        print "Locations {0:d}: {1:s}".format(i, list_connector2)
        input_location_conn.append( p.Projection(input_pop_location[i], pop_locations, p.FromListConnector(list_connector2)) )
        input_location_injection.append( p.Projection(input_locations, input_pop_location[i], p.FromListConnector([[i, 0, weight_to_spike, 1]])) )
        input_location_inh_subjects = p.Projection(input_pop_location[i], pop_subject, p.AllToAllConnector(weights = 0.5*weight_to_spike, delays = 1), target='inhibitory')
        input_location_inh_objects = p.Projection(input_pop_location[i], pop_object, p.AllToAllConnector(weights = 0.5*weight_to_spike, delays = 1), target='inhibitory')
        input_location_inh_conn.append( p.Projection(input_pop_location[i], network_stabilizer, p.FromListConnector([[input_reps-1, 0, weight_to_spike, 1]])) )

    input_pop_object = list()
    input_pop_object_int_conn = list()
    input_object_conn = list()
    input_object_injection = list()
    input_object_inh_conn = list()
    for i in xrange (objects):
        input_pop_object.append( p.Population(input_reps, p.IF_curr_exp, cell_params_lif, label='pop_object_input_{0:d}'.format(i)) )
        input_pop_object_int_conn.append( p.Projection(input_pop_object[i], input_pop_object[i], p.FromListConnector(list_connector)) )
        list_connector2 = list()
        for j in xrange (input_reps):
            list_connector2.append([j, i, 1.5*weight_to_spike, 1])
        #print "Objects {0:d}: {1:s}".format(i, list_connector2)
        input_object_conn.append( p.Projection(input_pop_object[i], pop_object, p.FromListConnector(list_connector2)) )
        input_object_injection.append( p.Projection(input_objects, input_pop_object[i], p.FromListConnector([[i, 0, weight_to_spike, 1]]), target="excitatory"))
        input_object_inh_subjects = p.Projection(input_pop_object[i], pop_subject, p.AllToAllConnector(weights = 0.5*weight_to_spike, delays = 1), target='inhibitory') 
        input_object_inh_locations = p.Projection(input_pop_object[i], pop_locations, p.AllToAllConnector(weights = 0.5*weight_to_spike, delays = 1), target='inhibitory') 
        input_object_inh_conn.append( p.Projection(input_pop_object[i], network_stabilizer, p.FromListConnector([[input_reps-1, 0, weight_to_spike, 1]])) )

    who = p.Population(1, p.IF_curr_exp, cell_params_lif, label='who')
    where = p.Population(1, p.IF_curr_exp, cell_params_lif, label='where')
    what = p.Population(1, p.IF_curr_exp, cell_params_lif, label='what')

    who_gating = p.Projection(pop_subject, who_gate, p.OneToOneConnector(weights = weight_to_gate, delays = 1))
    where_gating = p.Projection(pop_locations, where_gate, p.OneToOneConnector(weights = weight_to_gate, delays = 1))
    what_gating = p.Projection(pop_object, what_gate, p.OneToOneConnector(weights = weight_to_gate, delays = 1))

    who_control = p.Projection(who, who_gate, p.AllToAllConnector(weights = weight_to_control, delays = 1))
    where_control = p.Projection(where, where_gate, p.AllToAllConnector(weights = weight_to_control, delays = 1))
    what_control = p.Projection(what, what_gate, p.AllToAllConnector(weights = weight_to_control, delays = 1))

    #once the output is given, stabilize the network
    who_gate_inh_conn = list()
    where_gate_inh_conn = list()
    what_gate_inh_conn = list()

    who_self_inh = p.Projection(who_gate, who_gate, p.AllToAllConnector(weights=2*weight_to_inhibit, delays=1), target="inhibitory")
    where_self_inh = p.Projection(where_gate, where_gate, p.OneToOneConnector(weights=2*weight_to_inhibit, delays=1), target="inhibitory")
    what_self_inh = p.Projection(what_gate, what_gate, p.OneToOneConnector(weights=2*weight_to_inhibit, delays=1), target="inhibitory")

    who_gate_inh_conn.append( p.Projection(who_gate, pop_subject, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target="inhibitory") )
    #who_gate_inh_conn.append( p.Projection(who_gate, pop_locations, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target="inhibitory") )
    #who_gate_inh_conn.append( p.Projection(who_gate, pop_object, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target="inhibitory") )

    #where_gate_inh_conn.append( p.Projection(where_gate, pop_subject, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target="inhibitory") )
    where_gate_inh_conn.append( p.Projection(where_gate, pop_locations, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target="inhibitory") )
    #where_gate_inh_conn.append( p.Projection(where_gate, pop_object, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target="inhibitory") )

    #what_gate_inh_conn.append( p.Projection(what_gate, pop_subject, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target="inhibitory") )
    #what_gate_inh_conn.append( p.Projection(what_gate, pop_locations, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target="inhibitory") )
    what_gate_inh_conn.append( p.Projection(what_gate, pop_object, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target="inhibitory") )

    who_network_stabilize = p.Projection(who_gate, network_stabilizer, p.AllToAllConnector(weights = weight_to_spike, delays = 1), target="excitatory")
    where_network_stabilize = p.Projection(where_gate, network_stabilizer, p.AllToAllConnector(weights = weight_to_spike, delays = 1), target="excitatory")
    what_network_stabilize = p.Projection(what_gate, network_stabilizer, p.AllToAllConnector(weights = weight_to_spike, delays = 1), target="excitatory")


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
    p.Projection(external_conn_pop, input_subjects, p.FromListConnector(list_connector_subject), target='excitatory')
    p.Projection(external_conn_pop, input_locations, p.FromListConnector(list_connector_location), target='excitatory')
    p.Projection(external_conn_pop, input_objects, p.FromListConnector(list_connector_object), target='excitatory')
    p.Projection(external_conn_pop, query_pop_subject, p.FromListConnector(list_connector_query_subject), target='excitatory')
    p.Projection(external_conn_pop, query_pop_locations, p.FromListConnector(list_connector_query_location), target='excitatory')
    p.Projection(external_conn_pop, query_pop_object, p.FromListConnector(list_connector_query_object), target='excitatory')
    p.Projection(external_conn_pop, who, p.FromListConnector(list_connector_query_who), target='excitatory')
    p.Projection(external_conn_pop, where, p.FromListConnector(list_connector_query_where), target='excitatory')
    p.Projection(external_conn_pop, what, p.FromListConnector(list_connector_query_what), target='excitatory')

    ExternalDevices.activate_live_output_for(who_gate)
    ExternalDevices.activate_live_output_for(where_gate)
    ExternalDevices.activate_live_output_for(what_gate)

    input_populations = {
        'input_subjects': input_subjects,
        'input_locations': input_locations,
        'input_objects': input_objects,
        'query_pop_subject': query_pop_subject,
        'query_pop_locations': query_pop_locations,
        'query_pop_object': query_pop_object,
        'who': who,
        'where': where,
        'what': what
        }
    
    output_populations = {
        'who_gate': who_gate,
        'where_gate': where_gate,
        'what_gate': what_gate
        }
    
    projections = {
        'statement_binding_sub_loc': statement_binding_sub_loc,
        'statement_binding_loc_sub': statement_binding_loc_sub,
        'statement_binding_sub_obj': statement_binding_sub_obj,
        'statement_binding_obj_sub': statement_binding_obj_sub,
        'statement_binding_obj_loc': statement_binding_obj_loc,
        'statement_binding_loc_obj': statement_binding_loc_obj
        }
    
    state_populations = {
        'pop_subject': pop_subject,
        'pop_locations': pop_locations,
        'pop_object': pop_object
        }
    
    who.record()
    where.record()
    what.record()
    
    who_gate.record()
    where_gate.record()
    what_gate.record()
    
    pop_subject.record()
    pop_locations.record()
    pop_object.record()
    
    return [input_populations, state_populations, output_populations, projections]

    '''
    #simulate a sentence to link first subject and first location
    #and then ask for the location of the first subject
    injection1a = {'spike_times' : [[50]]}

    injection1b = {'spike_times' : [[250]]}

    injection1c = {'spike_times' : [[450]]}

    injection2 = {'spike_times' : [[800]]}

    injection3 = {'spike_times' : [[806]]}

    ss1a = p.Population(1, p.SpikeSourceArray, injection1a)

    ss1b = p.Population(1, p.SpikeSourceArray, injection1b)

    ss1c = p.Population(1, p.SpikeSourceArray, injection1c)

    ss2 = p.Population(1, p.SpikeSourceArray, injection2)

    ss3 = p.Population(1, p.SpikeSourceArray, injection3)

    #john has a ball
    ss1a_inj_1 = p.Projection(ss1a, input_subjects, p.FromListConnector([[0, 0, weight_to_spike, 1]]))
    ss1a_inj_2 = p.Projection(ss1a, input_objects, p.FromListConnector([[0, 0, weight_to_spike, 1]]))

    #john is in the kitchen
    ss1b_inj_1 = p.Projection(ss1b, input_subjects, p.FromListConnector([[0, 0, weight_to_spike, 1]]))
    ss1b_inj_1 = p.Projection(ss1b, input_locations, p.FromListConnector([[0, 0, weight_to_spike, 1]]))

    #sergio is in the kitchen
    ss1c_inj_1 = p.Projection(ss1c, input_subjects, p.FromListConnector([[0, 1, weight_to_spike, 1]]))
    ss1c_inj_1 = p.Projection(ss1c, input_locations, p.FromListConnector([[0, 0, weight_to_spike, 1]]))

    #who has the ball
    #ss2_inj = p.Projection(ss2, query_pop_object, p.FromListConnector([[0, 0, weight_to_spike, 1]]))

    #who is in the kitchen
    ss2_inj = p.Projection(ss2, query_pop_locations, p.FromListConnector([[0, 0, weight_to_spike, 1]]))

    ss3_inj = p.Projection(ss3, who, p.FromListConnector([[0, 0, weight_to_spike, 1]]))

    '''


    '''
    #recording section
    for i in xrange(subjects):
        input_pop_subject[i].record()

    for i in xrange(locations):
        input_pop_location[i].record()

    for i in xrange(objects):
        input_pop_object[i].record()

    pop_subject.record()
    pop_locations.record()
    pop_object.record()

    pop_subject.record_v()
    pop_subject.record_gsyn()

    pop_locations.record_v()
    pop_locations.record_gsyn()

    network_stabilizer.record()

    who.record()
    where.record()
    what.record()
    
    who_gate.record()
    where_gate.record()
    what_gate.record()
    
    where_gate.record_v()
    where_gate.record_gsyn()

    query_pop_locations.record()
    query_pop_object.record()
    query_pop_subject.record()
    '''

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