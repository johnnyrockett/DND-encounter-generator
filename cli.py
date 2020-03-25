import argcomplete, argparse, readline
import random
import pprint

from monster_maker import Encounter, Monster, player_level, players, skills, Ability

# Requirements:
# 1. Start encounter with options
# 1. Kill monsters
# 1. Do damage to monsters
# 1. Add in monsters with options
# 1. Have monsters make checks/saves
# 1. Make monsers roll to attack


def subject_completer(prefix, parsed_args, **kwargs):
    if parsed_args.cmd == 'new':
        return ['encounter', 'monster']
    elif parsed_args.cmd not in ['help', 'quit'] and self.state:
        if len(parsed_args.subargs) == 0:
            return [mon._name for mon in self.state._monsters]
        elif parsed_args.cmd == 'check':
            return ['attack', 'hit', 'ac', 'dc', 'damage'] + list(skills.keys())

def size_completer(prefix, parsed_args, **kwargs):
    return [size.name for size in Monster.MonsterSize]

def difficulty_completer(prefix, parsed_args, **kwargs):
    return [diff.name for diff in Encounter.EncounterDifficulty]

class CLI:

    def __init__(self):
        self.state = None

        self.cmdParser = argparse.ArgumentParser(prog='PROG', description='DND encounter interface')
        self.cmdParser.add_argument('cmd', choices=['new','damage','heal','check','remove', 'help', 'quit'])
        self.cmdParser.add_argument('subargs', nargs='*').completer = subject_completer
        self.cmdParser.add_argument('-n', '--name', required=False)
        self.cmdParser.add_argument('-l', '--level', type=int, required=False)
        self.cmdParser.add_argument('-s', '--size', required=False).completer = size_completer
        self.cmdParser.add_argument('-hp', '--health', type=int, required=False)
        self.cmdParser.add_argument('-d', '--difficulty', required=False).completer = difficulty_completer

        completer = argcomplete.CompletionFinder(self.cmdParser)
        readline.set_completer_delims("")
        readline.set_completer(completer.rl_complete)
        readline.parse_and_bind("tab: complete")


    def query(self, text):
        try:
            args, remaining = self.cmdParser.parse_known_args(text.split())
        except SystemExit:
            # trap argparse error message
            return 'error parsing "' + text + '"'
        if args.cmd == 'new' and len(args.subargs) >= 1:
            if args.subargs[0] == 'encounter':
                self.state = Encounter(difficulty=args.difficulty)
            elif args.subargs[0] == 'monster':
                if not self.state:
                    self.state = Encounter(populate=False)
                self.state.addMonster(Monster(name=args.name, size=args.size, health=args.health, level=args.level if args.level else player_level))
        elif args.cmd == 'damage' and self.state and len(args.subargs) == 2:
            mon = self.state.getMonster(args.subargs[0])
            if mon and args.subargs[1].isdigit():
                mon.damage(int(args.subargs[1]))
        elif args.cmd == 'heal' and self.state and len(args.subargs) == 2:
            mon = self.state.getMonster(args.subargs[0])
            if mon and args.subargs[1].isdigit():
                mon.damage(-1*int(args.subargs[1]))
        elif args.cmd == 'remove' and self.state and len(args.subargs) == 1:
            self.state.removeMonster(args.subargs[0])
        elif args.cmd == 'check' and self.state and len(args.subargs) == 2:
            mon = self.state.getMonster(args.subargs[0])
            if mon:
                # "stats" print out all stored stats for mon
                if args.subargs[1] == 'attack' or args.subargs[1] == 'hit':
                    roll = random.randint(1, 20)
                    print(mon._name + ' rolls {crit}{roll} to hit'.format(roll=roll + mon._attkBonus, crit='a NATURAL 20 for ' if roll == 20 else ''))
                elif args.subargs[1] == 'ac':
                    print(mon._name + ' has an armor class of ' + str(mon._ac))
                elif args.subargs[1] == 'dc':
                    print(mon._name + ' has a save DC of ' + str(mon._saveDC))
                elif args.subargs[1] == 'stats':
                    pp = pprint.PrettyPrinter(indent=4)
                    pp.pprint(mon.__dict__)
                elif args.subargs[1] == 'damage':
                    print(mon._name + ' deals {damage} damage'.format(damage=random.randint(mon._dpr[0], mon._dpr[1])))
                elif args.subargs[1] in skills:
                    a = Ability(skills[args.subargs[1]])
                    print(mon._name + ' rolled a ' + str(mon.checkAbility(str.lower(a.name))))

        elif args.cmd == 'help':
            cmdParser.print_help()
        elif args.cmd == 'quit':
            return 1
        else:
            cmdParser.error("I didn't understand that")
        return 0

if __name__ == "__main__":
    cli = CLI()
    while True:
        # cmdParser._get_args
        if cli.state:
            astr = input(str(cli.state) + "\n> ")
        else:
            astr = input('> ')

        rc = cli.query(astr)
        if rc == 1:
            break
        elif type(rc) is str:
            print(rc)