#!/usr/bin/env python3
"""Exhaust genuine Teleport PP; use virtual Struggle without leaving arena."""
import json
from test_stability import L,cmd,check,checks
import lab
try:
    cmd('boot');cmd('fixture-team',mons=['ABRA:100'])
    s=cmd('battle',species='POOCHYENA',level=3,classic=False)
    check('Teleport-only set enters arena',s['arena']['active'])
    cmd('press',keys='R',frames=1)
    cmd('wait',frames=1)
    for _ in range(700):
        s=cmd('hold',keys='A',frames=12)
        if not s['party'][0]['pp'][0]:break
    check('all 20 Teleport PP spent through real input',s['party'][0]['pp'][0]==0 and s['party'][0]['hp']>0)
    s=cmd('wait',frames=200)
    check('exhaustion stays in real-time arena',s['arena']['active'])
    moves=s['party'][0]['moves']
    for _ in range(400):
        dx=s['arena']['x'][1]-s['arena']['x'][0];dy=s['arena']['y'][1]-s['arena']['y'][0]
        keys='A' if dx*dx+dy*dy<28*28 else '+'.join(([('RIGHT' if dx>0 else 'LEFT')] if abs(dx)>5 else [])+([('DOWN' if dy>0 else 'UP')] if abs(dy)>5 else []))
        s=cmd('hold',keys=keys or 'A',frames=4)
        if s['battlers'][1]['hp']<s['battlers'][1]['max_hp']:break
    check('virtual Struggle deals real damage',s['battlers'][1]['hp']<s['battlers'][1]['max_hp'])
    check('native exhausted PP and moves are preserved',s['party'][0]['pp'][0]==0 and s['party'][0]['moves']==moves)
    cmd('screenshot',name='six-pp-struggle')
finally:
    (lab.WORK/'results/stability-pp.json').write_text(json.dumps(dict(checks=checks,rom_sha256=getattr(L,'sha',None)),indent=2)+'\n')
    if L.runner:L.raw('quit',reply=False);L.runner.wait(timeout=5)
