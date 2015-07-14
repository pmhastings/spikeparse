locations = ["kitchen", "classroom1", "classroom2", "lecture_room"]
objects = ["ball", "dog", "cube", "hyperplane", "spike"]
people = ["John", "Sergio", "Peter", "Guido", "Ritwik", "Eric", "Philip", "Kan", "Shashi", "Pam"]
locVerbs = ["is in", "are in"]
words = {'.': 0,
        'unknown': 1,
        '2': 2,
        'Eric': 3,
        'Guido': 4,
        'John': 5,
        'Kan': 6,
        'Pam': 7,
        'Peter': 8,
        'Philip': 9,
        'Ritwik': 10,
        'Sergio': 11,
        'Shashi': 12,
        'a': 13,
        'ball': 14,
        'classroom1': 15,
        'classroom2': 16,
        'cube': 17,
        'dog': 18,
        'has': 19,
        'hyperplane': 20,
        'in': 21,
        'is': 22,
        'kitchen': 23,
        'lecture_room': 24,
        'pointer': 25,
        'spike': 26,
        'the': 27,
        'where': 28,
        'who': 29}

NUMBER_WORDS = 30

NUMBER_SYNSTATES = 10
NUMBER_PEOPLE = 10
NUMBER_LOCS = 10
NUMBER_OBJS = 10
NUMBER_STATES = NUMBER_SYNSTATES + NUMBER_PEOPLE + NUMBER_LOCS + NUMBER_OBJS
