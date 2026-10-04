import json
from test_stability import L,cmd,check,checks
import lab
try:
    cmd('boot');cmd('fixture-team',mons=['CHARIZARD:40'])
    s=cmd('battle',species='MIGHTYENA',level=20,classic=False)
    check('Intimidate matchup skips classic presentation',s['arena']['active'] and s['intro']['skipped']==1)
    check('native Intimidate still lowers Attack',s['battlers'][0]['stat_stages'][1]==5)
    cmd('boot');cmd('fixture-team',mons=['CHARIZARD:40'])
    s=cmd('battle',species='KYOGRE',level=30,classic=False)
    check('Drizzle matchup skips classic presentation',s['arena']['active'] and s['intro']['skipped']==1)
    check('native Drizzle still sets weather',int.from_bytes(L.read('gBattleWeather',2),'little')!=0)
finally:
    (lab.WORK/'results/matheus-intro.json').write_text(json.dumps(dict(checks=checks,rom_sha256=getattr(L,'sha',None)),indent=2)+'\n')
    if L.runner:L.raw('quit',reply=False);L.runner.wait(timeout=5)
