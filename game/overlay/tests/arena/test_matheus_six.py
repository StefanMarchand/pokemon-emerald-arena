#!/usr/bin/env python3
"""Real input gates for Matheus's six requested improvements."""
import json
from test_stability import L,cmd,check,checks,tap,until
import lab

def main():
    cmd('boot');cmd('fixture-team',mons=['CHARIZARD:36','MUDKIP:25'])
    s=cmd('battle',species='MAGIKARP',level=5,classic=False)
    check('Magikarp Splash set enters arena',s['arena']['active'])
    check('native intro skipped',s['intro']['skipped']==1)
    tap('START');before=cmd('status');cmd('screenshot',name='six-pause-root')
    s=cmd('wait',frames=120)
    check('root menu freezes battle',before['arena']['frames']==s['arena']['frames'] and before['battlers']==s['battlers'])
    tap('A',180)
    check('START Pokemon opens native team',cmd('status')['cb2']=='CB2_UpdatePartyMenu')
    tap('B',180)
    check('cancel team returns to arena',cmd('status')['arena']['active'])
    tap('START');tap('DOWN');tap('A',180)
    check('START Bag opens native bag','Bag' in cmd('status')['cb2'])
    tap('B',180)
    check('cancel bag returns to arena',cmd('status')['arena']['active'])
    tap('START');tap('DOWN');tap('DOWN');tap('A')
    cmd('screenshot',name='six-moves')
    check('view moves stays paused',cmd('status')['arena']['paused'])
    tap('B');tap('B')
    check('back from moves then root resumes',not cmd('status')['arena']['paused'])
    tap('START');tap('A',180);tap('DOWN');tap('A');tap('A',0)
    s=until(lambda s:s['arena']['active'])
    check('voluntary switch returns to real time',s['battlers'][0]['species']==L.species_id('MUDKIP'))
    cmd('boot');cmd('fixture-team',mons=['MAGIKARP:10'])
    s=cmd('battle',species='MAGIKARP',level=5,classic=False)
    check('both status-only opponents get arena fallback',s['arena']['active'])
    pp=s['party'][0]['pp'];moves=s['party'][0]['moves']
    # Pursue using ordinary movement, no HP/PP writes.
    for _ in range(240):
        if not s['arena']['active']:break
        dx=s['arena']['x'][1]-s['arena']['x'][0];dy=s['arena']['y'][1]-s['arena']['y'][0]
        keys=['A']
        if dx*dx+dy*dy>30*30:
            keys=[]
            if abs(dx)>5:keys.append('RIGHT' if dx>0 else 'LEFT')
            if abs(dy)>5:keys.append('DOWN' if dy>0 else 'UP')
        s=cmd('hold',keys='+'.join(keys) or 'A',frames=4)
        if s['arena']['hits'][0]:break
    check('Struggle deals actual native damage',s['arena']['hits'][0]>0)
    check('fallback does not overwrite moves or PP',s['party'][0]['pp']==pp and s['party'][0]['moves']==moves)
    cmd('screenshot',name='six-struggle')

if __name__=='__main__':
    try:main()
    finally:
        (lab.WORK/'results/matheus-six.json').write_text(json.dumps(dict(checks=checks,rom_sha256=getattr(L,'sha',None)),indent=2)+'\n')
        if L.runner:L.raw('quit',reply=False);L.runner.wait(timeout=5)
