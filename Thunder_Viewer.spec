# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Thunder_Viewer.py'],
             pathex=['C:\\Users\\ltber\\OneDrive\\Desktop\\Python_Stuff\\source_dir\\Thunder_Viewer'],
             binaries=[('C:\\Users\\ltber\\Anaconda3\Lib\\site-packages\\imagehash\\VERSION', 'imagehash/'),
                       ('C:\\Users\\ltber\\Anaconda3\\Lib\\site-packages\\PyQt5\\Qt\\bin\*', 'PyQt5\\Qt\\bin')],
             datas=[],
             hiddenimports=[],
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
          name='Thunder_Viewer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
