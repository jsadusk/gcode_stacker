#!/usr/bin/env python3

import sys
import os
import re

with open(sys.argv[1], "r") as fh:
    first_model = fh.readlines()

with open(sys.argv[2], "r") as fh:
    other_model = fh.readlines()

stack_num = int(sys.argv[3])

start_marker = "; **** end of start.gcode ****\n"
end_marker = "; **** Replicator 2 end.gcode ****\n"
z_bump = 0.25

found = False
for (i, line) in enumerate(first_model):
    if line == end_marker:
        end_gcode = first_model[i:]
        first_piece = first_model[:i]
        found = True
        break
assert(found)

found = False
for i, line in enumerate(other_model):
    if line == start_marker:
        other_piece_start = i
        found = True
        break
assert(found)

found = False
for i, line in enumerate(other_model):
    if line == end_marker:
        other_piece_end = i
        found = True
        break
assert(found)

other_piece = other_model[other_piece_start:other_piece_end]

zmove_re = re.compile("^G1.*\sZ([0-9.]+)")

with open(sys.argv[4], "w") as fh:
    last_z = 0
    for line in first_piece:
        match = zmove_re.match(line)
        if match is not None:
            last_z = float(match.group(1))
        fh.write(line)

    last_model_z = last_z
    
    for i in range(1, stack_num):
        fh.write("; STACK MODEL {}\n".format(i))
        found_first_z = False
        for line in other_piece:
            match = zmove_re.match(line)
            if match is not None:
                old_z = float(match.group(1))
                if found_first_z:
                    new_z = old_z + last_model_z
                else:
                    new_z = old_z + last_model_z + z_bump
                    found_first_z = True
                    
                line = line.replace("Z{}".format(match.group(1)), "Z{:.5f}".format(new_z))
                last_z = new_z
                
            fh.write(line)
            
        last_model_z = last_z

    for line in end_gcode:
        fh.write(line)


