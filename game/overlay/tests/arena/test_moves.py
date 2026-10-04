#!/usr/bin/env python3
"""Six real move profiles, native consequences and classic handoff on mGBA."""
import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/arena'))
from lab import call,WORK
checks=[]
def cmd(action,**kw):
    r=call(dict(action=action,**kw));assert r['ok'],r
    return r['result']
def check(name,ok):
    assert ok,name
    checks.append(name);print('PASS '+name,flush=True)
def setup(species='TREECKO',level=11,enemy=3):
    cmd('boot');field=cmd('fixture-lead',species=species,level=level)
    cmd('battle',species='POOCHYENA',level=enemy,classic=False)
    ready=cmd('wait',frames=16);cmd('snapshot',name='moves-start')
    return field,ready
def select(slot):
    for _ in range(6):
        s=cmd('status')
        if s['arena']['move_slot']==slot:return s
        cmd('press',keys='R',frames=3)
        cmd('wait',frames=3)
    raise AssertionError('Cannot select supported slot')
def restore():return cmd('restore',name='moves-start')['status']
def main():
    began=time.monotonic();field,start=setup()
    cmd('press',keys='A',frames=1);far=cmd('wait',frames=24)
    check('Pound is a close arc, never a long-range bullet',far['moves']['kind'][0]==1 and far['arena']['hits'][0]==0 and far['battlers'][1]['hp']==start['battlers'][1]['hp'])
    check('missed melee still spends exactly one native PP',far['party'][0]['pp'][0]==34 and far['arena']['shots'][0]==1)
    restore();select(3);before=cmd('status');cmd('press',keys='RIGHT+A',frames=1);quick=cmd('wait',frames=26)
    quickDistance=quick['arena']['x'][0]-before['arena']['x'][0]
    check('Quick Attack is a fast long committed dash',quickDistance>=75 and quick['moves']['kind'][0]==2 and quick['moves']['range'][0]==84)
    check('offensive dash uses PP and is not defensive invulnerability',quick['party'][0]['pp'][3]==29 and quick['arena']['dodges']==0)
    cmd('screenshot',name='moves-quick-attack')
    restore();select(3);cmd('press',keys='UP+A',frames=1);wall=cmd('wait',frames=28)
    check('Quick Attack collides with and cracks a sturdy rock',wall['moves']['rush_walls'][0]==1 and wall['physics']['hp'][0]==1 and wall['arena']['y'][0]>=97)
    check('rush collision never refunds its committed PP',wall['party'][0]['pp'][3]==29)
    restore();select(2);cmd('press',keys='UP+A',frames=1);cover=cmd('wait',frames=55)
    check('Absorb is a green 132-pixel projectile',cover['moves']['kind'][0]==3 and cover['moves']['range'][0]==132)
    check('blocked Absorb damages cover but cannot heal',cover['physics']['hp'][0]==2 and cover['moves']['healed'][0]==0 and cover['ai']['blocked_shots'][0]>0 and cover['party'][0]['pp'][2]==19)
    cmd('screenshot',name='moves-absorb-cover')
    # Let a real enemy attack supply missing HP, then heal via an actual hit.
    field,start=setup(enemy=10);cmd('hold',keys='LEFT',frames=44)
    for _ in range(400):
        hurt=cmd('wait',frames=1)
        if hurt['party'][0]['hp']<hurt['party'][0]['max_hp'] and hurt['combat']['cooldown'][1]>20:break
    check('healing fixture damage comes from the enemy, not RAM writes',0<hurt['party'][0]['hp']<hurt['party'][0]['max_hp'])
    select(2)
    for _ in range(500):
        healed=cmd('hold',keys='A',frames=1)
        if healed['moves']['healed'][0]:break
    dealt=start['battlers'][1]['hp']-healed['battlers'][1]['hp']
    healing=healed['moves']['healed'][0]
    expected=max(1,dealt//2) # missing HP from the real 6-HP enemy hit exceeds this
    check('Absorb heals half of actual HP dealt with native rounding',dealt>0 and healing==expected and healing>0)
    check('native party and battle HP agree after drain',healed['party'][0]['hp']==healed['battlers'][0]['hp'] and healed['party'][0]['hp']<=healed['party'][0]['max_hp'])
    cmd('screenshot',name='moves-absorb-heal');after=cmd('wait',frames=25)
    check('return particles cannot heal a second time',after['moves']['healed']==healed['moves']['healed'])
    # Primary status move: real native stat stages, no HP damage or terrain hit.
    field,start=setup(enemy=2);select(1)
    cmd('press',keys='UP+A',frames=1);leerCover=cmd('wait',frames=30)
    check('Leer cannot damage scenery even when aimed at solid cover',leerCover['physics']['impacts']==0 and leerCover['physics']['solid_mask']==127 and leerCover['party'][0]['pp'][1]==29)
    restore();select(1);cmd('hold',keys='LEFT',frames=44)
    for _ in range(30):
        leer=cmd('hold',keys='A',frames=45)
        if leer['battlers'][1]['stat_stages'][2]==0:break
    check('Leer lowers native Defense to its legal minimum',leer['moves']['stat_changes'][0]==6 and leer['battlers'][1]['stat_stages'][2]==0)
    # The enemy can hit scenery with Tackle during this long sequence; the
    # isolated assertion above checks Leer without conflating both attackers.
    check('repeated Leer never damages the target HP',leer['battlers'][1]['hp']==start['battlers'][1]['hp'] and leer['arena']['hits'][0]==0)
    floor=cmd('hold',keys='A',frames=140)
    check('additional Leer spends PP without going below the stat floor',floor['battlers'][1]['stat_stages'][2]==0 and floor['moves']['stat_changes'][0]==6 and floor['party'][0]['pp'][1]<leer['party'][0]['pp'][1])
    cmd('screenshot',name='moves-leer-defense')
    cmd('press',keys='START',frames=1);cmd('wait',frames=4);frozen=cmd('status')
    cmd('press',keys='SELECT',frames=1);classic=cmd('wait',frames=140)
    check('native party menu receives Leer stages and all PP/HP exactly',classic['battlers']==frozen['battlers'] and classic['party']==frozen['party'] and classic['cb2']=='CB2_UpdatePartyMenu')
    field,start=setup('POOCHYENA',6);cmd('press',keys='RIGHT+A',frames=1);tackle=cmd('wait',frames=36)
    tackleDistance=tackle['arena']['x'][0]-start['arena']['x'][0]
    check('Tackle has its own shorter slower displacement',40<=tackleDistance<=55 and tackleDistance<quickDistance and tackle['moves']['range'][0]==50)
    check('Tackle spends one PP per action',tackle['party'][0]['pp'][0]==field['party'][0]['pp'][0]-1)
    field,start=setup('MUDKIP',10);slot=field['party'][0]['moves'].index(55);select(slot)
    water=cmd('status');check('Water Gun has a distinct 160-pixel projectile profile',water['moves']['kind'][0]==3 and water['moves']['range'][0]==160)
    cmd('press',keys='UP+A',frames=1);water=cmd('wait',frames=40)
    check('Water Gun hits cover and consumes its own native PP',water['ai']['blocked_shots'][0]>0 and water['physics']['hp'][0]==2 and water['party'][0]['pp'][slot]==field['party'][0]['pp'][slot]-1)
    cmd('screenshot',name='moves-water-gun')
    chosen=[]
    for _ in range(4):
        cmd('press',keys='R',frames=3);s=cmd('wait',frames=3);chosen.append(s['party'][0]['moves'][s['arena']['move_slot']])
    check('selection includes four newly adapted native Mudkip moves',set(chosen)=={33,45,189,55})
    result=dict(ok=True,checks=checks,rom_sha256=start['rom_sha256'],seconds=round(time.monotonic()-began,3),quick_distance=quickDistance,tackle_distance=tackleDistance)
    (WORK/'results/moves.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(ok=True,checks=len(checks),seconds=result['seconds'])))
if __name__=='__main__':main()
