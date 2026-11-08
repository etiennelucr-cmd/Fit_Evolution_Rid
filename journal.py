"""Journal nutrition/pas et projection prudente du poids."""
from datetime import date, timedelta
import statistics
import moteur as m

FOODS = {'Pomme moyenne':95,'Banane moyenne':105,'Œuf':75,'Pain complet (tranche)':90,'Riz cuit (100 g)':130,'Poulet cuit (100 g)':165,'Pâtes cuites (100 g)':155,'Yaourt nature (125 g)':85,'Flocons d’avoine (40 g)':150,'Huile d’olive (1 c. à soupe)':120,'Lentilles cuites (100 g)':115,'Saumon cuit (100 g)':205}

def init():
 with m.connect() as c:
  c.execute('PRAGMA foreign_keys=ON')
  c.executescript('''CREATE TABLE IF NOT EXISTS food_log(id INTEGER PRIMARY KEY, day TEXT NOT NULL, meal TEXT NOT NULL, name TEXT NOT NULL, quantity REAL NOT NULL CHECK(quantity>0), kcal_unit REAL NOT NULL CHECK(kcal_unit>=0), created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
  CREATE INDEX IF NOT EXISTS idx_food_day ON food_log(day);
  CREATE TABLE IF NOT EXISTS step_log(day TEXT PRIMARY KEY, steps INTEGER NOT NULL CHECK(steps>=0), source TEXT NOT NULL DEFAULT 'manuel', updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
  CREATE TABLE IF NOT EXISTS food_macros(food_id INTEGER PRIMARY KEY REFERENCES food_log(id) ON DELETE CASCADE,protein REAL NOT NULL DEFAULT 0,carbs REAL NOT NULL DEFAULT 0,fat REAL NOT NULL DEFAULT 0);
  CREATE TABLE IF NOT EXISTS weight_goal(id INTEGER PRIMARY KEY CHECK(id=1), target_kg REAL NOT NULL);
  ''')

def add_food(day,meal,name,quantity,kcal_unit):
 name=name.strip()[:120]
 if not name or not 0<quantity<=100 or not 0<=kcal_unit<=3000:raise ValueError('Aliment, quantité ou calories invalides.')
 with m.connect() as c:c.execute('INSERT INTO food_log(day,meal,name,quantity,kcal_unit) VALUES(?,?,?,?,?)',(day,meal,name,float(quantity),float(kcal_unit)))

def add_food_macros(day,meal,name,quantity,kcal_unit,protein=0,carbs=0,fat=0):
 # Macronutrients per portion, saved atomically.
 name=name.strip()[:120]
 vals=(quantity,kcal_unit,protein,carbs,fat)
 if not name or not 0<float(quantity)<=100 or not 0<=float(kcal_unit)<=3000 or any(not 0<=float(v)<=500 for v in (protein,carbs,fat)):
  raise ValueError('Quantité, calories ou macronutriments invalides.')
 with m.connect() as c:
  cur=c.execute('INSERT INTO food_log(day,meal,name,quantity,kcal_unit) VALUES(?,?,?,?,?)',(day,meal,name,float(quantity),float(kcal_unit)))
  c.execute('INSERT INTO food_macros(food_id,protein,carbs,fat) VALUES(?,?,?,?)',(cur.lastrowid,float(protein),float(carbs),float(fat)))


def set_food_macros(food_id,protein,carbs,fat):
 vals=(protein,carbs,fat)
 if any(not 0<=float(v)<=500 for v in vals):raise ValueError('Macronutriments invalides')
 with m.connect() as c:
  if not c.execute('SELECT 1 FROM food_log WHERE id=?',(food_id,)).fetchone():raise ValueError('Aliment introuvable')
  c.execute('INSERT INTO food_macros(food_id,protein,carbs,fat) VALUES(?,?,?,?) ON CONFLICT(food_id) DO UPDATE SET protein=excluded.protein,carbs=excluded.carbs,fat=excluded.fat',(food_id,*map(float,vals)))

