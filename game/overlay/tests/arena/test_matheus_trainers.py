"""Original Route 104 parties, no fake replacement or forced damage."""
import json
from test_stability import L,cmd,check,checks,tap
import lab
try:
    for trainer,expected in [('IVAN',3),('BILLY',2)]:
        cmd('boot');before=cmd('fixture-team',mons=['CHARIZARD:36','MUDKIP:25'])
        s=cmd('trainer',trainer=trainer);seen=set();classic_live=0
        check(trainer+' starts directly in arena',s['arena']['active'] and s['intro']['skipped']==1)
        for _ in range(1800):
            if s['arena']['active']:
                # Index, not species: Ivan uses three different Magikarp.
                seen.add(int.from_bytes(L.read('gBattlerPartyIndexes',4)[2:4],'little'))
                x,y=s['arena']['x'][0],s['arena']['y'][0]
                dx=s['arena']['x'][1]-x;dy=s['arena']['y'][1]-y
                if x>62 and y>110:keys='LEFT'
                elif dx*dx+dy*dy<90*90:keys='A'
                else:keys=('RIGHT' if dx>8 else 'LEFT' if dx< -8 else '')+('+' if abs(dx)>8 and abs(dy)>8 else '')+('DOWN' if dy>8 else 'UP' if dy< -8 else '')
                s=cmd('hold',keys=keys or 'A',frames=6);classic_live=0
            else:
                if s['battle_main']=='HandleTurnActionSelectionState' and s['battlers'][1]['hp']:
                    classic_live+=6
                    assert classic_live<180,'live opponent trapped in native selection'
                # Advance native victory dialogue only after all party entries.
                s=tap('A',3) if len(seen)==expected and s['battlers'][1]['hp']==0 else cmd('wait',frames=6)
            if s['cb2']=='CB2_Overworld' and not s['field_locked']:break
        print(json.dumps(dict(trainer=trainer,seen=list(seen),status=s)),flush=True)
        cmd('screenshot',name='six-trainer-'+trainer.lower())
        check(trainer+' all original party members enter arena',len(seen)==expected)
        check(trainer+' wins and releases field',s['cb2']=='CB2_Overworld' and s['battle_outcome']==1 and not s['field_locked'])
        check(trainer+' retains native XP',s['party'][0]['exp']>before['party'][0]['exp'])
        cmd('save',name='six-'+trainer.lower());loaded=cmd('boot',save='six-'+trainer.lower())
        check(trainer+' save reload keeps party',loaded['party']==s['party'])
finally:
    (lab.WORK/'results/matheus-trainers.json').write_text(json.dumps(dict(checks=checks,rom_sha256=getattr(L,'sha',None)),indent=2)+'\n')
    if L.runner:L.raw('quit',reply=False);L.runner.wait(timeout=5)
