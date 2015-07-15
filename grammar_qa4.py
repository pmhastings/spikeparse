# this is for facebook task QA4: two arg relations
# ../Data/tasks_1-20_v1-2/en/qa4_two-arg-relations_test.txt

# There are two end states: 6 for assertions, and 11 for questions.
# Note: I either downcase everything or have 'The' and 'the' 

# 1 The hallway is east of the bathroom.
# 2 The bedroom is west of the bathroom.
# 3 What is the bathroom east of?	bedroom	2
# 3 What is west of the kitchen?   bedroom 1

locations = ['bathroom', 'bedroom', 'garden', 'hallway', 'kitchen', 'office']
directions = ['east', 'north', 'south', 'west']

# 'The', 'What', 'is', 'the', 'of', 

words = ['.',
        '?',
        'The', 
        'What', 
        'bathroom', 
        'bedroom', 
        'east', 
        'garden', 
        'hallway', 
        'is', 
        'kitchen', 
        'north', 
        'of', 
        'office', 
        'south', 
        'the', 
        'west']

TRANSITIONS = \
  [[[0,['The'],1],{}],                        # 0 -The-> 1 
    [[1,locations,2], dict(location=True)],   # 1 -loc-> 2
    [[2,['is'],3], {}],                       # 2 -is-> 3
    [[3,directions,4], dict(direction=True)], # 3 -dir-> 4
    [[4,['of'],5], {}],                       # 4 -of-> 5
    [[5,['the'],6], {}],                      # 5 -the-> 6
    [[6,locations,7], dict(location2=True)],  # 6 -dir-> 7
    [[7,['.'],8], {}]]                        # final
    [[0,['What'],9], dict(question=True)],
    [[9,['is'],10],{}],
    [[10,directions,11], dict(direction=True)],
    [[11,['of'],12], {}],
    [[12,['the'],13], {}],
    [[13,locations,14], dict(location=True)],
    [[14,['?'],15], {}],                  # final
    [[10,['the'],16], {}],
    [[16,locations,17], dict(location2=True)],
    [[17,directions,18], dict(direction=True)],
    [[18,['of'],19], {}],
    [[19,['?'],15], {}]]                  # final

NUMBER_WORDS = len(words)+1

NUMBER_LOCS = len(locations)
NUMBER_DIRS = len(directions)
NUMBER_QUES = 1

NUMBER_SYNSTATES = max([tr[0][2] for tr in TRANSITIONS])+1
# number locs twice because I have location and location2
NUMBER_STATES = NUMBER_SYNSTATES + NUMBER_LOCS + NUMBER_DIRS + NUMBER_LOCS + NUMBER_QUES


finalSynStateAssertion = 8
finalSynStateQuery = 15