def add_food_product(day,meal,product,quantity):
 keys=('proteins','carbs','fat')
 if all(product.get(k) is not None for k in keys):
  add_food_macros(day,meal,product['name'],quantity,product['kcal_100g'],*(product[k] for k in keys))
 else:add_food(day,meal,product['name'],quantity,product['kcal_100g'])

def add_frequent_food(day,meal,food):
 with m.connect() as c:
  old=c.execute('SELECT x.protein,x.carbs,x.fat FROM food_log f JOIN food_macros x ON x.food_id=f.id WHERE f.name=? AND f.kcal_unit=? ORDER BY f.id DESC LIMIT 1',(food['name'],food['kcal_unit'])).fetchone()
 if old:add_food_macros(day,meal,food['name'],1,food['kcal_unit'],*old)
 else:add_food(day,meal,food['name'],1,food['kcal_unit'])

def foods_with_macros(day):
 return m.all_rows('''SELECT f.id,f.meal,f.name,f.quantity,f.kcal_unit,ROUND(f.quantity*f.kcal_unit,0) AS kcal,
 ROUND(f.quantity*COALESCE(x.protein,0),1) AS protein,
 ROUND(f.quantity*COALESCE(x.carbs,0),1) AS carbs,
 ROUND(f.quantity*COALESCE(x.fat,0),1) AS fat,
 x.food_id IS NOT NULL AS macros_known
 FROM food_log f LEFT JOIN food_macros x ON x.food_id=f.id WHERE f.day=? ORDER BY f.id DESC''',(day,))

def macro_history(days=30):
 start=(date.today()-timedelta(days=days-1)).isoformat()
 return m.all_rows('''SELECT f.day,ROUND(SUM(f.quantity*f.kcal_unit),0) AS kcal,
 ROUND(SUM(f.quantity*COALESCE(x.protein,0)),1) AS protein,
 ROUND(SUM(f.quantity*COALESCE(x.carbs,0)),1) AS carbs,
 ROUND(SUM(f.quantity*COALESCE(x.fat,0)),1) AS fat,
 COUNT(*) AS foods, SUM(CASE WHEN x.food_id IS NOT NULL THEN 1 ELSE 0 END) AS with_macros
 FROM food_log f LEFT JOIN food_macros x ON x.food_id=f.id WHERE f.day>=? GROUP BY f.day ORDER BY f.day''',(start,))

def delete_food(food_id):
 with m.connect() as c:c.execute('DELETE FROM food_log WHERE id=?',(food_id,))

def foods(day):return m.all_rows('SELECT id,meal,name,quantity,kcal_unit,ROUND(quantity*kcal_unit,0) AS kcal FROM food_log WHERE day=? ORDER BY id DESC',(day,))

def save_steps(day,steps):
 if not 0<=steps<=100000:raise ValueError('Nombre de pas invalide')
 with m.connect() as c:c.execute('INSERT INTO step_log(day,steps) VALUES(?,?) ON CONFLICT(day) DO UPDATE SET steps=excluded.steps,updated=CURRENT_TIMESTAMP',(day,int(steps)))

def steps(day):
 r=m.one('SELECT steps FROM step_log WHERE day=?',(day,));return r['steps'] if r else 0

def set_goal(kg):
 if not 30<=kg<=300:raise ValueError('Poids cible invalide')
 with m.connect() as c:c.execute('INSERT INTO weight_goal(id,target_kg) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET target_kg=excluded.target_kg',(kg,))

def goal():
 r=m.one('SELECT target_kg FROM weight_goal WHERE id=1');return float(r['target_kg']) if r else 60.0

def daily(days=30):
 start=(date.today()-timedelta(days=days-1)).isoformat()
 rows=m.all_rows('''SELECT d.day, COALESCE(f.kcal,0) AS calories, COALESCE(s.steps,0) AS steps, COALESCE(f.entries,0) AS entries
 FROM (SELECT day FROM food_log WHERE day>=? UNION SELECT day FROM step_log WHERE day>=?) d
 LEFT JOIN (SELECT day,SUM(quantity*kcal_unit) AS kcal,COUNT(*) AS entries FROM food_log GROUP BY day) f ON f.day=d.day
 LEFT JOIN step_log s ON s.day=d.day ORDER BY d.day''',(start,start))
 return rows

