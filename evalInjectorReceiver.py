import sys
import time
import re
from grammar_qa1 import *
from readInput import *

from spinnman.messages.eieio.data_messages.eieio_32bit.\
    eieio_32bit_data_message import EIEIO32BitDataMessage
from spynnaker.pyNN.utilities.conf import config
from spinnman.connections.udp_packet_connections.reverse_iptag_connection \
    import ReverseIPTagConnection

#globals
udp_connection = \
    ReverseIPTagConnection(remote_host=config.get("Machine", "machineName"),
                           remote_port=12346)

base_key = 0x80800
#keys allowed: 0x70800 - 0x70811

delay = 0.05

def sendKeyTest(number):
#def sendKey(number):
    print number

def sendKey(number):
#def sendKey2(number):
    message = EIEIO32BitDataMessage()
    key = base_key | number
    message.add_key(key)
    udp_connection.send_eieio_message(message)
    time.sleep(delay)


def getSentenceTest(sentenceNum):
    if (sentenceNum == 0): 
        return "Mary moved to the bathroom."
    elif (sentenceNum == 1):
        return "John went to the hallway."
    elif (sentenceNum == 2):
        return "Where is Mary?"
    elif (sentenceNum == 3):
        return "Daniel went back to the hallway."
    elif (sentenceNum == 4):
        return "Sandra moved to the garden."
    elif (sentenceNum == 5):
        return "Where is Daniel?"
    elif (sentenceNum == 6):
        return "John moved to the office."
    elif (sentenceNum == 7):
        return "Sandra journeyed to the bathroom."
    elif (sentenceNum == 8):
        return "Where is Daniel?"
    elif (sentenceNum == 9):
        return "Mary moved to the hallway."
    elif (sentenceNum == 10):
        return "Daniel travelled to the office."
    elif (sentenceNum == 11):
        return "Where is Daniel?"
    elif (sentenceNum == 12):
        return "John went back to the garden."
    elif (sentenceNum == 13):
        return"John moved to the bedroom."
    elif (sentenceNum == 14):
        return "Where is Sandra?"
    else:
        return "Where is john?"
        return "Daniel went to the bathroom."
        return "John went to the hallway."

def breakSentenceIntoWords(sentence):
    wordList = re.findall(r"[\w']+|[.,!?;]", sentence)
    return wordList

def send(wordString):
    wordNum = -1
    wordIter = 0
    for word in words:
        if wordString == word:
            wordNum = wordIter
        wordIter = wordIter + 1

    wordNum = wordNum + 1 # 0 is to start the parser
    sendKey(wordNum)

def sendSentence(wordList):
    sendKey(0)
    for word in wordList:
        send (word)
    time.sleep(0.2)

###---------------Main--------------
inputArgLength = len (sys.argv)
if inputArgLength != 2:
    testNum = 0
else:
    testNum = int(sys.argv[1])
print testNum

hugeSentenceList = getSentences("train.txt")


for sentenceNum in range ((testNum*15),(testNum+1)*15):
    inputTuple = hugeSentenceList[sentenceNum]
    Sentence = inputTuple[1]
    sentence = Sentence.lower()
    wordList = breakSentenceIntoWords(sentence)

    sendSentence(wordList)

""""
#Daniel went to the bathroom. 
sendKey(0)
sendKey(3)
sendKey(21)
sendKey(19)
sendKey(18)
sendKey(9)
sendKey(2)
time.sleep(0.2)

#John went to the hallway.
sendKey(0)
sendKey(4)
sendKey(21)
sendKey(19)
sendKey(18)
sendKey(12)
sendKey(2)
time.sleep(0.2)

#Where is john?
sendKey(0)
sendKey(7)
sendKey(13)
sendKey(4)
sendKey(1)
"""""



