import math

from enum import Enum

stats_by_cr = {
    0:     { "xp": 10, "prof": 2, "ac": 13, "attkBonus": 3, "dpr": range(0, 1), "saveDC": 13},
    0.125:   { "xp": 25, "prof": 2, "ac": 13, "attkBonus": 3, "dpr": range(2, 3), "saveDC": 13},
    0.25:     { "xp": 50, "prof": 2, "ac": 13, "attkBonus": 3, "dpr": range(4, 5), "saveDC": 13},
    0.5:    { "xp": 100, "prof": 2, "ac": 13, "attkBonus": 3, "dpr": range(6, 8), "saveDC": 13},
    1:    { "xp": 200, "prof": 2, "ac": 13, "attkBonus": 3, "dpr": range(9, 14), "saveDC": 13},
    2:    { "xp": 450, "prof": 2, "ac": 13, "attkBonus": 3, "dpr": range(15, 20), "saveDC": 13},
    3:    { "xp": 700, "prof": 2, "ac": 13, "attkBonus": 4, "dpr": range(21, 26), "saveDC": 13},
    4:   { "xp": 1100, "prof": 2, "ac": 14, "attkBonus": 5, "dpr": range(27, 32), "saveDC": 14},
    5:   { "xp": 1800, "prof": 3, "ac": 15, "attkBonus": 6, "dpr": range(33, 38), "saveDC": 15},
    6:   { "xp": 2300, "prof": 3, "ac": 15, "attkBonus": 6, "dpr": range(39, 44), "saveDC": 15},
    7:   { "xp": 2900, "prof": 3, "ac": 15, "attkBonus": 6, "dpr": range(45, 50), "saveDC": 15},
    8:   { "xp": 3900, "prof": 3, "ac": 16, "attkBonus": 7, "dpr": range(31, 36), "saveDC": 16},
    9:   { "xp": 5000, "prof": 4, "ac": 16, "attkBonus": 7, "dpr": range(57, 62), "saveDC": 16},
    10:   { "xp": 5900, "prof": 4, "ac": 17, "attkBonus": 7, "dpr": range(63, 68), "saveDC": 16},
    11:   { "xp": 7200, "prof": 4, "ac": 17, "attkBonus": 8, "dpr": range(69, 74), "saveDC": 17},
    12:   { "xp": 8400, "prof": 4, "ac": 17, "attkBonus": 8, "dpr": range(75, 80), "saveDC": 17},
    13:  { "xp": 10000, "prof": 5, "ac": 18, "attkBonus": 8, "dpr": range(81, 86), "saveDC": 18},
    14:  { "xp": 11500, "prof": 5, "ac": 18, "attkBonus": 8, "dpr": range(87, 92), "saveDC": 18},
    15:  { "xp": 13000, "prof": 5, "ac": 18, "attkBonus": 8, "dpr": range(93, 98), "saveDC": 18},
    16:  { "xp": 15000, "prof": 5, "ac": 18, "attkBonus": 9, "dpr": range(99, 104), "saveDC": 18},
    17:  { "xp": 18000, "prof": 6, "ac": 19, "attkBonus": 10, "dpr": range(105, 110), "saveDC": 19},
    18:  { "xp": 20000, "prof": 6, "ac": 19, "attkBonus": 10, "dpr": range(111, 116), "saveDC": 19},
    19:  { "xp": 22000, "prof": 6, "ac": 19, "attkBonus": 10, "dpr": range(117, 122), "saveDC": 19},
    20:  { "xp": 25000, "prof": 6, "ac": 19, "attkBonus": 10, "dpr": range(123, 140), "saveDC": 19},
    21:  { "xp": 33000, "prof": 7, "ac": 19, "attkBonus": 11, "dpr": range(141, 158), "saveDC": 20},
    22:  { "xp": 41000, "prof": 7, "ac": 19, "attkBonus": 11, "dpr": range(159, 176), "saveDC": 20},
    23:  { "xp": 50000, "prof": 7, "ac": 19, "attkBonus": 11, "dpr": range(177, 194), "saveDC": 20},
    24:  { "xp": 62000, "prof": 7, "ac": 19, "attkBonus": 12, "dpr": range(195, 212), "saveDC": 21},
    25:  { "xp": 75000, "prof": 8, "ac": 19, "attkBonus": 12, "dpr": range(213, 230), "saveDC": 21},
    26:  { "xp": 90000, "prof": 8, "ac": 19, "attkBonus": 12, "dpr": range(231, 248), "saveDC": 21},
    27: { "xp": 105000, "prof": 8, "ac": 19, "attkBonus": 13, "dpr": range(249, 266), "saveDC": 22},
    28: { "xp": 120000, "prof": 8, "ac": 19, "attkBonus": 13, "dpr": range(267, 284), "saveDC": 22},
    29: { "xp": 135000, "prof": 9, "ac": 19, "attkBonus": 13, "dpr": range(285, 302), "saveDC": 22},
    30: { "xp": 155000, "prof": 9, "ac": 19, "attkBonus": 14, "dpr": range(303, 320), "saveDC": 23},
}

