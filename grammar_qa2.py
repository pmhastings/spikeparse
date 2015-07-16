# this is for facebook task QA2: two supporting facts
# ../Data/tasks_1-20_v1-2/en/qa1_single-supporting-fact_test.txt
# There are two end states: 6 for assertions, and 11 for questions.

locations = ['bathroom', 'bedroom', 'garden', 'hallway', 'kitchen', 'office']

people = ['daniel', 'john', 'mary', 'sandra']

# moved to
# went back to
# travelled to

# discarded X
# got X there
# grabbed X there
# put down X (there)
locVerbs = ['went', 'journeyed', 'travelled']
getVerbs = ['got', 'grabbed', 'took']  # + picked up
putVerbs = ['discarded', 'dropped', 'left'] # + put down 
words = ['.', '?', 'daniel', 'john', 'mary', 'sandra',
        'where', 'apple', 'back', 'bathroom', 'bedroom', 'discarded', 'down',
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
    [[2,getVerbs,7],{}],
    [[7,['the'],8],{}],
    [[8,objects,9], dict(object=True)],
    [[9,['.'],6], {}],
    [[9,['there'],10], {}],
    [[10,['.'],6], {}],
    [[2, ['picked'], 11], {}],
    [[11, ['up'], 7], {}],
    [[2,putVerbs,12],{}],
    [[12,['the'],13],{}],
    [[13,objects,14], dict(object=True)],  # should have deleted object
    [[14,['.'],6], {}],
    [[14,['there'],15], {}],
    [[15,['.'],6], {}],
    [[2, ['put'], 16], {}],
    [[16, ['down'], 12], {}],
    [[2,['back'],17],{}],
    [[17,['to'],4],{}],
    [[0,['where'],18],dict(question=True)],
    [[18,['is'],19],{}],
    [[19,['the'],20],{}],
    [[20,objects,21], dict(object=True)],
    [[21,['?'],22],{}]]                   # final

NUMBER_WORDS = len(words)+1

NUMBER_SYNSTATES = max([tr[0][2] for tr in TRANSITIONS])+1
NUMBER_PEOPLE = 10
NUMBER_LOCS = 10
NUMBER_OBJS = 10
NUMBER_QUES = 1
NUMBER_STATES = NUMBER_SYNSTATES + NUMBER_PEOPLE + NUMBER_LOCS + NUMBER_OBJS


finalSynStateAssertion = 6
finalSynStateQuery = 11
