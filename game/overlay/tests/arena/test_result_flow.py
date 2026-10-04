#!/usr/bin/env python3
"""Fast results on the real ROM: earned levels, learning and native choices.

Fixtures use native CreateMon; victories use buttons only. No writes to party,
HP, XP, PP or outcome. Unsupported random wild held items are rejected while
preparing the encounter, before any combat; never reroll a combat result.
"""
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/arena'))
from lab import call, WORK

checks = []
victories = []


def cmd(action, **kw):
    reply = call(dict(action=action, **kw))
    assert reply['ok'], reply
    return reply['result']


def check(name, condition):
    assert condition, name
    checks.append(name)
    print('PASS ' + name, flush=True)


def encounter(level=12):
    # Native wild encounters may roll an Oran Berry; items remain classic.
    field = cmd('status')
    assert field['cb2'] == 'CB2_Overworld' and not field['field_locked']
    cmd('snapshot', name='result-fixture-field')
    for attempt in range(10):
        if attempt:
            cmd('restore', name='result-fixture-field')
            cmd('wait', frames=attempt * 8)
        start = cmd('battle', species='POOCHYENA', level=level, classic=False)
        if start['arena']['active']:
            assert start['party'] == field['party']
            return start
        assert start['battlers'][1]['item'], 'Unexpected eligibility fallback'
    raise AssertionError('Could not prepare a native no-held-item encounter')


def knock_out():
    s=cmd('hold', keys='LEFT', frames=44)
    for _ in range(1000):
        # Fight the stronger wild opponent rather than standing still through
        # its new native Howl boost. All choices are ordinary player buttons.
        dx=s['arena']['x'][1]-s['arena']['x'][0]
        dy=s['arena']['y'][1]-s['arena']['y'][0]
        distance=dx*dx+dy*dy
        keys=[]
        if distance<65*65 and s['combat']['windup'][1] and not s['combat']['dash_cooldown'][0]:
            keys=['B',('RIGHT' if s['arena']['x'][0]<160 else 'LEFT') if abs(dy)>abs(dx) else ('UP' if s['arena']['y'][0]>80 else 'DOWN')]
        elif distance<27*27:
            keys=['A']
        else:
            if abs(dx)>6:keys.append('RIGHT' if dx>0 else 'LEFT')
            if abs(dy)>6:keys.append('DOWN' if dy>0 else 'UP')
        s = cmd('hold', keys='+'.join(keys) or 'A', frames=3)
        assert s['party'][0]['hp'] > 0, 'Player lost this real battle'
        if s['battlers'][1]['hp'] == 0:
            return s
    raise AssertionError('Player never won with native attacks')


def settle():
    callbacks = set()
    for frames in range(240):
        # Intentionally NO confirm key anywhere after the actual KO.
        s = cmd('wait', frames=1)
        callbacks.add(s['cb2'])
        if s['result_flow']['ui_fallbacks']:
            return s, frames + 1, callbacks
        if s['cb2'] == 'CB2_Overworld' and not s['field_locked']:
            return s, frames + 1, callbacks
    raise AssertionError('Silent settlement did not finish')


def normal_victory():
    start = encounter()
    ko = knock_out()
    result, frames, callbacks = settle()
    assert result['cb2'] == 'CB2_Overworld' and result['battle_outcome'] == 1
    assert result['result_flow']['ui_fallbacks'] == 0
    assert not any('Reshow' in cb or 'PartyMenu' in cb for cb in callbacks)
    assert frames <= 150, (frames, result['result_flow'])
    assert result['party'][0]['exp'] == start['party'][0]['exp'] + 94
    assert result['party'][0]['evs'][1] == start['party'][0]['evs'][1] + 1
    assert result['party'][1] == start['party'][1]
    emitted = ko['arena']['shots'][0] - start['arena']['shots'][0]
    assert result['party'][0]['pp'][0] == start['party'][0]['pp'][0] - emitted
    assert all(mon['checksum_ok'] for mon in result['party'])
    victories.append(dict(frames_to_free_field=frames, result=result['result_flow'],
                          before=start['party'], after=result['party']))
    return result


def reach_question(opcode):
    for _ in range(50):
        op = int(cmd('inspect', symbol='gBattlescriptCurrInstr', size=1, deref=True)['hex'], 16)
        flags = int(cmd('inspect', symbol='gBattleControllerExecFlags', size=4)['hex'], 16)
        if op == opcode and flags == 0:
            return cmd('wait', frames=4)
        cmd('press', keys='A', frames=1)
        cmd('wait', frames=20)
    raise AssertionError('Native yes/no question not reached')


