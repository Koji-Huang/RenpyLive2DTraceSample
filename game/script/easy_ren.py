"""renpy

init python:
"""

from math import sin
from random import randint

last_st = 0.0
saved_st = 0.0

def update_function(obj, st):

    common = obj.common
    motion = common.motions

    global saved_st, last_st
    if last_st > st:
        last_st = st - 0.01
    saved_st += st - last_st
    last_st = st

    attributes = tuple(obj.common.attributes)
    target = attributes[randint(0, len(attributes)-1)]
    if target == 'null': target = 'still'

    motion_data = motion[target].get((sin(saved_st) * 0.5 + 0.5) * motion[target].duration, 0, 0, 0)


    for k, v in motion_data.items():

        kind, key = k
        factor, value = v

        if kind == "PartOpacity":
            common.model.set_part_opacity(key, value)
        elif kind == "Parameter":
            obj.blend_parameter(name=key, value=value, weight=0.5, blend="Add")
        elif kind == "Model":
            obj.blend_parameter(name=key, value=value, weight=0.5, blend="Add")

    return 0.0