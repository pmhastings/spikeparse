import socket
import spinnman.messages.eieio.create_eieio_data as parse_msg
import spinnman.data.little_endian_byte_array_byte_reader as byte_reader
import os

def say (text):
    os.system("say -v Vicki " + "\"" + text + "\"")

UDP_IP = "0.0.0.0"
UDP_PORT = 17895

association = {
    460960: 'daniel',
    460961: 'john',
    460962: 'mary',
    460963: 'sandra',
    460964: 'Peter',
    460965: 'Chris',
    460966: 'Phil',
    460967: 'Emre',
    460968: 'Kate',
    460969: 'Michael',

    460976: 'kitchen',
    460977: 'bedroom',
    460978: 'bathroom',
    460979: 'hallway',
    460980: 'garden',
    117: 'Classroom',
    118: 'Bed',
    119: 'Gondola',
    120: 'Corridor',
    121: 'Lectureroom',

    128: 'Ball',
    129: 'Glass',
    130: 'Plate',
    131: 'Tablet',
    132: 'Notebook',
    133: 'paper',
    134: 'cup',
    135: 'box',
    136: 'pen',
    137: 'camera',
    }

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    data_bytearray = bytearray(data)
    byte_reader_msg = byte_reader.LittleEndianByteArrayByteReader(data_bytearray)
    packet = parse_msg.read_eieio_data_message(byte_reader_msg)
    n_keys = packet.n_elements
    for i in xrange(n_keys):
        key = packet.next_element.key
        if key not in association:
            print "I don't know what this means:", key
        else:
            print association[key]
            say(association[key])
    print "\n"
