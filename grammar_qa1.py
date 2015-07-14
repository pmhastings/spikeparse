# this is for facebook task QA1: single-supporting fact
# ../Data/tasks_1-20_v1-2/en/qa1_single-supporting-fact_test.txt
# There are two end states: 6 for assertions, and 11 for questions.
# from parse import makeTransition

locations = ["kitchen", "bedroom", "bathroom", "hallway", "garden"]
people = ['Daniel', 'John', 'Mary', 'Sandra']

locVerbs = ["went to", "journeyed to", "travelled to"]
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
        'went': 20,
        'unknown': 21}

NUMBER_WORDS = 22

NUMBER_PEOPLE = 10
NUMBER_LOCS = 10
NUMBER_OBJS = 10

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

# Grammar graph as above
# def makeTransitions():
#     # 0 -PN-> 1 PN ->Sem(pers(i))
#     makeTransition(0,people,1,person=True)
#     # 1 -loc-> 2
#     makeTransition(1,locVerbs,2)
#     # 2 -to-> 3
#     makeTransition(2,['to'],3)
#     # 3 -the-> 4
#     makeTransition(3,['the'],4)
#     # 4 -Loc-> 5: Sem(loc(j))
#     makeTransition(4,locations,5,location=True)
#     # 5 -period> 6
#     makeTransition(5,['.'],6)
#     # 2 -back-> 7
#     makeTransition(2,['back'],7)
#     # 7 -to-> 3
#     makeTransition(3,['to'],4)
#     # 0 -Where-> 8
#     makeTransition(0,['Where'],8)
#     # 8 -is-> 9
#     makeTransition(8,['is'],9)
#     # 9 -is-> 10
#     makeTransition(9,people,10,pquery=True)
#     # 10 -?-> 11
#     makeTransition(10,['?'],11)
# [[2, ['back']], {'location':True}]

TRANSITIONS = [[[0,people,1],dict(person=True)],     # 0 -PN-> 1 PN ->Sem(pers(i))
    # 1 -loc-> 2
    [[1,locVerbs,2], {}],
    # 2 -to-> 3
    [[2,['to'],3], {}],
    # 3 -the-> 4
    [[3,['the'],4], {}],
    # 4 -Loc-> 5: Sem[loc[j]]
    [[4,locations,5],dict(location=True)],
    # 5 -period> 6
    [[5,['.'],6], {}],
    # 2 -back-> 7
    [[2,['back'],7], {}],
    # 7 -to-> 3
    [[3,['to'],4], {}],
    # 0 -Where-> 8
    [[0,['Where'],8], {}],
    # 8 -is-> 9
    [[8,['is'],9], {}],
    # 9 -is-> 10
    [[9,people,10],dict(pquery=True)],
    # 10 -?-> 11
    [[10,['?'],11], {}]]

NUMBER_SYNSTATES = 12
NUMBER_STATES = NUMBER_SYNSTATES + NUMBER_PEOPLE + NUMBER_LOCS + NUMBER_OBJS


finalSynStateAssertion = 6
finalSynStateQuery = 11
