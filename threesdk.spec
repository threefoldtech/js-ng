# -*- mode: python ; coding: utf-8 -*-
import wcwidth

block_cipher = None


a = Analysis(['jumpscale/entry_points/usershell.py'],
             pathex=['/tmp'],
             binaries=[],
             datas=[
                 (os.path.dirname(wcwidth.__file__), 'wcwidth')
                 ],
             hiddenimports = ["packaging.requirements", "pkg_resources.py2_warn", "pathlib", "_cffi_backend"],
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
          name='3sdk',
          debug=False,
          bootloader_ignore_signals=False,
          strip=True,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
