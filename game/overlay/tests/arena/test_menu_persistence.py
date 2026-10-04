#!/usr/bin/env python3
"""Native menus must not erase cover or renew timed barriers. Real ROM/input."""
import json
from test_stability import L, cmd, check, checks, tap, until
import lab

def u16(symbol, offset=0):
    return int.from_bytes(L.read(L.symbols[symbol]+offset,2),'little')

def select(slot):
    for _ in range(5):
        if cmd('status')['arena']['move_slot']==slot:return
        tap('R',0)
    raise AssertionError('slot selection')

def menu_cancel():
    tap('START',0)
    tap('SELECT',180)
    check('native party is open',cmd('status')['cb2']=='CB2_UpdatePartyMenu')
    frozen=(u16('sCover',12),u16('sSmoke',4),u16('sBarrierLife'))
    cmd('wait',frames=600)
    check('cover smoke barrier timers freeze in party',frozen==(u16('sCover',12),u16('sSmoke',4),u16('sBarrierLife')))
    tap('B',0)
    until(lambda s:s['arena']['active'],frames=600)

def main():
    cmd('boot');cmd('fixture-team',mons=['CHARIZARD:100','MUDKIP:25']);assert L.mail(19)==0
    cmd('battle',species='POOCHYENA',level=3,classic=False)
    select(0)
    for _ in range(80):
        cmd('hold',keys='A',frames=2)
        if u16('sCover',12):break
    check('Substitute created through real attack',u16('sCover',12)>0)
    hp=u16('sCover',12)
    menu_cancel()
    check('Substitute HP survives cancel',u16('sCover',12)==hp)
    until(lambda s:L.read(L.symbols['sCover']+16,1)[0]<64,frames=300)
    check('Substitute OBJ recreated',L.read(L.symbols['sCover']+16,1)[0]<64)
    cmd('screenshot',name='menu-persistence-substitute')
    select(1)
    for _ in range(100):
        cmd('hold',keys='A',frames=2)
        if u16('sSmoke',4):break
    check('Smokescreen cast',u16('sSmoke',4)>0)
    life=u16('sSmoke',4)
    menu_cancel()
    check('smoke survives without timer refill',0<u16('sSmoke',4)<=life)
    cmd('screenshot',name='menu-persistence-smoke')
    cmd('boot');cmd('fixture-team',mons=['STARMIE:100','MUDKIP:25']);assert L.mail(23)==0
    cmd('battle',species='POOCHYENA',level=3,classic=False)
    select(0)
    for _ in range(100):
        cmd('hold',keys='A',frames=2)
        if u16('sBarrierLife'):break
    check('Reflect cast',u16('sBarrierLife')>0)
    cmd('wait',frames=150)
    life=u16('sBarrierLife');menu_cancel()
    check('Reflect does not reset to full duration',0<u16('sBarrierLife')<=life)
    cmd('wait',frames=700)
    check('Reflect expires normally',u16('sBarrierLife')==0)
    cmd('boot');cmd('fixture-team',mons=['GASTLY:24','MUDKIP:25']);assert L.mail(24)==0
    cmd('battle',species='POOCHYENA',level=3,classic=False)
    select(0)
    for _ in range(100):
        cmd('hold',keys='A',frames=2)
        if u16('sDecoys',8):break
    check('Double Team cast',u16('sDecoys',8)>0)
    life=u16('sDecoys',8);menu_cancel()
    check('decoy survives without timer refill',0<u16('sDecoys',8)<=life)
    until(lambda s:L.read(L.symbols['sDecoys']+12,1)[0]<64,frames=300)
    check('decoy OBJ recreated',L.read(L.symbols['sDecoys']+12,1)[0]<64)
    cmd('screenshot',name='menu-persistence-decoy')
    cmd('boot');cmd('fixture-team',mons=['CHARIZARD:100','MUDKIP:25']);assert L.mail(30)==0
    cmd('battle',species='POOCHYENA',level=3,classic=False)
    select(3)
    for _ in range(100):
        cmd('hold',keys='A',frames=2)
        if L.read(L.symbols['sGuardLife'],1)[0]:break
    check('Protect cast',L.read(L.symbols['sGuardLife'],1)[0]>0)
    life=L.read(L.symbols['sGuardLife'],1)[0];menu_cancel()
    check('Protect survives without timer refill',0<L.read(L.symbols['sGuardLife'],1)[0]<=life)
    cmd('boot');cmd('fixture-team',mons=['CHARIZARD:100']);assert L.mail(19)==0
    cmd('battle',species='POOCHYENA',level=3,classic=False)
    check('new encounter clears cover and smoke',u16('sCover',12)==0 and u16('sSmoke',4)==0)

if __name__=='__main__':
    try:main()
    finally:
        (lab.WORK/'results/menu-persistence.json').write_text(json.dumps(dict(checks=checks,rom_sha256=getattr(L,'sha',None)),indent=2)+'\n')
        if L.runner:L.raw('quit',reply=False);L.runner.wait(timeout=5)
