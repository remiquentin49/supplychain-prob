from __future__ import annotations
import base64, csv, hashlib, os, pathlib, zipfile
DIST='supplychain_prob-0.1.0.dist-info'
def _meta(path):
    p=pathlib.Path(path)/DIST; p.mkdir(parents=True, exist_ok=True)
    (p/'METADATA').write_text('Metadata-Version: 2.1\nName: supplychain-prob\nVersion: 0.1.0\nRequires-Python: >=3.11\nProvides-Extra: dev\n')
    (p/'WHEEL').write_text('Wheel-Version: 1.0\nGenerator: local\nRoot-Is-Purelib: true\nTag: py3-none-any\n')
    return DIST
def prepare_metadata_for_build_editable(metadata_directory, config_settings=None): return _meta(metadata_directory)
def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None): return _meta(metadata_directory)
def get_requires_for_build_editable(config_settings=None): return []
def get_requires_for_build_wheel(config_settings=None): return []
def build_editable(wheel_directory, config_settings=None, metadata_directory=None): return _wheel(wheel_directory, editable=True)
def build_wheel(wheel_directory, config_settings=None, metadata_directory=None): return _wheel(wheel_directory, editable=False)
def _wheel(wheel_directory, editable=False):
    wh=os.path.join(wheel_directory,'supplychain_prob-0.1.0-py3-none-any.whl'); records=[]
    def add(z,path,data):
        z.writestr(path,data); h=base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b'=').decode(); records.append((path,f'sha256={h}',str(len(data))))
    with zipfile.ZipFile(wh,'w',zipfile.ZIP_DEFLATED) as z:
        if editable:
            add(z,'supplychain_prob.pth',(str(pathlib.Path.cwd())+'\n'+str(pathlib.Path.cwd()/'src')).encode())
        else:
            for f in pathlib.Path('src/supplychain_prob').rglob('*'):
                if f.is_file(): add(z,str(f.relative_to('src')),f.read_bytes())
        add(z,DIST+'/METADATA',b'Metadata-Version: 2.1\nName: supplychain-prob\nVersion: 0.1.0\n')
        add(z,DIST+'/WHEEL',b'Wheel-Version: 1.0\nGenerator: local\nRoot-Is-Purelib: true\nTag: py3-none-any\n')
        rec=DIST+'/RECORD'; rows=records+[(rec,'','')]
        import io
        s=io.StringIO(); csv.writer(s).writerows(rows); z.writestr(rec,s.getvalue())
    return os.path.basename(wh)
