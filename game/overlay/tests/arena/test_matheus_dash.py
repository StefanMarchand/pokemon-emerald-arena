import json
from test_stability import L,cmd,check,checks,tap
import lab
try:
    cmd('boot');cmd('fixture-team',mons=['CHARIZARD:100'])
    s=cmd('battle',species='BLASTOISE',level=36,classic=False)
    s=cmd('hold',keys='B+UP',frames=11)
    check('blocked landing retains swept collision',s['arena']['y'][0]>=96)
    cmd('boot');cmd('fixture-team',mons=['CHARIZARD:100'])
    s=cmd('battle',species='BLASTOISE',level=36,classic=False)
    for _ in range(60):
        if s['arena']['x'][0]<=93:break
        s=cmd('hold',keys='LEFT',frames=1)
    for _ in range(90):
        if s['arena']['y'][0]<=81:break
        s=cmd('hold',keys='UP',frames=1)
    before=cmd('status');cmd('screenshot',name='six-dash-before')
    s=cmd('hold',keys='B+UP+RIGHT',frames=4)
    print('dash coords',before['arena']['x'],before['arena']['y'],s['arena']['x'],s['arena']['y'],flush=True)
    check('clear destination crosses central obstacle',s['arena']['x'][0]>120 and s['arena']['y'][0]<59)
    cmd('screenshot',name='six-dash-after')
    tap('START');paused=cmd('status');s=cmd('wait',frames=120)
    check('pause freezes dodge and landing',paused['arena']==s['arena'])
    tap('START');s=cmd('wait',frames=30)
    check('dash ends outside the central solid',s['arena']['y'][0]<59)
finally:
    (lab.WORK/'results/matheus-dash.json').write_text(json.dumps(dict(checks=checks,rom_sha256=getattr(L,'sha',None)),indent=2)+'\n')
    if L.runner:L.raw('quit',reply=False);L.runner.wait(timeout=5)