def reach_move_selection():
    saw_evolution = False
    for _ in range(300):
        s = cmd('wait', frames=20)
        saw_evolution |= 'Evolution' in s['cb2']
        if 'Task_HandleReplaceMoveInput' in s['tasks']:
            # The task exists while summary graphics are still fading in;
            # native input deliberately ignores keys until that fade finishes.
            return cmd('wait', frames=60), saw_evolution
        cmd('press', keys='A', frames=1)
    raise AssertionError('Native replacement screen not reached')


def main():
    began = time.monotonic()
    cmd('boot')
    field = cmd('fixture-lead', species='TREECKO', level=10)
    normal_victory()
    cmd('heal')  # Explicit native fixture healing, never part of the rewards.
    leveled = normal_victory()
    check('ordinary KO returns to the field with no result text or button', len(victories) == 2)
    check('every win retains exact native XP EV and emitted PP', leveled['party'][0]['exp'] == 748
          and leveled['party'][0]['evs'] == [0, 2, 0, 0, 0, 0])
    check('earned level-up recomputes real stats without an EXP-bar scene', leveled['party'][0]['level'] == 11
          and leveled['party'][0]['max_hp'] > field['party'][0]['max_hp'])
    check('native learning fills an empty move slot without an artificial menu', leveled['party'][0]['moves'] == [1, 43, 71, 98]
          and leveled['party'][0]['pp'][3] == 30)
    cmd('save', name='fast-result-learned')
    loaded = cmd('boot', save='fast-result-learned')
    check('fast-result HP PP XP EV and learned move survive native save/reboot', loaded['party'] == leveled['party'])
    cmd('screenshot', name='result-level11-saved')

    # Four full slots at level 15: earn level 16 in actual battles, then verify
    # that the native decision is NOT silently accepted or discarded.
    cmd('fixture-lead', species='TREECKO', level=15)
    for _ in range(5):
        cmd('heal')
        normal_victory()
    cmd('heal')
    start = encounter()
    ko = knock_out()
    prompt, frames, callbacks = settle()
    check('full moveset restores native UI instead of making a choice', prompt['result_flow']['ui_fallbacks'] == 1
          and prompt['party'][0]['level'] == 16 and prompt['party'][0]['moves'] == [1, 43, 71, 98])
    cmd('wait', frames=160)
    cmd('snapshot', name='result-learn-choice')
    cmd('screenshot', name='result-learn-choice')
    reach_question(0x5A)  # Native yesnoboxlearnmove opcode, no guessed RAM address.
    cmd('press', keys='A', frames=1)
    selection, _ = reach_move_selection()
    check('native summary lets the player choose the move to replace', selection['party'][0]['moves'] == [1, 43, 71, 98])
    cmd('screenshot', name='result-learn-moves')
    cmd('press', keys='DOWN', frames=1)  # Explicitly replace Leer with Pursuit.
    cmd('press', keys='A', frames=1)
    evolved, saw_evolution = reach_move_selection()
    check('chosen move is learned and earned evolution remains fully native', saw_evolution
          and evolved['party'][0]['species'] == 278 and evolved['party'][0]['moves'] == [1, 228, 71, 98]
          and evolved['party'][0]['exp'] == 2599 and evolved['party'][0]['level'] == 16)
    cmd('screenshot', name='result-evolved-learning')
    # Grovyle naturally offers Fury Cutter after evolution; explicitly choose
    # its default Pound slot. This is a second real decision, not an auto-learn.
    cmd('press', keys='A', frames=1)
    for _ in range(150):
        finished = cmd('wait', frames=20)
        if finished['cb2'] == 'CB2_Overworld' and not finished['field_locked']:
            break
        cmd('press', keys='A', frames=1)
    check('evolution and its additional learning return to the real field', finished['cb2'] == 'CB2_Overworld'
          and not finished['field_locked'] and finished['party'][0]['moves'] == [210, 228, 71, 98]
          and finished['party'][0]['evs'] == [0, 6, 0, 0, 0, 0])
    cmd('save', name='fast-result-evolved')
    reloaded = cmd('boot', save='fast-result-evolved')
    check('evolution choices and exact earned progress persist in the cartridge save', reloaded['party'] == finished['party'])
    result = dict(ok=True, checks=checks, rom_sha256=loaded['rom_sha256'], victories=victories,
                  final=finished, seconds=round(time.monotonic()-began, 3))
    (WORK / 'results/result-flow.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(ok=True, checks=len(checks), seconds=result['seconds'])))


if __name__ == '__main__':
    main()
