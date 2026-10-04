#!/usr/bin/env python3
"""Real ROM regression gates. Disposable saves; native menus and damage only."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/arena'))
import lab

L = lab.Lab.__new__(lab.Lab)
L.runner = None
L.live_speed = None
L.mode = 'lab'
checks = []

def cmd(action, **kw):
    return L.handle(dict(action=action, **kw))

def check(name, condition):
    assert condition, name
    checks.append(name)
    print('PASS', name, flush=True)

def tap(key, wait=30):
    cmd('press', keys=key, frames=3)
    return cmd('wait', frames=wait)

def until(predicate, frames=600, confirm=False):
    for _ in range(frames // 5):
        s = tap('A', 2) if confirm else cmd('wait', frames=5)
        if predicate(s):
            return s
    cmd('screenshot', name='stability-timeout')
    raise AssertionError(('timeout', s['cb2'], s['battle_main'], s.get('tasks')))

def main():
    cmd('boot')
    cmd('fixture-team', mons=['TREECKO:30', 'MUDKIP:25'])
    start = cmd('battle', species='POOCHYENA', level=10, classic=False)
    check('normal encounter still enters arena', start['arena']['active'])
    tap('START')
    before = cmd('status')
    after = cmd('wait', frames=180)
    check('pause freezes HP PP and arena clock', before['battlers'] == after['battlers']
          and before['arena']['frames'] == after['arena']['frames'])
    tap('SELECT', 180)
    check('SELECT opens native party menu', cmd('status')['cb2'] == 'CB2_UpdatePartyMenu')
    tap('B', 180)
    check('cancel party returns to arena', cmd('status')['arena']['active'])
    tap('SELECT', 180)
    tap('DOWN')
    tap('A')
    tap('A', 0)
    switched = until(lambda s: s['arena']['active'])
    check('native party switch enters Mudkip', switched['battlers'][0]['species'] == L.species_id('MUDKIP'))
    cmd('wait', frames=180)
    cmd('screenshot', name='stability-mudkip-switch')
    # An unsupported lead uses the real native engine, then a compatible
    # replacement must finish its transaction and recover the arena.
    cmd('boot')
    cmd('fixture-team', mons=['RALTS:4', 'MUDKIP:25'])
    assert L.mail(38) == 0
    start = cmd('battle', species='POOCHYENA', level=3, classic=False)
    check('unsupported held effect safely uses native combat', not start['arena']['active'])
    cmd('wait', frames=120)
    tap('DOWN')  # FIGHT -> POKEMON
    tap('A', 180)
    check('native action menu opens party', cmd('status')['cb2'] == 'CB2_UpdatePartyMenu')
    tap('DOWN')
    tap('A')
    tap('A', 0)
    switched = until(lambda s: s['arena']['active'], frames=1800, confirm=True)
    check('Ralts to Mudkip recovers arena without deadlock', switched['battlers'][0]['species'] == L.species_id('MUDKIP'))
    cmd('wait', frames=180)
    cmd('screenshot', name='stability-classic-to-arena')
    # Finish by playing; never force HP, experience or a victory flag.
    sys.path.insert(0, str(ROOT / 'tests/arena'))
    import test_result_flow as result
    result.cmd = cmd
    result.knock_out()
    settled, _, _ = result.settle()
    check('mixed-mode victory returns field control', settled['cb2'] == 'CB2_Overworld'
          and not settled['field_locked'])
    cmd('save', name='stability-mixed-mode')
    loaded = cmd('boot', save='stability-mixed-mode')
    check('mixed-mode save survives cold boot', loaded['party'] == settled['party'])
    cmd('fixture-team', mons=['MUDKIP:25', 'RALTS:4'])
    again = cmd('battle', species='POOCHYENA', level=3, classic=False)
    check('arena still starts after mixed-mode save/reboot', again['arena']['active'])
    for index in range(3):
        cmd('boot')
        cmd('fixture-team', mons=['ZIGZAGOON:5', 'MUDKIP:25'])
        assert L.mail(33) == 0
        start = cmd('battle', species='POOCHYENA', level=3, classic=False)
        check('inert held Potion permits arena %d' % index, start['arena']['active'])
        check('held Potion remains equipped', start['battlers'][0]['item'] == 13)
    cmd('boot')
    cmd('fixture-team', mons=['CASCOON:10', 'MUDKIP:25'])
    assert L.mail(34) == 0
    start = cmd('battle', species='POOCHYENA', level=3, classic=False)
    check('Shed Skin and status-only Harden are supported', start['arena']['active'])
    # Stronger legal fixture with the same ability: observe its real cure RNG.
    cmd('boot')
    cmd('fixture-team', mons=['DRATINI:100', 'MUDKIP:25'])
    assert L.mail(34) == 0
    start = cmd('battle', species='POOCHYENA', level=3, classic=False)
    cured = until(lambda s: s['party'][0]['status'] == 0, frames=12000)
    check('Shed Skin cure persists in party and battler', cured['battlers'][0]['status'] == 0)
    check('Shed Skin leaves no controller request', L.u32('gBattleControllerExecFlags') == 0)

if __name__ == '__main__':
    try:
        main()
    finally:
        (lab.WORK / 'results').mkdir(exist_ok=True)
        (lab.WORK / 'results/stability.json').write_text(json.dumps(dict(checks=checks,
            rom_sha256=getattr(L, 'sha', None)), indent=2) + '\n')
        if L.runner:
            L.raw('quit', reply=False)
            L.runner.wait(timeout=5)
