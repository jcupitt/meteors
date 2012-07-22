# enums courtesy of stackoverflow
# http://stackoverflow.com/questions/36932/whats-the-best-way-to-implement-an-enum-in-python
# modified to skip 0 (to avoid being evaluated as false)
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(1, len(sequential) + 1)), **named)
    return type('Enum', (), enums)

# some global enumerations to avoid typos/comparing strings
TURN = enum('left', 'right')
THRUST = enum('forward', 'back')
STATE = enum('start', 'play', 'game_over', 'level')
