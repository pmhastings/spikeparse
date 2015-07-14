# this is for facebook task QA2: two supporting facts
# ../Data/tasks_1-20_v1-2/en/qa1_single-supporting-fact_test.txt
# There are two end states: 6 for assertions, and 11 for questions.

locations = ['bathroom', 'bedroom', 'garden', 'hallway', 'kitchen', 'office']

people = ['Daniel', 'John', 'Mary', 'Sandra']

# moved to
# went back to
# travelled to

# discarded X
# got X there
# grabbed X there
# put down X (there)
locVerbs = ["went to", "journeyed to", "travelled to"}
words = {'?': 0,
        '.': 1,
        'Daniel': 2,
        'John': 3,
        'Mary': 4,
        'Sandra': 5, 
        'Where': 6,
        'back': 7,
        'bathroom': 8,
        'bedroom': 9,
        'garden': 10,
        'hallway': 11,
        'is': 12,
        'journeyed': 13,
        'kitchen': 14,
        'moved': 15,
        'office': 16,
        'the': 17,
        'to': 18,
        'travelled': 19,
        'went': 20}

NUMBER_WORDS = 21

NUMBER_SYNSTATES = 10
NUMBER_PEOPLE = 10
NUMBER_LOCS = 10
NUMBER_OBJS = 10
NUMBER_STATES = NUMBER_SYNSTATES + NUMBER_PEOPLE + NUMBER_LOCS + NUMBER_OBJS

# Grammar graph as above
def makeTransitions():
    # 0 -PN-> 1 PN ->Sem(pers(i))
    makeTransition(0,people,1,person=True)
    # 1 -loc-> 2
    makeTransition(1,['locVerb'],2)
    # 2 -to-> 3
    makeTransition(2,['to'],3)
    # 3 -the-> 4
    makeTransition(3,['the'],4)
    # 4 -Loc-> 5: Sem(loc(j))
    makeTransition(4,locations,5,location=True)
    # 5 -period> 6
    makeTransition(5,['.'],6)
    # 2 -back-> 7
    makeTransition(2,['back'],7)
    # 7 -to-> 3
    makeTransition(3,['to'],4)
    # 0 -Where-> 8
    makeTransition(0,['Where'],8)
    # 8 -is-> 9
    makeTransition(8,['is'],9)
    # 9 -is-> 10
    makeTransition(9,people,10,pquery=True)
    # 10 -?-> 11
    makeTransition(10,['?'],11)

finalSynStateAssertion = 6
finalSynStateQuery = 11
