#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    (root / 'a.txt').write_text('hola', encoding='utf-8')
    (root / 'b.txt').write_text('hola', encoding='utf-8')
    (root / 'c.bin').write_bytes(b'123456')
    p = subprocess.run([sys.executable, str(HERE / 'miarchivos.py'), str(root), '--duplicates', '--compact'], capture_output=True, text=True, check=True)
    r = json.loads(p.stdout)
    assert r['schema'] == 'desarrollamo.miarchivos.v1'
    assert r['summary']['files'] == 3
    assert r['privacy']['files_modified'] is False
    assert r['privacy']['files_uploaded'] is False
    assert len(r['duplicates']['groups']) == 1
print('MiArchivos schema OK')
