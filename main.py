import argcomplete, argparse, readline

from monster_maker import Encounter, Monster, player_level, players

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
        return [mon._name for mon in state._monsters]

cmdParser = argparse.ArgumentParser(prog='PROG', description='DND encounter interface')
cmdParser.add_argument('cmd', choices=['new','damage','heal','check','remove', 'help', 'quit'])
cmdParser.add_argument('subargs', nargs='*').completer = subject_completer

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
            state = Encounter()
        elif args.subargs[0] == 'monster':
            if not state:
                state = Encounter(populate=False)
            state.addMonster(Monster(player_level))
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
    elif args.cmd == 'help':
        cmdParser.print_help()
    elif args.cmd == 'quit':
        exit(0)
    else:
        cmdParser.error("I didn't understand that")