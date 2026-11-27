"""Transactional, single-learner SQLite persistence."""
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .simulator import initial_state


def blank():
    return dict(read=False,quiz_pass=False,completed=False,bookmark=False,notes='',attempts=0,best_score=0,last_answers=None,lab=initial_state())

class Store:
    def __init__(self,path):
        self.path=str(path)
        Path(path).parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS lessons (id TEXT PRIMARY KEY, data TEXT NOT NULL)')
    def connect(self):
        db=sqlite3.connect(self.path,timeout=15)
        db.execute('PRAGMA journal_mode=WAL'); return db
    @contextmanager
    def edit(self,lesson_id):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT data FROM lessons WHERE id=?',(lesson_id,)).fetchone()
            state=json.loads(row[0]) if row else blank()
            yield state
            db.execute('INSERT INTO lessons VALUES (?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data',(lesson_id,json.dumps(state)))
    def get(self,lesson_id):
        with self.connect() as db:
            row=db.execute('SELECT data FROM lessons WHERE id=?',(lesson_id,)).fetchone()
            return json.loads(row[0]) if row else blank()
    def all(self,full=False):
        with self.connect() as db:
            rows=db.execute('SELECT id,data FROM lessons').fetchall()
        result={k:json.loads(v) for k,v in rows}
        if not full:
            result={k:{key:value for key,value in v.items() if key!='lab'}|{'tasks_done':v['lab']['done']} for k,v in result.items()}
        return result
