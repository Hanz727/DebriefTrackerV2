from enum import Enum

class Squadrons(Enum):
    VF103 = 'VF-103'
    VFA34 = 'VFA-34'

class Weapons(Enum):
    # These names are prefixes and thus must match for all the weapon types, i.e. AIM-54(C-MK60/B-MK47), AIM-9(M/X/F)
    phoenix = 'AIM-54'
    amraam = 'AIM-120'
    sidewinder = 'AIM-9'
    sparrow = 'AIM-7'