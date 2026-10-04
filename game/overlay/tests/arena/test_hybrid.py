#!/usr/bin/env python3
"""Current arena -> native party -> arena contract; SELECT is no longer classic."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/arena'))
from lab import call,WORK
checks=[]
def cmd(action,**kw):
    r=call(dict(action=action,**kw));assert r['ok'],r
    return r['result']
def check(name,ok):
    assert ok,name
    checks.append(name);print('PASS '+name,flush=True)
def tap(key,n=30):
    cmd('press',keys=key,frames=3);return cmd('wait',frames=n)
def main():
    cmd('boot');field=cmd('fixture-team',mons=['TREECKO:20','MUDKIP:20'])
    start=cmd('battle',species='POOCHYENA',level=12,classic=False)
    import test_result_flow as flow
    flow.cmd=cmd
    s=cmd('hold',keys='LEFT',frames=44)
    for _ in range(500):
        dx=s['arena']['x'][1]-s['arena']['x'][0];dy=s['arena']['y'][1]-s['arena']['y'][0]
        keys='A' if dx*dx+dy*dy<27*27 else '+'.join(([('RIGHT' if dx>0 else 'LEFT')] if abs(dx)>5 else [])+([('DOWN' if dy>0 else 'UP')] if abs(dy)>5 else []))
        s=cmd('hold',keys=keys or 'A',frames=3)
        if s['arena']['hits'][0]:break
    check('real attack damages native opponent',0<s['battlers'][1]['hp']<start['battlers'][1]['hp'])
    frozen=tap('START',4);check('pause settled',frozen['arena']['paused'])
    menu=tap('SELECT',180)
    check('SELECT opens native party, not legacy Fight',menu['cb2']=='CB2_UpdatePartyMenu')
    check('handoff preserves battlers exactly',menu['battlers']==frozen['battlers'])
    check('handoff does not fabricate XP',menu['party'][0]['exp']==field['party'][0]['exp'])
    returned=tap('B',1)
    for _ in range(120):
        if returned['arena']['active']:break
        returned=cmd('wait',frames=3)
    check('cancel returns to same real-time encounter',returned['arena']['active'])
    check('cancel preserves damage and PP',returned['battlers'][1]['hp']==frozen['battlers'][1]['hp'] and returned['party'][0]['pp']==frozen['party'][0]['pp'])
    flow.knock_out();settled,_,_=flow.settle()
    check('victory restores overworld',settled['cb2']=='CB2_Overworld' and not settled['field_locked'])
    cmd('save',name='hybrid-current-contract');loaded=cmd('boot',save='hybrid-current-contract')
    check('save and cold boot preserve progress',loaded['party']==settled['party'])
    (WORK/'results/hybrid.json').write_text(json.dumps(dict(ok=True,checks=checks,rom_sha256=start['rom_sha256']),indent=2)+'\n')
if __name__=='__main__':main()