xp_by_lvl = {
    1: { 'easy':   25, 'medium':   50, 'hard':   75, 'deadly':   100 },
    2: { 'easy':   50, 'medium':  100, 'hard':  150, 'deadly':   200 },
    3: { 'easy':   75, 'medium':  150, 'hard':  225, 'deadly':   400 },
    4: { 'easy':  125, 'medium':  250, 'hard':  375, 'deadly':   500 },
    5: { 'easy':  250, 'medium':  500, 'hard':  750, 'deadly':  1100 },
    6: { 'easy':  300, 'medium':  600, 'hard':  900, 'deadly':  1400 },
    7: { 'easy':  350, 'medium':  750, 'hard': 1100, 'deadly':  1700 },
    8: { 'easy':  450, 'medium':  900, 'hard': 1400, 'deadly':  2100 },
    9: { 'easy':  550, 'medium': 1100, 'hard': 1600, 'deadly':  2400 },
    10: { 'easy':  600, 'medium': 1200, 'hard': 1900, 'deadly':  2800 },
    11: { 'easy':  800, 'medium': 1600, 'hard': 2400, 'deadly':  3600 },
    12: { 'easy': 1000, 'medium': 2000, 'hard': 3000, 'deadly':  4500 },
    13: { 'easy': 1100, 'medium': 2200, 'hard': 3400, 'deadly':  5100 },
    14: { 'easy': 1250, 'medium': 2500, 'hard': 3800, 'deadly':  5700 },
    15: { 'easy': 1400, 'medium': 2800, 'hard': 4300, 'deadly':  6400 },
    16: { 'easy': 1600, 'medium': 3200, 'hard': 4800, 'deadly':  7200 },
    17: { 'easy': 2000, 'medium': 3900, 'hard': 5900, 'deadly':  8800 },
    18: { 'easy': 2100, 'medium': 4200, 'hard': 6300, 'deadly':  9500 },
    19: { 'easy': 2400, 'medium': 4900, 'hard': 7300, 'deadly': 10900 },
    20: { 'easy': 2800, 'medium': 5700, 'hard': 8500, 'deadly': 12700 },
    21: { 'easy': 3200, 'medium': 6400, 'hard': 9600, 'deadly': 14400 },
}

for lvl in xp_by_lvl:
    xp_by_lvl[lvl]['tpk'] = math.floor(xp_by_lvl[lvl]['deadly'] * 1.3)

healthBrackets = {
    6: 0,
    35: 0.125,
    49: 0.25,
    70: 0.5,
    85: 1,
    100: 2,
    115: 3,
    130: 4,
    145: 5,
    160: 6,
    175: 7,
    190: 8,
    205: 9,
    220: 10,
    235: 11,
    250: 12,
    265: 13,
    280: 14,
    295: 15,
    310: 16,
    325: 17,
    340: 18,
    355: 19,
    400: 20,
    445: 21,
    490: 22,
    535: 23,
    580: 24,
    625: 25,
    670: 26,
    715: 27,
    760: 28,
    805: 29,
    850: 30
}

class Ability(Enum):
    Strength = 0
    Str = 0
    Dexterity = 1
    Dex = 1
    Intelligence = 2
    Int = 2
    Wisdom = 3
    Wis = 3
    Charisma = 4
    Cha = 4

abilityNames = ['strength', 'dexterity', 'intelligence', 'wisdom', 'charisma', 'constitution']

skills =  {
    # Str
    "athletics": Ability.Str.value,
    # Dex
    "acrobatics": Ability.Dex.value,
    "sleight of hand": Ability.Dex.value,
    "stealth": Ability.Dex.value,
    # Int
    "arcana": Ability.Int.value,
    "history": Ability.Int.value,
    "investigation": Ability.Int.value,
    "nature": Ability.Int.value,
    "religion": Ability.Int.value,
    #Wis
    "animal handling": Ability.Wis.value,
    "insight": Ability.Wis.value,
    "medicine": Ability.Wis.value,
    "perception": Ability.Wis.value,
    "survival": Ability.Wis.value,
    # Cha
    "deception": Ability.Cha.value,
    "intimidation": Ability.Cha.value,
    "performance": Ability.Cha.value,
    "persuasion": Ability.Cha.value,
}
