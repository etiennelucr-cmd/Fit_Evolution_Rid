"""Fonctions de coaching, habitudes et suivi. Compatible avec la base V2."""
import csv, io, json, sqlite3
from datetime import date, datetime, timedelta
import moteur as m

GUIDES={
'Pompes':('Mains sous les épaules, corps gainé, descendre sans creuser le dos.','Expirer en poussant.','Pompes contre un mur ou sur les genoux.'),
'Squats':('Pieds largeur épaules, hanches vers arrière, genoux alignés avec les pieds.','Inspirer en descendant, expirer en remontant.','Squat sur chaise.'),
'Gainage':('Aligner tête, bassin et talons, contracter abdominaux et fessiers.','Respirer sans bloquer.','Appui sur les genoux.'),
'Fentes':('Grand pas en arrière, buste droit, descendre de façon contrôlée.','Expirer en remontant.','Se tenir à une chaise stable.'),
'Pont fessier':('Allongé sur le dos, pieds au sol, pousser le bassin vers le haut.','Expirer à la montée.','Réduire l’amplitude.'),
'Cardio':('Bouger à une intensité permettant de rester en contrôle.','Garder une respiration régulière.','Marcher sur place.'),
'HIIT':('Rester souple sur les appuis et garder une exécution contrôlée.','Ralentir si la technique se dégrade.','Pas latéraux sans saut.'),
'Dos':('Stabiliser le bassin et mobiliser bras et jambes sans cambrer.','Respirer lentement.','Bird dog avec petite amplitude.')}
HABITS=['Bouger ou marcher','Boire régulièrement','Manger des végétaux','Respecter mon sommeil','Prendre un temps de récupération']
MOTIVATION=['La régularité vaut mieux que la perfection.','Chaque répétition bien exécutée compte.','Le repos fait partie de la progression.','Tu progresses à ton rythme, séance après séance.','Une séance adaptée vaut mieux qu’une séance forcée.']

def init():
 m.init()
 with m.connect() as c:
  c.executescript('''
  CREATE TABLE IF NOT EXISTS checkins (day TEXT PRIMARY KEY, energy INTEGER, sleep INTEGER, soreness INTEGER, mood INTEGER, note TEXT);
  CREATE TABLE IF NOT EXISTS habits (day TEXT NOT NULL, habit TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(day,habit));
  CREATE TABLE IF NOT EXISTS targets (name TEXT PRIMARY KEY, value REAL NOT NULL, unit TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS personal_records (id INTEGER PRIMARY KEY, day TEXT NOT NULL, name TEXT NOT NULL, value REAL NOT NULL, unit TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS preferences_v3 (key TEXT PRIMARY KEY, value TEXT NOT NULL);
  CREATE INDEX IF NOT EXISTS idx_workouts_program_date ON workouts(program_id,planned_date);
  CREATE INDEX IF NOT EXISTS idx_records_name_date ON personal_records(name,day);
  ''')

def save_checkin(energy,sleep,soreness,mood,note):
 with m.connect() as c:c.execute('INSERT INTO checkins VALUES (?,?,?,?,?,?) ON CONFLICT(day) DO UPDATE SET energy=excluded.energy,sleep=excluded.sleep,soreness=excluded.soreness,mood=excluded.mood,note=excluded.note',(date.today().isoformat(),energy,sleep,soreness,mood,note[:500]))

def today_checkin():return m.one('SELECT * FROM checkins WHERE day=?',(date.today().isoformat(),))

def readiness():
 r=today_checkin()
 if not r:return 'inconnu','Fais ton bilan forme avant la séance pour obtenir une suggestion adaptée.'
 if r['soreness']>=4 or r['energy']<=2 or r['sleep']<=2:return 'repos','Fatigue ou courbatures importantes : privilégie récupération, mobilité douce ou repos. Ne force pas.'
 if r['soreness']==3 or r['energy']==3:return 'modéré','Forme moyenne : réduis les séries ou la durée et conserve une intensité confortable.'
 return 'ok','Tu te sens prêt·e : suis ton programme, sans chercher l’épuisement.'