def weight_forecast():
 """Projection basée sur la tendance des pesées, jamais sur calories/pas seuls."""
 rows=m.all_rows('SELECT substr(measured,1,10) AS day, AVG(weight) AS weight FROM measurements GROUP BY substr(measured,1,10) ORDER BY day')
 if len(rows)<3:return {'status':'insufficient','message':'Ajoute au moins 3 pesées sur 14 jours ou plus pour afficher une tendance indicative.'}
 from datetime import date as dt
 last=dt.fromisoformat(rows[-1]['day'])
 recent=[r for r in rows if (last-dt.fromisoformat(r['day'])).days<=42]
 if len(recent)<3 or (dt.fromisoformat(recent[-1]['day'])-dt.fromisoformat(recent[0]['day'])).days<14:
  return {'status':'insufficient','message':'Il faut au moins 14 jours entre les premières et dernières pesées récentes pour une projection.'}
 xs=[(dt.fromisoformat(r['day'])-dt.fromisoformat(recent[0]['day'])).days for r in recent]
 ys=[float(r['weight']) for r in recent]
 xm=statistics.mean(xs);ym=statistics.mean(ys)
 denom=sum((x-xm)**2 for x in xs)
 slope=sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/denom if denom else 0
 # Les tendances extrêmes sont trop peu fiables pour extrapoler.
 if abs(slope)>0.18:return {'status':'unstable','message':'Variation récente trop importante pour une projection fiable. Continue les pesées et surveille la tendance.'}
 fitted=[ym+slope*(x-xm) for x in xs]
 residual=statistics.stdev([y-f for y,f in zip(ys,fitted)]) if len(ys)>2 else .3
 spread=max(.3,2*residual)
 current=ys[-1]
 return {'status':'ok','current':round(current,2),'weekly_change':round(slope*7,2),'tomorrow':round(current+slope,2),'week':round(current+7*slope,2),'uncertainty':round(spread,2),'observations':len(recent)}


def frequent_foods(limit=8):
 return m.all_rows('SELECT name,kcal_unit,COUNT(*) AS times FROM food_log GROUP BY name,kcal_unit ORDER BY times DESC,name LIMIT ?', (limit,))


def init_references():
 with m.connect() as db:
  db.execute('CREATE TABLE IF NOT EXISTS nutrition_references (name TEXT PRIMARY KEY COLLATE NOCASE,kcal_100g REAL NOT NULL,protein_100g REAL NOT NULL,carbs_100g REAL NOT NULL,fat_100g REAL NOT NULL)')

def save_reference(name,kcal,protein,carbs,fat):
 name=str(name).strip()[:120]
 values=[float(x) for x in (kcal,protein,carbs,fat)]
 if not name or not 0<=values[0]<=1000 or any(not 0<=v<=100 for v in values[1:]):
  raise ValueError('Nom ou valeurs nutritionnelles invalides.')
 init_references()
 with m.connect() as db:
  db.execute('INSERT INTO nutrition_references VALUES (?,?,?,?,?) ON CONFLICT(name) DO UPDATE SET kcal_100g=excluded.kcal_100g,protein_100g=excluded.protein_100g,carbs_100g=excluded.carbs_100g,fat_100g=excluded.fat_100g',(name,*values))

def references():
 init_references()
 return m.all_rows('SELECT * FROM nutrition_references ORDER BY name COLLATE NOCASE')

def add_reference_food(day,meal,reference,grams):
 grams=float(grams)
 if not 0<grams<=3000:raise ValueError('Quantité invalide.')
 add_food_macros(day,meal,reference['name'],grams/100,reference['kcal_100g'],reference['protein_100g'],reference['carbs_100g'],reference['fat_100g'])
