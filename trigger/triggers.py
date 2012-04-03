#!/usr/bin/env python

from rootpy.io import openFile
from rootpy.tree import Tree
from prettytable import PrettyTable

f = openFile("user.NoelDawe.001204._00001.VBFH130hh.root")
tree = f.Get("VBFH130hh")

total = tree.GetEntries()

"""
triggers = tree.glob("EF_*")

trigger_table = []

for trigger in triggers:
    accept = 100. * tree.GetEntries(trigger) / float(total)
    trigger_table.append((trigger, accept))

trigger_table.sort(reverse=True, key=lambda e: e[1])

table = PrettyTable(["Trigger", "Acceptance"])
for trigger, accept in trigger_table:
    table.add_row([trigger, "%.1f%%" % accept])
print table
"""

accept = tree.GetEntries("EF_tau29_medium1_tau20_medium1 || EF_e20_medium || EF_e60_loose || EF_xe60_noMu")

print accept / float(total)
