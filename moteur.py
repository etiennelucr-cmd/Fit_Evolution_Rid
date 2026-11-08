import json
import sqlite3
from datetime import date, timedelta, datetime
from pathlib import Path

DB = Path(__file__).with_name('fit_evolution.db')
LEVELS = ['Débutant', 'Intermédiaire', 'Avancé']
EXERCISES = {
 'Pompes': {'beginner':'Pompes contre un mur','intermediate':'Pompes sur les genoux','advanced':'Pompes classiques','unit':'reps'},
 'Squats': {'beginner':'Squats sur chaise','intermediate':'Squats classiques','advanced':'Squats avec pause','unit':'reps'},
 'Gainage': {'beginner':'Gainage sur genoux','intermediate':'Gainage avant','advanced':'Gainage avec toucher épaule','unit':'sec'},
 'Fentes': {'beginner':'Fentes arrière assistées','intermediate':'Fentes arrière','advanced':'Fentes alternées contrôlées','unit':'reps'},
 'Pont fessier': {'beginner':'Pont fessier','intermediate':'Pont fessier avec pause','advanced':'Pont fessier une jambe alternée','unit':'reps'},
 'Cardio': {'beginner':'Marche rapide sur place','intermediate':'Montées de genoux sans saut','advanced':'Montées de genoux dynamiques','unit':'sec'},
 'HIIT': {'beginner':'Pas latéraux rapides','intermediate':'Jumping jacks sans saut','advanced':'Jumping jacks','unit':'sec'},
 'Dos': {'beginner':'Bird dog','intermediate':'Superman alterné','advanced':'Superman avec pause','unit':'reps'},
}
TEMPLATES = [
 ('Renforcement complet',['Squats','Pompes','Pont fessier','Gainage']),
 ('Cardio progressif',['Cardio','HIIT','Squats','Gainage']),
 ('Haut du corps & tronc',['Pompes','Dos','Gainage','Cardio']),
 ('Jambes & mobilité',['Fentes','Squats','Pont fessier','Gainage']),
]
MEALS = {
 'Omnivore': [
  ('Flocons d’avoine, yaourt et fruits','Poulet, riz et légumes','Omelette, pommes de terre et salade'),
  ('Pain complet, fromage blanc et banane','Salade de thon, pois chiches et crudités','Saumon, quinoa et brocoli'),
  ('Œufs, tartines et fruit','Dinde, semoule et légumes','Soupe de lentilles, pain et fromage')],
 'Végétarien': [
  ('Porridge au lait et fruits','Lentilles, riz et légumes','Omelette, salade et pain complet'),
  ('Yaourt, muesli et fruits','Bowl pois chiches et quinoa','Tofu sauté, nouilles et légumes'),
  ('Tartines, fromage et fruit','Chili sin carne et riz','Curry de lentilles et légumes')],
 'Végétalien': [
  ('Porridge au lait végétal et fruits','Lentilles, riz et légumes','Tofu sauté et légumes'),
  ('Tartines de purée de cacahuète et banane','Bowl pois chiches et quinoa','Chili sin carne et riz'),
  ('Yaourt soja, muesli et fruits','Curry de lentilles et riz','Soupe de haricots et pain complet')]
}

def connect():
 c=sqlite3.connect(DB)
 c.row_factory=sqlite3.Row
 c.execute('PRAGMA foreign_keys=ON')
 return c

def init():
 with connect() as c:
  c.executescript('''
  CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY CHECK(id=1), age INTEGER, height REAL, weight REAL, goal TEXT, level TEXT, days INTEGER, sessions_week INTEGER, duration INTEGER, diet TEXT, notes TEXT, updated TEXT);
  CREATE TABLE IF NOT EXISTS programs (id INTEGER PRIMARY KEY, created TEXT, start_date TEXT, days INTEGER, goal TEXT, status TEXT DEFAULT 'active');
  CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY, program_id INTEGER REFERENCES programs(id), day_no INTEGER, planned_date TEXT, title TEXT, details TEXT, status TEXT DEFAULT 'planned', completed_at TEXT, effort INTEGER, technique TEXT, note TEXT, UNIQUE(program_id,day_no));
  CREATE TABLE IF NOT EXISTS measurements (id INTEGER PRIMARY KEY, measured TEXT, weight REAL NOT NULL);
  CREATE TABLE IF NOT EXISTS meals (id INTEGER PRIMARY KEY, day TEXT, meal_type TEXT, name TEXT, UNIQUE(day,meal_type));
  CREATE TABLE IF NOT EXISTS adjustments (id INTEGER PRIMARY KEY, program_id INTEGER, workout_id INTEGER UNIQUE, delta INTEGER, created TEXT);
  CREATE TABLE IF NOT EXISTS goals (id INTEGER PRIMARY KEY CHECK(id=1), weekly_loss REAL NOT NULL DEFAULT 0.5);
  CREATE TABLE IF NOT EXISTS calories (workout_id INTEGER PRIMARY KEY, minutes REAL NOT NULL, met REAL NOT NULL, weight REAL NOT NULL, estimated_kcal REAL NOT NULL, created TEXT NOT NULL);
  INSERT OR IGNORE INTO goals(id,weekly_loss) VALUES(1,0.5);
  ''')

