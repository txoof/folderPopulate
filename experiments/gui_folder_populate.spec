# -*- mode: python -*-

block_cipher = None


a = Analysis(['gui_folder_populate.py'],
             pathex=['/Users/aaronciuffo/src/folderPopulate'],
             binaries=[],
             datas=[],
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
          name='gui_folder_populate',
          debug=False,
          strip=False,
          upx=True,
          console=False )
app = BUNDLE(exe,
             name='gui_folder_populate.app',
             icon=None,
             bundle_identifier=None)
