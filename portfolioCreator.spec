# -*- mode: python -*-

block_cipher = None


a = Analysis(['portfolioCreator.py'],
             pathex=['/Users/aciuffo/src/folderPopulate'],
             binaries=[],
             datas=[('./data/*', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='portfolioCreator',
          debug=False,
          strip=False,
          upx=True,
          console=False )
app = BUNDLE(exe,
             name='portfolioCreator.app',
             icon=None,
             bundle_identifier=None)