def one(sql, params=()):
 with connect() as c:
  r=c.execute(sql,params).fetchone()
  return dict(r) if r else None

def all_rows(sql, params=()):
 with connect() as c: return [dict(r) for r in c.execute(sql,params).fetchall()]

def profile(): return one('SELECT * FROM profile WHERE id=1')

def weekly_loss():
 r=one('SELECT weekly_loss FROM goals WHERE id=1')
 return float(r['weekly_loss']) if r else 0.5

def set_weekly_loss(value):
 if float(value) not in (0,0.25,0.5,0.75,1.0): raise ValueError('Objectif non valide')
 with connect() as c:c.execute('INSERT INTO goals(id,weekly_loss) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET weekly_loss=excluded.weekly_loss',(float(value),))

def milestones():
 done=one("SELECT COUNT(*) AS n FROM workouts WHERE status='done'")['n']
 return [x for x in (3,7,14,30,50,100) if done>=x]

def performance_summary():
 return all_rows("SELECT planned_date,title,effort,technique FROM workouts WHERE status='done' ORDER BY completed_at DESC LIMIT 15")

def save_profile(p):
 with connect() as c:
  c.execute('''INSERT INTO profile VALUES (1,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET age=excluded.age,height=excluded.height,weight=excluded.weight,goal=excluded.goal,level=excluded.level,days=excluded.days,sessions_week=excluded.sessions_week,duration=excluded.duration,diet=excluded.diet,notes=excluded.notes,updated=excluded.updated''',
  (p['age'],p['height'],p['weight'],p['goal'],p['level'],p['days'],p['sessions_week'],p['duration'],p['diet'],p['notes'],datetime.now().isoformat(timespec='seconds')))

def active_program(): return one("SELECT * FROM programs WHERE status='active' ORDER BY id DESC LIMIT 1")

def generate(p):
 if active_program(): raise ValueError('Archive le programme actif avant de créer un nouveau programme.')
 start=date.today()
 # Répartir les séances sur la semaine, en privilégiant les jours séparés.
 patterns={2:[0,3],3:[0,2,4],4:[0,2,4,6],5:[0,1,3,4,6],6:[0,1,2,3,4,5]}
 slots=patterns[int(p['sessions_week'])]
 with connect() as c:
  cur=c.execute('INSERT INTO programs(created,start_date,days,goal) VALUES (?,?,?,?)',(datetime.now().isoformat(timespec='seconds'),start.isoformat(),p['days'],p['goal']))
  pid=cur.lastrowid
  seq=0
  for d in range(p['days']):
   if d%7 not in slots: continue
   name,ex=TEMPLATES[seq%len(TEMPLATES)]
   if p['goal']=='Endurance / cardio' and seq%2==0: name,ex=TEMPLATES[1]
   # Objectif de perte = légère orientation cardio, jamais une hausse forcée de l'intensité.
   if weekly_loss()>=0.5 and seq%3==1: name,ex=TEMPLATES[1]
   details={'exercises':ex,'minutes':p['duration']}
   c.execute('INSERT INTO workouts(program_id,day_no,planned_date,title,details) VALUES(?,?,?,?,?)',(pid,d+1,(start+timedelta(days=d)).isoformat(),name,json.dumps(details,ensure_ascii=False)))
   seq+=1
 return pid

def workouts(pid): return all_rows('SELECT * FROM workouts WHERE program_id=? ORDER BY day_no',(pid,))

def difficulty(pid, workout_id):
 p=profile()
 base=LEVELS.index(p['level'])
 changes=one('SELECT COALESCE(SUM(delta),0) AS total FROM adjustments WHERE program_id=? AND workout_id<?',(pid,workout_id))['total']
 return max(0,min(8,base+changes))

