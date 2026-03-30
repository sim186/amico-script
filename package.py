import os
import sys
import shutil
import PyInstaller.__main__

def build():
    # Detect OS
    is_windows = sys.platform.startswith('win')
    is_mac = sys.platform == 'darwin'
    
    # Define paths
    root = os.path.dirname(os.path.abspath(__file__))
    dist = os.path.join(root, "dist")
    build_dir = os.path.join(root, "build")
    
    # Clean up previous builds
    for d in [dist, build_dir]:
        if os.path.exists(d):
            print(f"Cleaning {d}...")
            shutil.rmtree(d)
            
    # PyInstaller arguments
    args = [
        'run.py',                          # Entry point
        '--name=AmicoScript',              # Output name
        '--onedir',                        # Better for large apps (faster launch/debug)
        '--noconsole',                     # No terminal window (if desired)
        '--paths=backend',                 # Make backend modules importable during analysis/runtime
        '--add-data=frontend:frontend',    # Include frontend files
        '--add-data=VERSION:.',            # Include VERSION at bundle root
        '--add-data=CHANGELOG.md:.',      # Include changelog
        '--hidden-import=main',            # backend/main.py imported dynamically in run.py
        '--hidden-import=ffmpeg_helper',   # backend/ffmpeg_helper.py imported dynamically in run.py
        '--hidden-import=faster_whisper',
        '--collect-data=faster_whisper',  # include VAD ONNX assets (silero_vad_v6.onnx)
        '--hidden-import=pyannote.audio',
        '--collect-data=pyannote.audio',  # include telemetry/config.yaml and other package assets
        '--hidden-import=torch',
        '--hidden-import=torchaudio',
        '--hidden-import=uvicorn.streaming', # Hidden dependency
        '--hidden-import=sse_starlette.sse',
    ]

    if is_mac:
        args.append('--windowed') # Create .app

        # On Windows, create a version resource file for the executable
        version_file_path = None
        try:
                root_version = os.path.join(root, 'VERSION')
                if os.path.exists(root_version):
                        ver_text = open(root_version, 'r', encoding='utf-8').read().strip()
                else:
                        ver_text = '0.0.0'
                ver_nums = ver_text.split('.')
                while len(ver_nums) < 3:
                        ver_nums.append('0')
                filevers = tuple(int(x) if x.isdigit() else 0 for x in (ver_nums + ['0'])[:4])

                if is_windows:
                        # create a temporary version info python-style file consumed by PyInstaller
                        build_meta_dir = os.path.join(root, 'buildmeta')
                        os.makedirs(build_meta_dir, exist_ok=True)
                        version_file_path = os.path.join(build_meta_dir, 'version_info.txt')
                        with open(version_file_path, 'w', encoding='utf-8') as vf:
                                vf.write('''# UTF-8
VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=%s,
        prodvers=%s,
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo([
            StringTable(
                '040904b0',
                [
                    ('CompanyName', ''),
                    ('FileDescription', 'AmicoScript'),
                    ('FileVersion', '%s'),
                    ('InternalName', 'AmicoScript'),
                    ('LegalCopyright', ''),
                    ('OriginalFilename', 'AmicoScript.exe'),
                    ('ProductName', 'AmicoScript'),
                    ('ProductVersion', '%s')
                ]
            )
        ]),
        VarFileInfo([VarStruct('Translation', [1033, 1200])])
    ]
)
''' % (str(filevers), str(filevers), ver_text, ver_text))
                        args.append('--version-file=%s' % version_file_path)
        except Exception:
                pass
    
    print("Starting build with PyInstaller...")
    PyInstaller.__main__.run(args)
    
    print("\nDraft build complete!")
    print(f"Output available in: {dist}/AmicoScript")
    print("\nNote: You may need to manually bundle ffmpeg binaries in the dist folder if not in system path.")

if __name__ == "__main__":
    build()
