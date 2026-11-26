#!/usr/bin/env python3
"""A- local automation: read-only remote observation, durable local receipts."""
import argparse, hashlib, json, os, re, sqlite3, subprocess, time
from pathlib import Path, PurePosixPath
from urllib.parse import quote
from datetime import datetime, timezone

REPOS=('www-infinity4/A-','www-infinity4/Moltnook','www-infinity4/QuantaPhi')
SEQ=';46&&&#)?$_jduuhf/+3&&5_+8;&'

def transform(data, seq):
    if seq != SEQ: raise ValueError('unsupported GH-1 sequence')
    b=bytearray(data)
    for i in range(3,len(b),46): b[i]=((b[i]^59^5)+8)%256
    return bytes(b)

def untransform(data, seq):
    if seq != SEQ: raise ValueError('unsupported GH-1 sequence')
    b=bytearray(data)
    for i in range(3,len(b),46): b[i]=((b[i]-8)%256)^59^5
    return bytes(b)

def digest(data): return hashlib.sha256(data).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')

def index_tree(tree):
    if tree.get('truncated') is not False or not isinstance(tree.get('tree'),list):
        raise ValueError('incomplete source tree')
    return sorted(e['path'] for e in tree['tree'] if e.get('type')=='blob' and e.get('mode') in ('100644','100755') and (PurePosixPath(e['path']).suffix.lower() in ('.py','.sh','.js','.mjs','.cjs','.ts','.go','.rs','.html') or e['path'].startswith('.github/workflows/')))

def open_db(path):
    db=sqlite3.connect(path,timeout=15)
    db.execute('pragma journal_mode=WAL')
    db.executescript('''CREATE TABLE IF NOT EXISTS runs(repo TEXT,id INTEGER,attempt INTEGER,sha TEXT,status TEXT,conclusion TEXT,url TEXT,workflow TEXT,seen TEXT,PRIMARY KEY(repo,id,attempt));
    CREATE TABLE IF NOT EXISTS checks(repo TEXT PRIMARY KEY,state TEXT,seen TEXT,detail TEXT);
    CREATE TABLE IF NOT EXISTS indexes(repo TEXT PRIMARY KEY,sha TEXT,paths TEXT,seen TEXT);
    ''')
    return db

def record_runs(db, repo, runs):
    with db:
        db.executemany('INSERT OR REPLACE INTO runs VALUES(?,?,?,?,?,?,?,?,?)',[(repo,r['databaseId'],r['attempt'],r['headSha'],r['status'],r.get('conclusion'),r['url'],r['workflowName'],now()) for r in runs])

def classify(runs):
    if not runs: return 'no_runs_observed'
    if any(r.get('conclusion') in ('failure','timed_out','action_required','startup_failure') for r in runs): return 'failure_observed'
    if any(r.get('status')!='completed' for r in runs): return 'pending'
    if all(r.get('conclusion')=='success' for r in runs): return 'sample_success_only'
    return 'mixed_or_unknown'

def api(path):
    p=subprocess.run(['gh','api','--method','GET',path],capture_output=True,text=True,timeout=45,check=True)
    return json.loads(p.stdout)

def observe(db, repo, request=api):
    try:
        response=request(f'repos/{repo}/actions/runs?per_page=30')
        items=response['workflow_runs']
        runs=[dict(databaseId=x['id'],attempt=x['run_attempt'],headSha=x['head_sha'],status=x['status'],conclusion=x['conclusion'],url=x['html_url'],workflowName=x['name']) for x in items]
        record_runs(db,repo,runs)
        state=classify(runs)
        meta=request(f'repos/{repo}')
        commit=request(f'repos/{repo}/commits/{quote(meta["default_branch"],safe="")}')
        tree=request(f'repos/{repo}/git/trees/{commit["commit"]["tree"]["sha"]}?recursive=1')
        paths=index_tree(tree)
        with db:
            db.execute('INSERT OR REPLACE INTO indexes VALUES(?,?,?,?)',(repo,commit['sha'],json.dumps(paths),now()))
            db.execute('INSERT OR REPLACE INTO checks VALUES(?,?,?,?)',(repo,state,now(),f'{len(runs)} latest runs sampled; {len(paths)} tracked program paths'))
        return True
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,subprocess.SubprocessError) as exc:
        with db: db.execute('INSERT OR REPLACE INTO checks VALUES(?,?,?,?)',(repo,'unknown',now(),type(exc).__name__))
        return False

def status(db):
    for row in db.execute('select * from checks order by repo'): print(*row,sep=' | ')
    print('\nObserved failures (latest recorded attempt per run; may be historical):')
    for row in db.execute('''select repo,id,attempt,sha,conclusion,url from runs r where attempt=(select max(attempt) from runs where repo=r.repo and id=r.id) and conclusion in ('failure','timed_out','action_required','startup_failure') order by seen desc limit 20'''): print(*row,sep=' | ')

def main():
    p=argparse.ArgumentParser(); p.add_argument('command',choices=['once','loop','status','index','hash']); p.add_argument('file',nargs='?'); p.add_argument('--interval',type=int,default=300); a=p.parse_args()
    if a.command=='hash':
        if not a.file: p.error('hash needs a file')
        b=Path(a.file).read_bytes(); print(json.dumps({'source_sha256':digest(b),'gh1_transformed_sha256':digest(transform(b,SEQ))})); return 0
    root=Path.home()/'.infinity'/'a-automation'; root.mkdir(mode=0o700,parents=True,exist_ok=True); os.umask(0o077)
    db=open_db(root/'ledger.sqlite3')
    if a.command=='status': status(db); return 0
    if a.command=='index':
        for repo,sha,paths,seen in db.execute('select * from indexes order by repo'): print(json.dumps({'repo':repo,'sha':sha,'paths':json.loads(paths),'observed_at':seen}))
        return 0
    if a.interval<60: p.error('minimum interval is 60 seconds')
    # Kernel lock releases even after a crash; no stale PID lock.
    import fcntl
    with open(root/'supervisor.lock','a') as lock:
        try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: print('Supervisor already active'); return 1
        while True:
            if a.command=='loop' and (root/'stop').exists(): return 0
            results=[observe(db,r) for r in REPOS]; status(db); print('Cycle observed:',now(),flush=True)
            if a.command=='once': return 0 if all(results) else 2
            for _ in range(a.interval):
                if (root/'stop').exists(): return 0
                time.sleep(1)
if __name__=='__main__': raise SystemExit(main())