def workout_details(w):
 p=profile(); rank=difficulty(w['program_id'],w['id'])
 variation='beginner' if rank<=1 else 'intermediate' if rank<=4 else 'advanced'
 sets=min(4,2+rank//3)
 duration=p['duration']
 result=[]
 for ex in json.loads(w['details'])['exercises']:
  info=EXERCISES[ex]
  if info['unit']=='sec': count=min(55,15+rank*5)
  else: count=min(20,6+rank*2)
  # Alterner les objectifs entre séries, sans changer brutalement la charge totale.
  # Ordre : mise en route, série plus exigeante, série intermédiaire, puis finition.
  offsets=[-2,2,-1,1]
  targets=[max(1, count+offsets[i]) for i in range(sets)]
  if info['unit']=='sec':
   targets=[max(10, min(55, count+5*offsets[i])) for i in range(sets)]
  result.append({'name':info[variation], 'sets':sets, 'count':count,'targets':targets,'unit':info['unit'],'rest':75 if rank<=2 else 60})
 # Les objectifs de poids ne doivent pas imposer plus de répétitions ni de HIIT.
 return result

def complete(wid,effort,technique,note):
 with connect() as c:
  w=c.execute('SELECT * FROM workouts WHERE id=?',(wid,)).fetchone()
  if not w or w['status']!='planned': raise ValueError('Séance introuvable ou déjà enregistrée.')
  if technique=='Douleur / gêne': delta=-1
  elif technique=='À améliorer' or effort>=9: delta=-1
  elif technique=='Bonne' and effort<=6: delta=1
  else: delta=0
  c.execute("UPDATE workouts SET status='done',completed_at=?,effort=?,technique=?,note=? WHERE id=?",(datetime.now().isoformat(timespec='seconds'),effort,technique,note[:500],wid))
  c.execute('INSERT INTO adjustments(program_id,workout_id,delta,created) VALUES(?,?,?,?)',(w['program_id'],wid,delta,datetime.now().isoformat(timespec='seconds')))
 return delta

def streak(ws):
 # Streak de séances prévues, en remontant depuis la dernière séance éligible.
 eligible=[w for w in ws if w['planned_date']<=date.today().isoformat()]
 n=0
 for w in reversed(eligible):
  if w['status']=='done': n+=1
  else: break
 return n

def archive(pid):
 with connect() as c:c.execute("UPDATE programs SET status='archived' WHERE id=?",(pid,))

def log_weight(value):
 with connect() as c:c.execute('INSERT INTO measurements(measured,weight) VALUES(?,?)',(datetime.now().isoformat(timespec='seconds'),value))

def weight_history(): return all_rows('SELECT measured,weight FROM measurements ORDER BY id')

def meals_for_day(day,diet):
 variants=MEALS[diet]
 index=(date.fromisoformat(day)-date(2020,1,1)).days%len(variants)
 return dict(zip(('Petit-déjeuner','Déjeuner','Dîner'),variants[index]))


# MET = equivalent metabolique; calcul approximatif de depense totale.
MET_OPTIONS = {
 'Renforcement léger (3,5 MET)':3.5,
 'Renforcement soutenu (5 MET)':5.0,
 'Circuit intense (7 MET)':7.0,
 'Cardio modéré (5 MET)':5.0,
 'Cardio soutenu (7 MET)':7.0,
 'HIIT soutenu (8 MET)':8.0,
}
def estimate_calories(weight_kg,minutes,met):
 """Dépense énergétique totale estimée, en kcal (inclut la dépense au repos)."""
 return round(float(met)*3.5*float(weight_kg)/200*float(minutes))

def save_calories(workout_id, minutes, met, weight_kg):
 kcal=estimate_calories(weight_kg,minutes,met)
 with connect() as conn:
  conn.execute('INSERT INTO calories(workout_id,minutes,met,weight,estimated_kcal,created) VALUES(?,?,?,?,?,?) ON CONFLICT(workout_id) DO UPDATE SET minutes=excluded.minutes,met=excluded.met,weight=excluded.weight,estimated_kcal=excluded.estimated_kcal,created=excluded.created',(workout_id,minutes,met,weight_kg,kcal,datetime.now().isoformat(timespec='seconds')))
 return kcal

def calories_history():
 return all_rows('SELECT c.*,w.title,w.completed_at FROM calories c JOIN workouts w ON w.id=c.workout_id WHERE w.status="done" ORDER BY w.completed_at DESC')
