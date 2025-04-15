# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['car_racer.py'],
    pathex=[],
    binaries=[],
    datas=[('background_music.wav', '.'), ('bonus_points.png', '.'), ('car.png', '.'), ('crash.png', '.'), ('crash.wav', '.'), ('enemy_car1.png', '.'), ('enemy_car2.png', '.'), ('enemy_car3.png', '.'), ('engine.wav', '.'), ('levelup.wav', '.'), ('powerup.wav', '.'), ('shield.png', '.'), ('speed_boost.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='car_racer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
