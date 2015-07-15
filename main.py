import pyNN.spiNNaker as p
import memory_for_parser as mem
import parse as parser

NUMBER_PEOPLE = 10
NUMBER_LOCS = 10
NUMBER_OBJS = 10

max_delay = 100.0

p.setup(timestep=1.0, min_delay = 1.0, max_delay = max_delay)

parser.parse_no_run('spiNNaker', "Daniel went to the bathroom. John went to the hallway. Where is John?")
[input_populations, state_populations, output_populations, projections] = mem.memory(NUMBER_PEOPLE, NUMBER_LOCS, NUMBER_OBJS)

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

weight_to_spike = mem.weight_to_spike
weight_to_gate = 0.5
weight_to_control = 0.5
weight_to_inhibit = mem.weight_to_inhibit

src_pop = parser.pop_outputs

dst_pop_subject = input_populations['input_subjects']
dst_pop_location = input_populations['input_locations']
dst_pop_objects = input_populations['input_objects']

dst_query_subject = input_populations['query_pop_subject']
dst_query_location = input_populations['query_pop_locations']
dst_query_object = input_populations['query_pop_object']

who = p.Population(1, p.IF_curr_exp, cell_params_lif, label='who')
where = p.Population(1, p.IF_curr_exp, cell_params_lif, label='where')
what = p.Population(1, p.IF_curr_exp, cell_params_lif, label='what')

who_statement_gate = p.Population(NUMBER_PEOPLE, p.IF_curr_exp, cell_params_lif, label='query_pop_subject')
where_statement_gate = p.Population(NUMBER_LOCS, p.IF_curr_exp, cell_params_lif, label='query_pop_locations')
what_statement_gate = p.Population(NUMBER_OBJS, p.IF_curr_exp, cell_params_lif, label='query_pop_object')

who_query_gate = p.Population(NUMBER_PEOPLE, p.IF_curr_exp, cell_params_lif, label='query_pop_subject')
where_query_gate = p.Population(NUMBER_LOCS, p.IF_curr_exp, cell_params_lif, label='query_pop_locations')
what_query_gate = p.Population(NUMBER_OBJS, p.IF_curr_exp, cell_params_lif, label='query_pop_object')

query_pop_subject = p.Population(NUMBER_PEOPLE, p.IF_curr_exp, cell_params_lif, label='query_pop_subject')
query_pop_locations = p.Population(NUMBER_LOCS, p.IF_curr_exp, cell_params_lif, label='query_pop_locations')
query_pop_object = p.Population(NUMBER_OBJS, p.IF_curr_exp, cell_params_lif, label='query_pop_object')

dst_who = input_populations['who']
dst_where = input_populations['where']
dst_what = input_populations['what']

statement_subject_proj_list = [[i*5, i, weight_to_spike, 5] for i in xrange(NUMBER_PEOPLE)]
statement_locations_proj_list = [[i*5 + (NUMBER_PEOPLE)*5, i, weight_to_spike, 5] for i in xrange(NUMBER_LOCS)]
statement_objects_proj_list = [[i*5 + (NUMBER_PEOPLE + NUMBER_LOCS)*5, i, weight_to_spike, 5] for i in xrange(NUMBER_OBJS)]
query_subject_proj_list = [[i*5, i, weight_to_gate, 5] for i in xrange(NUMBER_PEOPLE)]
query_locations_proj_list = [[i*5 + (NUMBER_PEOPLE*5), i, weight_to_gate, 5] for i in xrange(NUMBER_LOCS)]
query_objects_proj_list = [[i*5 + (NUMBER_PEOPLE + NUMBER_LOCS)*5, i, weight_to_gate, 5] for i in xrange(NUMBER_OBJS)]

subj_source_statement_proj = p.Projection(src_pop, who_statement_gate, p.FromListConnector(statement_subject_proj_list), target='excitatory')
subj_source_query_proj = p.Projection(src_pop, who_query_gate, p.FromListConnector(query_subject_proj_list), target='excitatory')
loc_source_statement_proj = p.Projection(src_pop, where_statement_gate, p.FromListConnector(statement_locations_proj_list), target='excitatory')
loc_source_query_proj = p.Projection(src_pop, where_query_gate, p.FromListConnector(query_locations_proj_list), target='excitatory')
obj_source_statement_proj = p.Projection(src_pop, what_statement_gate, p.FromListConnector(statement_objects_proj_list), target='excitatory')
obj_source_query_proj = p.Projection(src_pop, what_query_gate, p.FromListConnector(query_objects_proj_list), target='excitatory')

who_subject_statement_projection = p.Projection(who, who_statement_gate, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target='inhibitory')
who_subject_query_projection = p.Projection(who, who_query_gate, p.AllToAllConnector(weights = weight_to_control, delays = 1), target='excitatory')
who_location_statement_projection = p.Projection(who, where_statement_gate, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target='inhibitory')
who_location_query_projection = p.Projection(who, where_query_gate, p.AllToAllConnector(weights = weight_to_control, delays = 1), target='excitatory')
who_object_statement_projection = p.Projection(who, what_statement_gate, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target='inhibitory')
who_object_query_projection = p.Projection(who, what_query_gate, p.AllToAllConnector(weights = weight_to_control, delays = 1), target='excitatory')

