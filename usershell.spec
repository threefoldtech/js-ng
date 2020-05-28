# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['usershell.py'],
             pathex=['/sandbox/code/github/js-next/js-ng'],
             binaries=[],
             datas=[('jumpscale', 'jumpscale')],
             hiddenimports=['jinja2', 'arrow', 'redis','psutil', 'fabric', 'terminaltables', 'distro', 'libtmux', 'distutils', 'watchdog', 'watchdog.events', 'watchdog.observers', 'gevent', 'stellar_sdk'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='usershell',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
