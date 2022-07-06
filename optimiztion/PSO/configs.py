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

        "rlj2": [vector[2], vector[3]],
        "llj2": [vector[3], vector[2]],

        "rlj3": [vector[4], vector[5]],
        "llj3": [vector[5], vector[4]],

        "rlj4": [vector[6], vector[7]],
        "llj4": [vector[7], vector[6]],

        "rlj5": [vector[8], vector[9]],
        "llj5": [vector[9], vector[8]],

        "rlj6": [vector[10], vector[11]],
        "llj6": [vector[11], vector[10]],

        "raj1": [vector[12], vector[13]],
        "laj1": [vector[13], vector[12]],

        "raj2": [vector[14], vector[15]],
        "laj2": [vector[15], vector[14]],

        "raj3": [vector[16], vector[17]],
        "laj3": [vector[17], vector[16]],

        "raj4": [vector[18], vector[19]],
        "laj4": [vector[19], vector[18]],
    }


def config_to_vector(config):

    joints = [
        'rlj1', 'llj1','rlj2', 'llj2', 'rlj3', 'llj3', 'rlj4', 'llj4', 'rlj5', 'llj5', 'rlj6',
        'llj6', 'raj1', 'laj1', 'raj2', 'laj2', 'raj3', 'laj3', 'raj4', 'laj4',
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
           
    lj2 = (random.uniform(hjMin['rlj2'], hjMax['rlj2']),
            random.uniform(hjMin['rlj2'], hjMax['rlj2']))

    lj3 = (random.uniform(hjMin['rlj3'], hjMax['rlj3']),
           random.uniform(hjMin['rlj3'], hjMax['rlj3']))

    lj4 = (random.uniform(hjMin['rlj4'], hjMax['rlj4']),
           random.uniform(hjMin['rlj4'], hjMax['rlj4']))

    lj5 = (random.uniform(hjMin['rlj5'], hjMax['rlj5']),
           random.uniform(hjMin['rlj5'], hjMax['rlj5']))

    lj6 = (random.uniform(hjMin['rlj6'], hjMax['rlj6']),
           random.uniform(hjMin['rlj6'], hjMax['rlj6']))
    
    aj1 = (random.uniform(hjMin['raj1'], hjMax['raj1']),
            random.uniform(hjMin['raj1'], hjMax['raj1']))

    aj2 = (random.uniform(hjMin['raj2'], hjMax['raj2']), 
            random.uniform(hjMin['raj2'], hjMax['raj2']))

    aj3 = (random.uniform(hjMin['raj3'], hjMax['raj3']), 
            random.uniform(hjMin['raj3'], hjMax['raj3']))

    aj4 = (random.uniform(hjMin['raj4'], hjMax['raj4']), 
            random.uniform(hjMin['raj4'], hjMax['raj4']))



    return [
       lj1[0], lj1[1], lj2[0], lj2[1] ,lj3[0], lj3[1], lj4[0], lj4[1], lj5[0], lj5[1], lj6[0],
        lj6[1], aj1[0], aj1[1], aj2[0], aj2[1], aj3[0], aj3[1], aj4[0], aj4[1],
    ]


joints = [
    'rlj1', 'llj1', 'rlj2', 'llj2' ,'rlj3', 'llj3', 'rlj4', 'llj4', 'rlj5', 'llj5', 'rlj6',
    'llj6', 'raj1', 'laj1', 'raj2', 'laj2', 'raj3', 'laj3', 'raj4', 'laj4'
]

