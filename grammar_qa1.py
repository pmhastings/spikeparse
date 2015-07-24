# this is for facebook task QA1: single-supporting fact
# ../Data/tasks_1-20_v1-2/en/qa1_single-supporting-fact_test.txt
# There are two end states: 6 for assertions, and 11 for questions.
# from parse import makeTransition

locations = ["kitchen", "bedroom", "bathroom", "hallway", "garden"]
people = ['daniel', 'john', 'mary', 'sandra']
objects = []
questions = ['where']
locVerbs = ["went", "journeyed", "travelled", "traveled"]
words = ['?',
        '.',
        'daniel',
        'john',
        'mary',
        'sandra', 
        'where',
        'back',
        'bathroom',
        'bedroom',
        'garden',
        'hallway',
        'is',
        'journeyed',
        'kitchen',
        'moved',
        'office',
        'the',
        'to',
        'travelled',
        'traveled',
        'went' # , 'unknown'
    ]

NUMBER_WORDS = len(words)+1

NUMBER_PEOPLE = 10
NUMBER_LOCS = 10
NUMBER_OBJS = 10
NUMBER_QUES = 3

# Grammar:
# S <- PN VP .
# PN: Person -> states(Person(i))
# VP <- "locverb" LNP
# LNP: Loc: Loc -> states(Loc(i))

# As a graph
# 0 -PN-> 1 PN ->Sem(pers(i))
# 1 -locVerbs-> 2
# 2 -to-> 3
# 3 -the-> 4
# 4 -Loc-> 5: Sem(loc(j))
# 5 -.-> 6
# 2 -back-> 7
# 7 -to-> 3
# 0 -Where-> 8
# 8 -is-> 9
# 9 -is-> 10
# 10 -?-> 11

TRANSITIONS = \
  [[[0,people,1],dict(person=True)],
    [[1,locVerbs,2], {}],
    [[2,['to'],3], {}],
    [[3,['the'],4], {}],
    [[4,locations,5],dict(location=True)],
    [[5,['.'],6], {}],
    [[2,['back'],7], {}],
    [[7,['to'],3], {}],
    [[0,['where'],8], dict(question=True)],
    [[8,['is'],9], {}],
    [[9,people,10],dict(person=True)],
    [[10,['?'],11], {}]]

NUMBER_SYNSTATES = 12
NUMBER_STATES = NUMBER_SYNSTATES + NUMBER_PEOPLE + NUMBER_LOCS + NUMBER_OBJS + NUMBER_QUES


finalSynStateAssertion = 6
finalSynStateQuery = 11
