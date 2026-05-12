#!/usr/bin/env python3
import json, subprocess, time, sys
from pathlib import Path

OWNER='ai-village-agents'
REPO='the-universe'
RAW=Path('data/raw_prs.jsonl')
FILES=Path('data/pr_files.jsonl')
COMMENTS=Path('data/pr_comments.jsonl')

def gh_json(path):
    out=subprocess.check_output(['gh','api',path], text=True)
    return json.loads(out)

def load_done(path, key='number'):
    done=set()
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)[key])
    return done

prs=[json.loads(line) for line in RAW.read_text().splitlines() if line.strip()]
prs=sorted(prs, key=lambda r:r['number'])

files_done=load_done(FILES)
comments_done=load_done(COMMENTS)
with FILES.open('a') as ff, COMMENTS.open('a') as cf:
    for i,pr in enumerate(prs,1):
        n=pr['number']
        if n not in files_done:
            try:
                files=[]; page=1
                while True:
                    batch=gh_json(f'/repos/{OWNER}/{REPO}/pulls/{n}/files?per_page=100&page={page}')
                    if not batch: break
                    files.extend(batch); page+=1
                rec={'number':n,'files':[{'filename':f.get('filename'),'status':f.get('status'),'additions':f.get('additions'),'deletions':f.get('deletions'),'changes':f.get('changes')} for f in files]}
                ff.write(json.dumps(rec, sort_keys=True)+'\n'); ff.flush()
            except subprocess.CalledProcessError as e:
                print(f'files failed PR {n}: {e}', file=sys.stderr)
        if n not in comments_done:
            try:
                comments=[]; page=1
                while True:
                    batch=gh_json(f'/repos/{OWNER}/{REPO}/issues/{n}/comments?per_page=100&page={page}')
                    if not batch: break
                    comments.extend(batch); page+=1
                rec={'number':n,'comments':[{'user':c.get('user',{}).get('login'),'created_at':c.get('created_at'),'body':c.get('body','')} for c in comments]}
                cf.write(json.dumps(rec, sort_keys=True)+'\n'); cf.flush()
            except subprocess.CalledProcessError as e:
                print(f'comments failed PR {n}: {e}', file=sys.stderr)
        if i % 50 == 0:
            print(f'processed {i}/{len(prs)}')
        time.sleep(0.05)
print('done')
