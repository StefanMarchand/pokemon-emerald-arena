#!/usr/bin/env python3
"""Real ROM capture acceptance. Fixtures only prepare native field inventory/team.
All throws, misses, escapes and catches are timed GBA inputs. No forced RNG/HP.
"""
import json
import struct
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/arena'))
from lab import call,WORK
checks=[]
def cmd(action,**kw):
    r=call(dict(action=action,**kw));assert r['ok'],r
    return r['result']
def check(name,yes):
    assert yes,name
    checks.append(name);print('PASS '+name,flush=True)
def fresh(balls=30,team=None):
    cmd('boot');cmd('view',speed=0)
    cmd('fixture-team',mons=team or ['CHARIZARD:50'])
    cmd('fixture-balls',count=balls)
def battle(species='POOCHYENA',level=3):
    cmd('battle',species=species,level=level,classic=False)
    return cmd('wait',frames=16)
def aim():
    cmd('hold',keys='L+R',frames=12)
    return cmd('status')
def settle():
    for _ in range(180):
        s=cmd('wait',frames=3)
        if s['cb2']=='CB2_Overworld' and not s['field_locked']:return s
        if s['capture']['state']==0:return s
    raise AssertionError('Capture state never settled')
def catch():
    for _ in range(24):
        s=aim()
        assert s['capture']['state']==1,s['capture']
        s=cmd('wait',frames=1)
        assert s['capture']['state']==2
        count=s['capture']['balls'];party=len(s['party'])
        for _ in range(40):
            s=cmd('wait',frames=1)
            if s['capture']['state']!=2:break
            assert -16<=s['capture']['ball_y']<=160,'Arc overflow'
            assert 0<=s['capture']['ball_x']<=240,'Horizontal overflow'
        if s['capture']['state']==3:
            before=s['battlers']
            # Do not press A+B+START+SELECT: that's Emerald's native soft reset.
            s=cmd('press',keys='A+B+L+R',frames=3)
            s=cmd('press',keys='START+SELECT',frames=3)
            assert s['battlers']==before,'Capture lock changed HP/PP/stats'
            assert s['capture']['balls']==count,'Capture lock consumed twice'
            assert len(s['party'])==party,'Reward granted before shakes'
        s=settle()
        if s['capture']['caught']:
            assert s['cb2']=='CB2_Overworld'
            return s
        assert s['arena']['active'] and s['battlers'][1]['hp']>0
    raise AssertionError('No native catch in 24 attempts')
def main():
    fresh(balls=1);start=battle();original=start['party']
    s=aim();check('L+R enters aim without consuming PP/balls',s['capture']['state']==1 and s['capture']['balls']==1 and s['party']==original)
    s=cmd('hold',keys='B+L+R',frames=3)
    check('B cancels freely',s['capture']['cancelled']==1 and s['capture']['throws']==0 and s['capture']['balls']==1)
    s=cmd('hold',keys='L+R',frames=12)
    check('Holding shoulders after cancel does not rearm or spend',s['capture']['state']==0 and s['capture']['throws']==0 and s['capture']['balls']==1)
    cmd('wait',frames=3);aim()
    s=cmd('hold',keys='L+R+LEFT+DOWN',frames=100)
    check('Manual aim stays inside arena',s['capture']['aim_x']==12 and s['capture']['aim_y']==143)
    s=cmd('wait',frames=25)
    check('Deliberate miss consumes exactly one ball',s['capture']['misses']==1 and s['capture']['throws']==1 and s['capture']['balls']==0)
    s=settle();cmd('hold',keys='L+R',frames=12);s=cmd('wait',frames=10)
    check('Empty bag blocks throw, battle remains playable',s['capture']['empty']==1 and s['capture']['throws']==1 and s['arena']['active'])
    cmd('screenshot',name='capture-no-balls')
    cmd('press',keys='SELECT',frames=3);s=cmd('wait',frames=130)
    check('Party menu remains available after capture miss',not s['arena']['active'] and s['cb2']=='CB2_UpdatePartyMenu')
    fresh();start=battle();s=catch();c=s['capture']
    check('Native capture joins party exactly once',len(s['party'])==2 and c['caught']==1 and s['party'][1]['species']==286)
    check('Capture preserves caught HP and checksum',s['party'][1]['hp']==c['hp'] and all(p['checksum_ok'] for p in s['party']))
    check('Capture gives no invented experience/EVs',s['party'][0]['exp']==start['party'][0]['exp'] and s['party'][0]['evs']==start['party'][0]['evs'])
    check('Every throw consumes one native ball',c['balls']==30-c['throws'] and c['throws']==c['hits']+c['misses'])
    audit=cmd('audit-capture',species='POOCHYENA')
    check('Native dex, capture statistic and inventory updated',audit['caught']==1 and audit['seen']==1 and audit['captures']==1 and audit['balls']==c['balls'])
    cmd('save',name='capture-party');loaded=cmd('boot',save='capture-party')
    check('Caught party survives native save/cold boot',loaded['party']==s['party'])
    check('Dex, stats and ball stock survive cold boot',cmd('audit-capture',species='POOCHYENA')==audit)
    # Full party routes through Emerald GiveMonToPlayer -> CopyMonToPC.
    fresh(team=['CHARIZARD:50','BLASTOISE:36','TREECKO:11','EEVEE:25','SCIZOR:15','DRAGONITE:30'])
    start=battle();s=catch();audit=cmd('audit-capture',species='POOCHYENA')
    check('Full party sends native captured mon to PC',len(s['party'])==6 and s['capture']['destination']==1 and audit['stored']==1 and audit['pc_location']==1)
    check('PC mon has correct level/ball, no bad egg',audit['level']==3 and audit['ball']==4 and audit['bad_egg']==0)
    cmd('save',name='capture-pc');cmd('boot',save='capture-pc')
    check('PC capture persists across cold boot',cmd('audit-capture',species='POOCHYENA')==audit)
    cmd('fixture-storage-full',confirm='replace-disposable-boxes');s=battle();aim();s=cmd('wait',frames=10)
    check('All storage full rejects before spending a ball',s['capture']['full']==1 and s['capture']['throws']==0 and s['capture']['balls']==audit['balls'])
    cmd('screenshot',name='capture-storage-full')
    # Low catch rate produces genuine native escapes, not a lab-forced branch.
    fresh();start=battle('EEVEE',25)
    for _ in range(10):
        aim();cmd('wait',frames=1);s=settle()
        if s['capture']['escaped']:break
        if s['capture']['caught']:raise AssertionError('Unexpected seed: need escape coverage')
    check('Breakout returns to battle with same wild HP',s['capture']['escaped']>0 and s['battlers'][1]['hp']==start['battlers'][1]['hp'] and len(s['party'])==1)
    check('Breakout does not invent XP or EVs',s['party'][0]['exp']==start['party'][0]['exp'] and s['party'][0]['evs']==start['party'][0]['evs'])
    cmd('screenshot',name='capture-breakout')
    cmd('hold',keys='LEFT',frames=30);cmd('hold',keys='A',frames=90)
    check('Attacking still works after breakout',cmd('status')['arena']['shots'][0]>0)
    result=dict(ok=True,checks=checks,rom_sha256=s['rom_sha256'])
    (WORK/'results/capture.json').write_text(json.dumps(result,indent=2)+'\n')
    print(str(len(checks))+' capture checks passed')
if __name__=='__main__':main()
