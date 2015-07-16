# NOTE: this requires PyAudio because it uses the Microphone class
import os
import speech_recognition as sr

def say (text):
    os.system("say -v Vicki " + "\"" + text + "\"")

def get_text(prompt="Say your statement now"):
    r = sr.Recognizer()
    good_recording = False
    text = ""
    while not good_recording:
        print prompt
        say(prompt)
        # use the default microphone as the audio source
        with sr.Microphone() as source:
            # listen for the first phrase and extract it into audio data
            audio = r.listen(source)  
        try:
            text = str(r.recognize(audio))
            # recognize speech using Google Speech Recognition
            print("You said: " + text)  
            say( "You said: " + text)
            say("Is this correct?")
            response = raw_input('Is this correct? Type y or n or q (to quit): ')
            if response == "y":
                good_recording = True
            elif response == "q":
                exit()
        except LookupError:  # speech is unintelligible
            text = "I did not understand"
            print(text)
            say(text)
    return text


# subjects = ["john", "bob", "tom", "mary", "susan"]
# places = ["kitchen", "lab", "office", "bathroom", "attic"]
# objects = ["ball", "bat", "book", "bottle", "hat"]
# questions = ["who", "what", "where"]

# memory=[]

def getSentence(words, prompt):
    text=get_text(prompt);
    print "initial text: " + text
    text_list = text.lower().split()
    final_list=[]
    for i in range(len(text_list)):
        word=text_list[i];
        if (word in words):
            final_list.append(text_list[i])
    if (final_list[0][0] == 'w'):
        final_list.append('?')
    else:
        final_list.append('.')
    return final_list
