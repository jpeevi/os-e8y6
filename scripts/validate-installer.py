#!/usr/bin/env python3
"""Check installed Calamares runtime in isolated rootfs; no host modifications."""
import sys
from pathlib import Path
import yaml

root=Path(sys.argv[1]); issues=[]
def require(rel):
    if not (root/rel).exists(): issues.append('Missing rootfs file: '+rel)
for rel in ('usr/bin/rsync','usr/bin/unsquashfs','usr/bin/calamares',
            'etc/calamares/settings.conf','etc/calamares/modules/unpackfs.conf',
            'etc/calamares/modules/initramfs.conf',
            'etc/calamares/modules/shellprocess-installed-session.conf',
            'usr/local/bin/os-e8y6-installer-logs',
            'usr/local/libexec/e8y6-calamares-root'):
    require(rel)
settings=root/'etc/calamares/settings.conf'
if settings.exists():
    cfg=yaml.safe_load(settings.read_text())
    jobs=[job for phase in cfg.get('sequence',[]) if isinstance(phase,dict) for job in phase.get('exec',[])]
    for job in ('partition','mount','unpackfs','fstab','users','initramfs','bootloader','shellprocess@installed-session'):
        if job not in jobs: issues.append('Missing Calamares exec job: '+job)
    if 'shellprocess@installed-session' in jobs and jobs.index('shellprocess@installed-session') < jobs.index('users'):
        issues.append('Installed-session cleanup before users')
    for instance in cfg.get('instances',[]):
        if not isinstance(instance,dict):continue
        module=instance.get('module');name=instance.get('config')
        if module=='shellprocess' and name:
            local=root/'etc/calamares/modules'/name
            shared=root/'usr/share/calamares/modules'/name
            if not local.exists() and not shared.exists():
                issues.append('Missing shellprocess instance configuration: '+name)
    # Require Calamares modules installed on disk; exact location is distro dependent.
    for job in jobs:
        mod=job.split('@')[0]
        if mod not in ('partition','mount','unpackfs','fstab','users','initramfs','bootloader','shellprocess'):
            continue
        matches=list((root/'usr/lib').rglob(f'*{mod}*')) if (root/'usr/lib').exists() else []
        if not matches: issues.append('Cannot locate Calamares module: '+mod)
if issues: raise SystemExit('\n'.join(issues))
print('Installer module/configuration files present')
