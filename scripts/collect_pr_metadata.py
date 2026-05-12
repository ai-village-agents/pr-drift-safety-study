#!/usr/bin/env python3
"""Collect GitHub PR metadata for ai-village-agents/the-universe via gh api."""
import json, subprocess, time
from pathlib import Path

OWNER='ai-village-agents'
REPO='the-universe'
OUT=Path('data/raw_prs.jsonl')
OUT.parent.mkdir(parents=True, exist_ok=True)

def gh(path):
    cmd=['gh','api',path]
    return json.loads(subprocess.check_output(cmd, text=True))

prs=[]
page=1
while True:
    batch=gh(f'/repos/{OWNER}/{REPO}/pulls?state=all&per_page=100&page={page}')
    if not batch:
        break
    prs.extend(batch)
    print(f'page {page}: total {len(prs)}')
    page += 1
    time.sleep(0.2)

with OUT.open('w') as f:
    for pr in prs:
        rec={
            'number': pr['number'],
            'title': pr['title'],
            'state': pr['state'],
            'user': pr['user']['login'] if pr.get('user') else None,
            'created_at': pr['created_at'],
            'updated_at': pr['updated_at'],
            'closed_at': pr.get('closed_at'),
            'merged_at': pr.get('merged_at'),
            'merge_commit_sha': pr.get('merge_commit_sha'),
            'head_ref': pr['head']['ref'],
            'head_sha': pr['head']['sha'],
            'base_ref': pr['base']['ref'],
            'base_sha': pr['base']['sha'],
            'draft': pr.get('draft'),
            'html_url': pr['html_url'],
        }
        f.write(json.dumps(rec, sort_keys=True) + '\n')
print(f'wrote {OUT} with {len(prs)} PRs')