def save_habit(habit,done,day=None):
 if habit not in HABITS:raise ValueError('Habitude inconnue')
 with m.connect() as c:c.execute('INSERT INTO habits VALUES (?,?,?) ON CONFLICT(day,habit) DO UPDATE SET done=excluded.done',((day or date.today().isoformat()),habit,int(done)))

def habits_today():
 return {x['habit']:bool(x['done']) for x in m.all_rows('SELECT habit,done FROM habits WHERE day=?',(date.today().isoformat(),))}

def habit_count():return m.one('SELECT COUNT(*) n FROM habits WHERE done=1')['n']

def set_target(name,value,unit):
 if name not in ('Pompes','Gainage','Squats'):raise ValueError('Objectif inconnu')
 with m.connect() as c:c.execute('INSERT INTO targets VALUES (?,?,?) ON CONFLICT(name) DO UPDATE SET value=excluded.value,unit=excluded.unit',(name,float(value),unit))

def targets():return {r['name']:r for r in m.all_rows('SELECT * FROM targets')}

def add_record(name,value,unit):
 if name not in ('Pompes','Gainage','Squats'):raise ValueError('Mesure inconnue')
 if not 0<=float(value)<=10000:raise ValueError('Valeur incorrecte')
 with m.connect() as c:c.execute('INSERT INTO personal_records(day,name,value,unit) VALUES (?,?,?,?)',(date.today().isoformat(),name,float(value),unit))

def records():return m.all_rows('SELECT * FROM personal_records ORDER BY day,id')

def best_records():return {r['name']:r['best'] for r in m.all_rows('SELECT name,MAX(value) best FROM personal_records GROUP BY name')}

def save_pref(key,value):
 with m.connect() as c:c.execute('INSERT INTO preferences_v3 VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,json.dumps(value,ensure_ascii=False)))

def pref(key,default=None):
 r=m.one('SELECT value FROM preferences_v3 WHERE key=?',(key,))
 return json.loads(r['value']) if r else default

def workout_streak():
 """Nombre de séances accomplies d'affilée parmi les séances prévues jusqu'à aujourd'hui."""
 p=m.active_program()
 return m.streak(m.workouts(p['id'])) if p else 0

def summary():
 done=m.one("SELECT COUNT(*) n FROM workouts WHERE status='done'")['n']
 programs=m.one('SELECT COUNT(*) n FROM programs')['n']
 total=m.one('SELECT COUNT(*) n FROM workouts')['n']
 return {'done':done,'programs':programs,'planned':total,'habits':habit_count(),'streak':workout_streak(),'level':min(20,1+done//5)}

def recommendations():
 r=readiness()[0]; p=m.active_program()
 if r=='repos':return ['Aujourd’hui : récupération prioritaire. Les performances ne doivent pas passer avant la sécurité.']
 tips=[]
 if p:
  ws=m.workouts(p['id']); completed=[w for w in ws if w['status']=='done']
  if completed and completed[-1]['effort']>=9:tips.append('Dernière séance très intense : envisage une variante plus facile.')
  if len(completed)>=3 and all(w['effort']<=5 and w['technique']=='Bonne' for w in completed[-3:]):tips.append('Tes trois dernières séances semblent confortables : la progression automatique peut être pertinente.')
 if not tips:tips.append('Commence par un échauffement, privilégie la qualité et termine par un retour au calme.')
 return tips

def export_csv():
 out=io.StringIO(); w=csv.writer(out)
 w.writerow(['date','séance','statut','effort','technique','note'])
 for r in m.all_rows('SELECT planned_date,title,status,effort,technique,note FROM workouts ORDER BY planned_date'):
  w.writerow([r['planned_date'],r['title'],r['status'],r['effort'],r['technique'],r['note']])
 return out.getvalue().encode('utf-8-sig')

def weekly_report():
 cutoff=(date.today()-timedelta(days=6)).isoformat()
 rows=m.all_rows("SELECT * FROM workouts WHERE planned_date>=? AND planned_date<=?",(cutoff,date.today().isoformat()))
 done=[r for r in rows if r['status']=='done']
 return {'scheduled':len(rows),'done':len(done),'average_effort':round(sum(r['effort'] for r in done)/len(done),1) if done else None}