where_subject_statement_projection = p.Projection(where, who_statement_gate, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target='inhibitory')
where_subject_query_projection = p.Projection(where, who_query_gate, p.AllToAllConnector(weights = weight_to_control, delays = 1), target='excitatory')
where_location_statement_projection = p.Projection(where, where_statement_gate, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target='inhibitory')
where_location_query_projection = p.Projection(where, where_query_gate, p.AllToAllConnector(weights = weight_to_control, delays = 1), target='excitatory')
where_object_statement_projection = p.Projection(where, what_statement_gate, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target='inhibitory')
where_object_query_projection = p.Projection(where, what_query_gate, p.AllToAllConnector(weights = weight_to_control, delays = 1), target='excitatory')

what_subject_statement_projection = p.Projection(what, who_statement_gate, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target='inhibitory')
what_subject_query_projection = p.Projection(what, who_query_gate, p.AllToAllConnector(weights = weight_to_control, delays = 1), target='excitatory')
what_location_statement_projection = p.Projection(what, where_statement_gate, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target='inhibitory')
what_location_query_projection = p.Projection(what, where_query_gate, p.AllToAllConnector(weights = weight_to_control, delays = 1), target='excitatory')
what_object_statement_projection = p.Projection(what, what_statement_gate, p.AllToAllConnector(weights = weight_to_inhibit, delays = 1), target='inhibitory')
what_object_query_projection = p.Projection(what, what_query_gate, p.AllToAllConnector(weights = weight_to_control, delays = 1), target='excitatory')

p.Projection(who_statement_gate, dst_pop_subject, p.OneToOneConnector(weights = weight_to_spike, delays = 1), target='excitatory')
p.Projection(where_statement_gate, dst_pop_location, p.OneToOneConnector(weights = weight_to_spike, delays = 1), target='excitatory')
p.Projection(what_statement_gate, dst_pop_objects, p.OneToOneConnector(weights = weight_to_spike, delays = 1), target='excitatory')
p.Projection(who_query_gate, dst_query_subject, p.OneToOneConnector(weights = weight_to_spike, delays = 1), target='excitatory')
p.Projection(where_query_gate, dst_query_location, p.OneToOneConnector(weights = weight_to_spike, delays = 1), target='excitatory')
p.Projection(what_query_gate, dst_query_object, p.OneToOneConnector(weights = weight_to_spike, delays = 1), target='excitatory')

p.Projection(who, dst_who, p.OneToOneConnector(weights = weight_to_spike, delays = 1), target='excitatory')
p.Projection(where, dst_where, p.OneToOneConnector(weights = weight_to_spike, delays = 1), target='excitatory')
p.Projection(what, dst_what, p.OneToOneConnector(weights = weight_to_spike, delays = 1), target='excitatory')

'''
injection1 = {'spike_times' : [[800]]}
ss1 = p.Population(1, p.SpikeSourceArray, injection1)
ss1_proj_a = p.Projection(ss1, who_statement_gate, p.FromListConnector([[0, 0, weight_to_spike, 5]]), target='excitatory')
ss1_proj_b = p.Projection(ss1, who_query_gate, p.FromListConnector([[0, 0, weight_to_spike, 5]]), target='excitatory')
ss1_proj_c = p.Projection(ss1, where, p.FromListConnector([[0, 0, weight_to_spike, 1]]), target='excitatory')
'''

src_pop.record()
who_statement_gate.record()
where_statement_gate.record()
what_statement_gate.record()
who_query_gate.record()
where_query_gate.record()
what_query_gate.record()

dst_who.record()
dst_where.record()
dst_what.record()

p.run(10 * 1000)

src_pop_spikes = src_pop.getSpikes(compatible_output=True)
who_statement_gate_spikes = who_statement_gate.getSpikes(compatible_output=True)
where_statement_gate_spikes = where_statement_gate.getSpikes(compatible_output=True)
what_statement_gate_spikes = what_statement_gate.getSpikes(compatible_output=True)
who_query_gate_spikes = who_query_gate.getSpikes(compatible_output=True)
where_query_gate_spikes = where_query_gate.getSpikes(compatible_output=True)
what_query_gate_spikes = what_query_gate.getSpikes(compatible_output=True)
dst_who_spikes = dst_who.getSpikes(compatible_output=True)
dst_where_spikes = dst_where.getSpikes(compatible_output=True)
dst_what_spikes = dst_what.getSpikes(compatible_output=True)

print 'a' , who_statement_gate_spikes 
print 'b' , where_statement_gate_spikes 
temp = output_populations['where_gate']
tempSpikes = temp.getSpikes(compatible_output=True)
print 'c' , tempSpikes 
print 'd' , src_pop_spikes 
