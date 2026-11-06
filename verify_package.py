from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parent
items=json.loads((r/'MANIFEST.json').read_text(encoding='utf-8'))
bad=[]
for x in items:
 p=r/x['path']
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:bad.append(x['path'])
print('Checked',len(items),'files; mismatches:',bad)
raise SystemExit(bool(bad))
