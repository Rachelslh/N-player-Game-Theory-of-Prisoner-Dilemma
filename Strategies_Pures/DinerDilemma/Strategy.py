from enum import Enum, auto


class Strategy(Enum):

    EXPENSIVE = 'Cher'
    CHEAP = 'Pas Cher'
    STRICTLY_DOMINANT_EXPENSIVE = 'La stratégie \'Cher\' est strictement dominante'
    STRICTLY_DOMINANT_CHEAP = 'La stratégie \'Pas Cher\' est strictement dominante'
    LAX_DOMINANT_EXPENSIVE = 'La stratégie \'Cher\' est faiblement dominante'
    LAX_DOMINANT_CHEAP = 'La stratégie \'Pas Cher\' est faiblement dominante'

