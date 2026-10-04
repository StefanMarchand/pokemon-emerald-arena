import json,importlib.util,struct
from test_stability import L,cmd,check,checks,tap,until,ROOT
import lab
def bind(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tests/arena'/f'{name}.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.cmd=lambda action,**kw: {} if action=='view' else cmd(action,**kw)
    return m
try:
    cmd('boot');cmd('fixture-team',mons=['CHARIZARD:40','BLASTOISE:40']);L.mail(17);L.mail(28)
    s=cmd('battle',species='SCEPTILE',level=35,classic=False,elemental_duel=True)
    for _ in range(240):
        s=cmd('wait',frames=6)
        if 0<s['battlers'][0]['hp']<s['battlers'][0]['max_hp']-20:break
    check('real damage precedes healing',0<s['battlers'][0]['hp']<s['battlers'][0]['max_hp'])
    tap('START');hp=cmd('status')['battlers'][0]['hp'];maximum=s['battlers'][0]['max_hp']
    tap('DOWN');tap('A',100);tap('A');tap('A',100);tap('A',100)
    check('Potion through START Bag restores native amount',cmd('status')['battlers'][0]['hp']==min(hp+20,maximum))
    tap('A',0);s=until(lambda s:s['arena']['active'])
    check('Potion returns to same battle without resetting HP',s['battlers'][0]['hp']==min(hp+20,maximum))
    cmd('screenshot',name='six-healed')
    res=bind('test_result_flow')
    cmd('boot');cmd('fixture-lead',species='TREECKO',level=10)
    res.normal_victory();cmd('wait',frames=220);cmd('heal')
    s=res.normal_victory();cmd('wait',frames=8)
    check('real second win levels Treecko to 11',s['party'][0]['level']==11)
    cmd('screenshot',name='six-level-toast')
    check('level toast consumed its queued level',L.read('sFieldLevel',6)[0]==0)
    check('both XP awards reach notifications',struct.unpack('<4I',L.read('gArenaQualityTelemetry',16))[1]==188)
    before=cmd('status')['position'];s=cmd('hold',keys='LEFT',frames=16)
    check('player walks while level notification is visible',s['position']!=before and not s['field_locked'])
    cap=bind('test_capture');cap.fresh();cap.battle();s=cap.catch();cmd('wait',frames=8)
    check('capture returns to field with real party award',s['capture']['caught']==1 and len(s['party'])==2)
    cmd('screenshot',name='six-caught-toast')
    check('caught notification is emitted after battle',L.read('sFieldCaught',1)[0]==0 and struct.unpack('<4I',L.read('gArenaQualityTelemetry',16))[2]==1)
finally:
    (lab.WORK/'results/matheus-feedback.json').write_text(json.dumps(dict(checks=checks,rom_sha256=getattr(L,'sha',None)),indent=2)+'\n')
    if L.runner:L.raw('quit',reply=False);L.runner.wait(timeout=5)
