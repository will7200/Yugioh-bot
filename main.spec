# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['D:\\Sync\\OneDrive\\Yu-gi-oh_bot'],
             binaries=[],
             datas=[    ('assets/', 'assets'),('config.ini','.'),('bin/','bin/'), ('.gitignore','tmp'), ('logging.yaml','.'), ('version.txt', '.')],
             hiddenimports=['scipy._lib.messagestream',
              'cython', 'sklearn', 'sklearn.tree','sklearn.neighbors.quad_tree','sklearn.neighbors.typedefs',
              'sklearn.tree._utils','apscheduler.triggers.date'],
             hookspath=['.'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='dlbot',
          debug=False,
          strip=False,
          upx=True,
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='dlbot')
