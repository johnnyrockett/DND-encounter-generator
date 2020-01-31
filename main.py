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

state = None

def subject_completer(prefix, parsed_args, **kwargs):
    if parsed_args.cmd == 'new':
        return ['encounter', 'monster']
    elif parsed_args.cmd not in ['help', 'quit'] and state:
        if len(parsed_args.subargs) == 0:
            return [mon._name for mon in state._monsters]
        elif parsed_args.cmd == 'check':
            return ['attack', 'hit', 'ac', 'dc'] + list(skills.keys())

def size_completer(prefix, parsed_args, **kwargs):
    return [size.name for size in Monster.MonsterSize]

def difficulty_completer(prefix, parsed_args, **kwargs):
    return [diff.name for diff in Encounter.EncounterDifficulty]

cmdParser = argparse.ArgumentParser(prog='PROG', description='DND encounter interface')
cmdParser.add_argument('cmd', choices=['new','damage','heal','check','remove', 'help', 'quit'])
cmdParser.add_argument('subargs', nargs='*').completer = subject_completer
cmdParser.add_argument('-n', '--name', required=False)
cmdParser.add_argument('-l', '--level', type=int, required=False)
cmdParser.add_argument('-s', '--size', required=False).completer = size_completer
cmdParser.add_argument('-hp', '--health', type=int, required=False)
cmdParser.add_argument('-d', '--difficulty', required=False).completer = difficulty_completer

completer = argcomplete.CompletionFinder(cmdParser)
readline.set_completer_delims("")
readline.set_completer(completer.rl_complete)
readline.parse_and_bind("tab: complete")

while True:
    cmdParser._get_args
    if state:
        astr = input(str(state) + "\n> ")
    else:
        astr = input('> ')

    try:
        args, remaining = cmdParser.parse_known_args(astr.split())
    except SystemExit:
        # trap argparse error message
        print('error')
        continue
    if args.cmd == 'new' and len(args.subargs) >= 1:
        if args.subargs[0] == 'encounter':
            state = Encounter(difficulty=args.difficulty)
        elif args.subargs[0] == 'monster':
            if not state:
                state = Encounter(populate=False)
            state.addMonster(Monster(name=args.name, size=args.size, health=args.health, level=args.level if args.level else player_level))
    elif args.cmd == 'damage' and state and len(args.subargs) == 2:
        mon = state.getMonster(args.subargs[0])
        if mon and args.subargs[1].isdigit():
            mon.damage(int(args.subargs[1]))
    elif args.cmd == 'heal' and state and len(args.subargs) == 2:
        mon = state.getMonster(args.subargs[0])
        if mon and args.subargs[1].isdigit():
            mon.damage(-1*int(args.subargs[1]))
    elif args.cmd == 'remove' and state and len(args.subargs) == 1:
        state.removeMonster(args.subargs[0])
    elif args.cmd == 'check' and state and len(args.subargs) == 2:
        mon = state.getMonster(args.subargs[0])
        if mon:
            # "stats" print out all stored stats for mon
            if args.subargs[1] == 'attack' or args.subargs[1] == 'hit':
                print(mon._name + ' rolls {roll} to hit'.format(roll=random.randint(1, 20) + mon._attkBonus))
            elif args.subargs[1] == 'ac':
                print(mon._name + ' has an armor class of ' + str(mon._ac))
            elif args.subargs[1] == 'dc':
                print(mon._name + ' has a save DC of ' + str(mon._saveDC))
            elif args.subargs[1] == 'stats':
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(mon.__dict__)
            elif args.subargs[1] in skills:
                a = Ability(skills[args.subargs[1]])
                print(mon._name + ' rolled a ' + str(mon.checkAbility(str.lower(a.name))))

    elif args.cmd == 'help':
        cmdParser.print_help()
    elif args.cmd == 'quit':
        exit(0)
    else:
        cmdParser.error("I didn't understand that")