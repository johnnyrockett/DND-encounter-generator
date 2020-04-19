# DND-encounter-generator

## TL;DR

pip install -r requirements.txt

For CLI:

```cmd
python cli.py
> new encounter
```

For GUI:

```cmd
python gui.py
```

## Summary

This project is intended to virtualize encounters within DND. There are two parts to this project: an encounter generator that generates realistic random dnd enemies with fully formed stats, and a graphical way to represent these enemies and simulate their turns as they attack players.

## Pathing Equation

### Metrics

```python
monsterHealth = (averageHealth / thisHealth)*-1 + 1
threat = damageDealt / maxHealth * 0.35
playerHealth =  avgPlayerHealth / currentHealth
speed = 30 / monsterSpeed
pathDifficulty = -1 * len(path)
```

### Final Equation

```python
static = monsterHealth + threat + playerHealth + speed
dynamic = speed * pathDifficulty
value = static + dynamic
```

## Commands

### GUI Commands

Run all unit tests in 'maps' directory to ensure desired monster behavior in different scenarios

```cmd
python gui.py test
```

Launch flask server with initial map state indicated from 'maps/exampleMap.json'

```cmd
python gui.py exampleMap.json
```

Launch flask server with no starting map.

```cmd
python gui.py
```

### CLI Commands

* new
  * encounter: Create a new encounter
  * monster: Create new monster. If an encounter has already been created, add monster to encounter.
* damage: "damage Greg 14"
  * damage a creature by referring to their name
* check
* remove
* help
* quit
