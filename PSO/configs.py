import random

#-----------------------------------------------------------------------------+

hjMax = {
    'hj1': 120.0,
    'hj2': 45.0,
    'raj1': 120.0,
    'raj2': 1.0,
    'raj3': 120.0,
    'raj4': 90.0,
    'laj1': 120.0,
    'laj2': 95.0,
    'laj3': 120.0,
    'laj4': 1.0,
    'rlj1': 1.0,
    'rlj2': 25.0,
    'rlj3': 100.0,
    'rlj4': 1.0,
    'rlj5': 75.0,
    'rlj6': 45.0,
    'llj1': 1.0,
    'llj2': 45.0,
    'llj3': 100.0,
    'llj4': 1.0,
    'llj5': 75.0,
    'llj6': 25.0,
}

hjMin = {
    'hj1': -120.0,
    'hj2': -45.0,
    'raj1': -120.0,
    'raj2': -95.0,
    'raj3': -120.0,
    'raj4': -1.0,
    'laj1': -120.0,
    'laj2': -1.0,
    'laj3': -120.0,
    'laj4': -90.0,
    'rlj1': -90.0,
    'rlj2': -45.0,
    'rlj3': -25.0,
    'rlj4': -130.0,
    'rlj5': -45.0,
    'rlj6': -25.0,
    'llj1': -90.0,
    'llj2': -25.0,
    'llj3': -25.0,
    'llj4': -130.0,
    'llj5': -45.0,
    'llj6': -45.0,
}


def congigure_vector(vector):
    return {
        "rlj1": [vector[0], vector[1]],
        "llj1": [vector[1], vector[0]],
        "rlj3": [vector[2], vector[3]],
        "llj3": [vector[3], vector[2]],
        "rlj4": [vector[4], vector[5]],
        "llj4": [vector[5], vector[4]],
        "rlj5": [vector[6], vector[7]],
        "llj5": [vector[7], vector[6]],
        "rlj6": [vector[8], vector[9]],
        "llj6": [vector[9], vector[8]],
    }

def config_to_vector(config):

    joints = [
        'rlj1', 'llj1', 'rlj3', 'llj3', 'rlj4', 'llj4', 'rlj5', 'llj5', 'rlj6',
        'llj6'
    ]

    lst = []

    for joint in joints:
        lst.append(config[joint][0])

    return lst

def get_custom_vector(child):
    return config_to_vector(child)


def get_random_vector():
    lj1 = (random.uniform(hjMin['rlj1'], hjMax['rlj1']),
           random.uniform(hjMin['rlj1'], hjMax['rlj1']))

    lj3 = (random.uniform(hjMin['rlj3'], hjMax['rlj3']),
           random.uniform(hjMin['rlj3'], hjMax['rlj3']))

    lj4 = (random.uniform(hjMin['rlj4'], hjMax['rlj4']),
           random.uniform(hjMin['rlj4'], hjMax['rlj4']))

    lj5 = (random.uniform(hjMin['rlj5'], hjMax['rlj5']),
           random.uniform(hjMin['rlj5'], hjMax['rlj5']))

    lj6 = (random.uniform(hjMin['rlj6'], hjMax['rlj6']),
           random.uniform(hjMin['rlj6'], hjMax['rlj6']))

    return [
        lj1[0], lj1[1], lj3[0], lj3[1], lj4[0], lj4[1], lj5[0], lj5[1], lj6[0],
        lj6[1]
    ]


joints = [
    'rlj1', 'llj1', 'rlj3', 'llj3', 'rlj4', 'llj4', 'rlj5', 'llj5', 'rlj6',
    'llj6'
]


print(congigure_vector([-44.146052750186364, -37.59012238826328, 65.86125426370435, 38.1258268703742, -83.29634569170925, -72.79896808588151, 30.30464613964763, 24.584450648748327, 6.271676051348379, -14.851921243124966]))