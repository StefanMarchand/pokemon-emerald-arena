"""Native Bide stores received HP and returns exactly double via real input."""
import json
from test_stability import L,cmd,check,checks,tap
import lab
try:
    cmd('boot');cmd('fixture-team',mons=['MUDKIP:20'])
    s=cmd('battle',species='ZIGZAGOON',level=7,classic=False)
    check('Bide set enters arena',s['arena']['active'])
    for _ in range(5):
        if s['battlers'][0]['moves'][s['arena']['move_slot']]==117:break
        s=tap('R',1)
    check('Bide selected from native set',s['battlers'][0]['moves'][s['arena']['move_slot']]==117)
    s=cmd('hold',keys='LEFT',frames=45)
    for _ in range(300):
        dx=s['arena']['x'][1]-s['arena']['x'][0];dy=s['arena']['y'][1]-s['arena']['y'][0]
        if dx*dx+dy*dy<27*27:break
        keys=('+'.join(([('RIGHT' if dx>0 else 'LEFT')] if abs(dx)>5 else [])+([('DOWN' if dy>0 else 'UP')] if abs(dy)>5 else [])))
        s=cmd('hold',keys=keys or 'A',frames=4)
    pp=s['party'][0]['pp'][:];hp=s['battlers'][1]['hp'];stored=0
    s=cmd('hold',keys='A',frames=20)
    paused=tap('START',1);same=cmd('wait',frames=90)
    check('pause freezes Bide charge and attacks',paused['arena']==same['arena'] and paused['battlers']==same['battlers'])
    tap('START',1)
    for _ in range(80):
        stored=max(stored,int.from_bytes(L.read('sBideDamage',2),'little'))
        s=cmd('wait',frames=3)
        if s['battlers'][1]['hp']<hp:break
    check('Bide actually received damage',stored>0)
    check('Bide returns twice stored HP',hp-s['battlers'][1]['hp']==min(hp,stored*2))
    check('Bide consumes one native PP',sum(pp)-sum(s['party'][0]['pp'])==1)
    cmd('screenshot',name='six-bide')
finally:
    (lab.WORK/'results/matheus-bide.json').write_text(json.dumps(dict(checks=checks,rom_sha256=getattr(L,'sha',None)),indent=2)+'\n')
    if L.runner:L.raw('quit',reply=False);L.runner.wait(timeout=5)
