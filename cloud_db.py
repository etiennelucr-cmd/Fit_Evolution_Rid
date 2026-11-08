"""PostgreSQL adapter for legacy SQLite-shaped queries."""
import re
from contextlib import contextmanager
import streamlit as st
from psycopg import connect as pg_connect
from psycopg.rows import dict_row

class Row(dict):
    def __getitem__(self, key):
        if isinstance(key, int): return list(self.values())[key]
        return super().__getitem__(key)

class Cursor:
    def __init__(self, cur):
        self.cur = cur
        self.lastrowid = None
        if cur.description and cur.description[-1].name == '_inserted_id':
            record = cur.fetchone()
            self.lastrowid = record['_inserted_id'] if record else None
    def fetchone(self):
        v = self.cur.fetchone()
        return Row(v) if v is not None else None
    def fetchall(self): return [Row(v) for v in self.cur.fetchall()]
    def __iter__(self): return iter(self.fetchall())

class Connection:
    def __init__(self, raw): self.raw=raw
    def __enter__(self): self.raw.__enter__(); return self
    def __exit__(self,*args): return self.raw.__exit__(*args)
    def executescript(self, script):
        for stmt in script.split(';'):
            if stmt.strip(): self.execute(stmt)
    def execute(self, sql, params=()):
        sql=sql.strip()
        if self.raw.execute('SELECT current_schema()').fetchone()['current_schema'] != 'fit_evolution':
            raise RuntimeError('Connexion hors du schéma fit_evolution : opération refusée.')
        if re.search(r'(?i)\b(?:SET\s+(?:LOCAL\s+)?search_path|CREATE\s+SCHEMA|DROP\s+SCHEMA|ALTER\s+SCHEMA|(?:public|auth|storage)\s*\.)', sql):
            raise RuntimeError('Requête hors du schéma fit_evolution refusée.')
        if sql.upper().startswith('PRAGMA '): return Cursor(self.raw.execute('SELECT 1'))
        # Keep fixed or externally referenced identifiers non-serial.
        # Other SQLite integer primary keys require generated IDs in PostgreSQL.
        if re.match(r'CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(?:profile|goals|calories|food_macros|weight_goal)\b', sql, re.I):
            sql=re.sub(r'\bINTEGER PRIMARY KEY\b', 'INTEGER PRIMARY KEY', sql, flags=re.I)
        else:
            sql=re.sub(r'\bINTEGER PRIMARY KEY(?: AUTOINCREMENT)?\b', 'BIGSERIAL PRIMARY KEY', sql, flags=re.I)
        sql=re.sub(r'\bCOLLATE NOCASE\b','',sql,flags=re.I)
        sql=re.sub(r'\browid\b','id',sql,flags=re.I)
        sql=re.sub(r'INSERT OR IGNORE INTO (\w+)',r'INSERT INTO \1',sql,flags=re.I)
        if re.search(r'INSERT INTO (goals|music_playlists)\s*\(',sql,re.I) and 'ON CONFLICT' not in sql.upper():
            sql+=' ON CONFLICT DO NOTHING'
        sql=re.sub(r'(?<![\w])\?', '%s',sql)
        # Psycopg uses double quotes for identifiers, never for string values.
        sql=sql.replace('status="done"',"status='done'")
        if re.match(r'INSERT INTO (programs|food_log|music_playlists|personal_records|measurements|adjustments|fe_reminders|free_sessions)\b',sql,re.I) and 'RETURNING' not in sql.upper():
            sql+=' RETURNING id AS _inserted_id'
        return Cursor(self.raw.execute(sql,params))

def connect():
    if 'postgres' not in st.secrets:
        raise RuntimeError('Configurer [postgres] dans les secrets Streamlit Cloud avant de lancer Fit Evolution.')
    cfg=st.secrets['postgres']
    raw=pg_connect(host=cfg['host'],port=int(cfg.get('port',5432)),dbname=cfg.get('dbname','postgres'),
                   user=cfg['user'],password=cfg['password'],sslmode='require',connect_timeout=12,
                   options='-csearch_path=fit_evolution',row_factory=dict_row)
    # Fail closed: never execute application SQL in the public schema.
    active = raw.execute('SELECT current_schema() AS schema').fetchone()['schema']
    if active != 'fit_evolution':
        raw.close()
        raise RuntimeError('Schéma fit_evolution absent ou inaccessible. Créez-le dans Supabase avant de lancer l’application.')
    return Connection(raw)
