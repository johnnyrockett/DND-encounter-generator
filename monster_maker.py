from numpy import random

from enum import Enum
from tables import *

players = 5
player_level = 3

f = open('names.txt', 'r')
names = f.readlines()
f.close()

# four heroes of a level equal to the creature’s Challenge Rating should exhaust roughly one-quarter of their resources battling it

# Ok, my algorithm will be to pick a random encounter difficulty using a normal distribution. I then calculate how much xp that would give.
# Using that xp cap, I create a group of monster's whose xp sum is that amount.
# The biggest problem here is being able to calculate the cr of my custom monsters.
# I'll determine CR by the hit point intervals
# I can also use hit points to determine AC, proficiency, etc
# Then, all I need is a nice algorithm for varying the party sizes.
# Ideally I'd be able to make a monster from CR, but size varies how good they really are too much.

# Encounter seems to be working well, but there should be some predefined metric for encounter size
# Maybe it keeps replacing the weakest of the monsters with higher level ones

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[31m'
    BRIGHT_RED = '\033[91m'
    MAGENTA = '\033[95m'
    BLINK = '\033[5m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Monster:

    class MonsterSize(Enum):
        Tiny = 0
        Small = 1
        Medium = 2
        Large = 3
        Huge = 4
        Gargantuan = 5

    hitDieMap = { MonsterSize.Tiny: 4, MonsterSize.Small: 6, MonsterSize.Medium: 8, MonsterSize.Large: 10, MonsterSize.Huge: 12, MonsterSize.Gargantuan: 20 }

    def __init__(self, level=None, size=None, health=None, name=None):

        # Monster's name
        if name is None:
            self._name = names[random.randint(0, len(names))][:-1]

        # Monster's level
        if level is None:
            self._level = random.randint(1, 20)
        else:
            self._level = level

        # Monster's size (effects hp)
        if size is None:
            rVal = round(random.normal(2, 0.75, 1)[0])
            self._size = self.MonsterSize(max(0, min(5, rVal)))
        else:
            self._size = size
            # distribution = {}
            # for size in rSize:
            #     result = Monster.MonsterSize(max(0, min(5, round(size))))
            #     if result not in distribution:
            #         distribution[result] = 1
            #     else:
            #         distribution[result] += 1

            # for key, val in distribution.items():
            #     print(key.name + ": " + str(val))

        # Monster's health
        if health is None:
            hitdie = self.hitDieMap[self._size]
            conmod = random.randint(-1, 4)
            self._max_health = hitdie
            for i in range(1, level):
                self._max_health += random.randint(0, hitdie) + conmod
            self._current_health = self._max_health
        else:
            self._max_health = self._current_health = health

        for health_cap in healthBrackets:
            if self._max_health < health_cap:
                self._cr = healthBrackets[health_cap]
                break

        stats = stats_by_cr[self._cr]
        for name, val in stats.items():
            setattr(self, "_" + name, val)

    def damage(self, amount):
        self._current_health = max(self._current_health - amount, 0)

    def __str__(self):
        s = "{bold}{name}{endc} {size}(lv{lvl}-cr{cr}): {current_health}/{max_health}".format(
            bold=bcolors.BOLD,
            name=self._name,
            endc=bcolors.ENDC,
            size=self._size.name,
            lvl=self._level,
            cr=self._cr,
            current_health=self._current_health,
            max_health=self._max_health)
        if self._current_health > 0:
            p = self._current_health/self._max_health
            s += " [{filled}{empty}]".format(
                filled='#' * round(p * 40),
                empty='-' * round((1-p) * 40))
        else:
            s += " dropped {xp} xp".format(xp=self._xp)
        return s


class Encounter:

    class EncounterDifficulty(Enum):
        easy = 0
        medium = 1
        hard = 2
        deadly = 3
        tpk = 4

        @classmethod
        def colorify(cls, diff):
            if diff == cls.easy:
                c = bcolors.GREEN
            elif diff == cls.medium:
                c = bcolors.YELLOW
            elif diff == cls.hard:
                c = bcolors.BRIGHT_RED
            elif diff == cls.deadly:
                c = bcolors.RED + bcolors.BOLD
            elif diff == cls.tpk:
                c = bcolors.MAGENTA + bcolors.BLINK
            return c + diff.name + bcolors.ENDC

    # EncounterDifficulty = Enum(value=diff_list)

    def __init__(self, difficulty=None, populate=True):
        if populate:
            self.populate(difficulty)

    def populate(self, difficulty=None):
        if difficulty is not None and isinstance(difficulty, str) and difficulty in self.EncounterDifficulty:
            self._difficulty = getattr(self.EncounterDifficulty, difficulty)
        else:
            difficulty = round(random.gamma(1.9, 0.6))
            self._difficulty = self.EncounterDifficulty((int)(max(0, min(4, difficulty))))

        target_xp = xp_by_lvl[player_level][self._difficulty.name] * (players / 4)

        self._monsters = []
        while self.calcMonsterXP() < target_xp:
            mon = Monster((int)(round(random.normal(player_level+2, 2, 1)[0])))
            self._monsters.append(mon)

    def calcMonsterXP(self):
        self._xp = 0
        for mon in self._monsters:
            self._xp += mon._xp

        multiplier = ((len(self._monsters) - 1) * 0.2) + 1
        self._xp *= multiplier
        self._xp = int(round(self._xp))

        return self._xp

    def calcDifficulty(self):
        xp_diff = 99999999
        closest_diff = ""
        for difficulty, xp_cap in xp_by_lvl[player_level].items():
            temp_xp_diff = abs((xp_cap * (players / 4)) - self._xp)
            if temp_xp_diff < xp_diff:
                xp_diff = temp_xp_diff
                closest_diff = difficulty

        self._difficulty = getattr(self.EncounterDifficulty,closest_diff)

    def addMonster(self, mon):
        if not hasattr(self, '_monsters'):
            self._monsters = []
        self._monsters.append(mon)
        self.calcMonsterXP()
        self.calcDifficulty()

    def removeMonster(self, i):
        self._monsters.remove(i)
        self.calcMonsterXP()

    def getMonster(self, name):
        for mon in self._monsters:
            if mon._name == name:
                return mon
        return None

    def __str__(self):
        if hasattr(self, "_difficulty"):
            s = "Difficulty: {diff} for {xp} xp".format(diff=self.EncounterDifficulty.colorify(self._difficulty), xp=self._xp)
            for i in range(len(self._monsters)):
                s += "\n    " + str(self._monsters[i])
        else:
            s = "Encounter not populated"
        return s


# enc = Encounter()
# print(enc)