#!/usr/bin/env python3
"""Keep verified vendor Calamares sequence and append our installed login cleanup."""
import sys
from pathlib import Path
import yaml

p=Path(sys.argv[1])
s=yaml.safe_load(p.read_text())
if not isinstance(s,dict) or not isinstance(s.get('sequence'),list):
    raise SystemExit('Invalid Calamares settings sequence')
seq=s['sequence']
exec_phases=[x for x in seq if isinstance(x,dict) and isinstance(x.get('exec'),list)]
if len(exec_phases)!=1:
    raise SystemExit('Expected a single vendor exec phase')
steps=exec_phases[0]['exec']
for required in ('partition','mount','unpackfs','fstab','users','initramfs','bootloader'):
    if required not in steps:
        raise SystemExit(f'Missing vendor installer job: {required}')
if 'shellprocess@installed-session' not in steps:
    # Run only after account creation, before final unmount.
    position=steps.index('users')+1
    steps.insert(position,'shellprocess@installed-session')
instances=s.setdefault('instances',[])
if not any(isinstance(x,dict) and x.get('id')=='installed-session' for x in instances):
    instances.append({'id':'installed-session','module':'shellprocess','config':'shellprocess-installed-session.conf'})
# The local directory contains the installed-session override.
ms=s.setdefault('modules-search',[])
if 'local' not in ms: ms.insert(0,'local')
p.write_text(yaml.safe_dump(s,sort_keys=False,allow_unicode=True))
print('Vendor Calamares job sequence preserved; installed-session cleanup registered')
