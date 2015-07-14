from spinnman.transceiver import create_transceiver_from_hostname

from spinnman.data.file_data_reader import FileDataReader as SpinnmanFileDataReader 

from spynnaker.pyNN.spynnaker_comms_functions import SpynnakerCommsFunctions 
 
import pickle 

txrx = create_transceiver_from_hostname(hostname="192.168.240.1", discover=False)

txrx.ensure_board_is_ready(int(5)) 

txrx.discover_connections() 
 
application_data_file_reader = SpinnmanFileDataReader("192.168.240.1_appData_0_0_7.dat")
txrx.write_memory(0, 0, 1879048192, application_data_file_reader, 124)
txrx.write_memory(0, 0, 3842012144, 1879048192)
application_data_file_reader = SpinnmanFileDataReader("192.168.240.1_appData_0_0_9.dat")
txrx.write_memory(0, 0, 1879048316, application_data_file_reader, 124)
txrx.write_memory(0, 0, 3842012400, 1879048316)
application_data_file_reader = SpinnmanFileDataReader("192.168.240.1_appData_0_0_2.dat")
txrx.write_memory(0, 0, 1879048440, application_data_file_reader, 128692)
txrx.write_memory(0, 0, 3842011504, 1879048440)
application_data_file_reader = SpinnmanFileDataReader("192.168.240.1_appData_0_0_13.dat")
txrx.write_memory(0, 0, 1879201136, application_data_file_reader, 218088)
txrx.write_memory(0, 0, 3842012912, 1879201136)
application_data_file_reader = SpinnmanFileDataReader("192.168.240.1_appData_0_0_6.dat")
txrx.write_memory(0, 0, 1879443228, application_data_file_reader, 124)
txrx.write_memory(0, 0, 3842012016, 1879443228)
application_data_file_reader = SpinnmanFileDataReader("192.168.240.1_appData_0_0_8.dat")
txrx.write_memory(0, 0, 1879443352, application_data_file_reader, 124)
txrx.write_memory(0, 0, 3842012272, 1879443352)
application_data_file_reader = SpinnmanFileDataReader("192.168.240.1_appData_0_0_1.dat")
txrx.write_memory(0, 0, 1879443476, application_data_file_reader, 128)
txrx.write_memory(0, 0, 3842011376, 1879443476)
application_data_file_reader = SpinnmanFileDataReader("192.168.240.1_appData_0_0_12.dat")
txrx.write_memory(0, 0, 1879443604, application_data_file_reader, 124)
txrx.write_memory(0, 0, 3842012784, 1879443604)
application_data_file_reader = SpinnmanFileDataReader("192.168.240.1_appData_0_0_5.dat")
txrx.write_memory(0, 0, 1879443728, application_data_file_reader, 124)
txrx.write_memory(0, 0, 3842011888, 1879443728)
application_data_file_reader = SpinnmanFileDataReader("192.168.240.1_appData_0_0_11.dat")
txrx.write_memory(0, 0, 1879443852, application_data_file_reader, 124)
txrx.write_memory(0, 0, 3842012656, 1879443852)
application_data_file_reader = SpinnmanFileDataReader("192.168.240.1_appData_0_0_4.dat")
txrx.write_memory(0, 0, 1879443976, application_data_file_reader, 124)
txrx.write_memory(0, 0, 3842011760, 1879443976)
application_data_file_reader = SpinnmanFileDataReader("192.168.240.1_appData_0_0_10.dat")
txrx.write_memory(0, 0, 1879444100, application_data_file_reader, 124)
txrx.write_memory(0, 0, 3842012528, 1879444100)
application_data_file_reader = SpinnmanFileDataReader("192.168.240.1_appData_0_0_3.dat")
txrx.write_memory(0, 0, 1879444224, application_data_file_reader, 220288)
txrx.write_memory(0, 0, 3842011632, 1879444224)
router_table = pickle.load(open("picked_routing_table_for_0_0", "rb"))
txrx.load_multicast_routes(router_table.x, router_table.y, router_table.multicast_routing_entries, app_id=30)
executable_targets = pickle.load(open("picked_executables_mappings", "rb"))
core_subset = executable_targets["/Users/peter/Envs/spinn/lib/python2.7/site-packages/spynnaker/pyNN/model_binaries/reverse_iptag_multicast_source.aplx"]
file_reader = SpinnmanFileDataReader("/Users/peter/Envs/spinn/lib/python2.7/site-packages/spynnaker/pyNN/model_binaries/reverse_iptag_multicast_source.aplx")
txrx.execute_flood(core_subset, file_reader, 30, 10000)
core_subset = executable_targets["/Users/peter/Envs/spinn/lib/python2.7/site-packages/spynnaker/pyNN/model_binaries/IF_curr_exp.aplx"]
file_reader = SpinnmanFileDataReader("/Users/peter/Envs/spinn/lib/python2.7/site-packages/spynnaker/pyNN/model_binaries/IF_curr_exp.aplx")
txrx.execute_flood(core_subset, file_reader, 30, 14508)
core_subset = executable_targets["/Users/peter/Envs/spinn/lib/python2.7/site-packages/spynnaker/pyNN/model_binaries/spike_source_array.aplx"]
file_reader = SpinnmanFileDataReader("/Users/peter/Envs/spinn/lib/python2.7/site-packages/spynnaker/pyNN/model_binaries/spike_source_array.aplx")
txrx.execute_flood(core_subset, file_reader, 30, 10352)
executable_targets = pickle.load(open("picked_executable_targets", "rb"))
spinnaker_comms = SpynnakerCommsFunctions(None, None)
spinnaker_comms._setup_interfaces("192.168.240.1")
spinnaker_comms._start_execution_on_machine(executable_targets, 30, 750)
