# this is for facebook task QA6
# ../Data/tasks_1-20_v1-2/en/qa6_yes-no-questions_test.txt

locations = ['bathroom', 'bedroom', 'garden', 'hallway', 'kitchen', 'office']

people = ['daniel', 'john', 'mary', 'sandra']

# moved to
# went back to
# travelled to

# discarded X
# got X there
# grabbed X there
# put down X (there)
locVerbs = ['moved', 'journeyed', 'travelled', 'went']
getVerbs = ['got', 'grabbed', 'took']  # + picked up
putVerbs = ['discarded', 'dropped', 'left'] # + put down 
words = ['.', '?', 'daniel', 'john', 'mary', 'sandra',
        'apple', 'back', 'bathroom', 'bedroom', 'discarded', 'down',
        'dropped', 'football', 'garden', 'got', 'grabbed', 'hallway', 'is',
        'journeyed', 'kitchen', 'left', 'milk', 'moved', 'office', 'picked',
        'put', 'the', 'there', 'to', 'took', 'travelled', 'up', 'went']
objects = ['apple', 'football', 'milk']
locations = ['bathroom', 'bedroom', 'garden', 'hallway', 'kitchen', 'office']

# Grammar graph as above
TRANSITIONS = \
    [[[0,people,1], dict(person=True)],
    [[1,locVerbs,2],{}],
    [[2,['to'],3],{}],
    [[3,['the'],4],{}],
    [[4,locations,5], dict(location=True)],
    [[5,['.'],6],{}],                     # final
    [[1,getVerbs,7],{}],
    [[7,['the'],8],{}],
    [[8,objects,9], dict(object=True)],
    [[9,['.'],6], {}],
    [[9,['there'],10], {}],
    [[10,['.'],6], {}],
    [[1, ['picked'], 11], {}],
    [[11, ['up'], 7], {}],
    [[1,putVerbs,12],{}],
    [[12,['the'],13],{}],
    [[13,objects,14], dict(object=True)],  # should have deleted object
    [[14,['.'],6], {}],
    [[14,['there'],15], {}],
    [[15,['.'],6], {}],
    [[1, ['put'], 16], {}],
    [[16, ['down'], 12], {}],
    [[2,['back'],17],{}],
    [[17,['to'],3],{}],
    [[0,['is'],18],dict(question=True)],
    [[18,['people'],19], dict(person=True)],
    [[19,['in'],20], {}],
    [[20,['the'],21],{}],
    [[21,locations,22], dict(location=True)],
    [[22,['?'],23],{}],                   # final
    [[0,['where'],24],dict(question=True)],
    [[24,['is'],25],{}],
    [[25,['the'],26],{}],
    [[26,objects,22], dict(object=True)],
    [[25,['people'],22], dict(person=True)]]

NUMBER_WORDS = len(words)+1

NUMBER_SYNSTATES = max([tr[0][2] for tr in TRANSITIONS])+1
NUMBER_PEOPLE = 10
NUMBER_LOCS = 10
NUMBER_OBJS = 10
NUMBER_QUES = 1
NUMBER_STATES = NUMBER_SYNSTATES + NUMBER_PEOPLE + NUMBER_LOCS + NUMBER_OBJS


finalSynStateAssertion = 6
finalSynStateQuery = 23
