"""Séances libres : génération, historique et estimation d'effort."""
import json, random
from datetime import datetime
import streamlit as st
import moteur as m
import mannequin
import guide_2d

EXOS={
'Pectoraux':[('Pompes sur les genoux','Poids du corps'),('Pompes classiques','Poids du corps'),('Développé couché au sol','Haltères'),('Pompes mains larges','Poids du corps')],
'Dos':[('Rowing un bras','Haltères'),('Rowing buste penché','Haltères'),('Superman alterné','Poids du corps'),('Oiseau sans charge','Poids du corps')],
'Épaules':[('Développé épaules contrôlé','Haltères'),('Cercles de bras','Poids du corps'),('Élévations frontales sans charge','Poids du corps'),('Pike push-up adapté','Poids du corps')],
'Biceps':[('Curl alterné','Haltères'),('Curl marteau','Haltères'),('Curl concentration','Haltères')],
'Triceps':[('Extension triceps un bras','Haltères'),('Pompes serrées adaptées','Poids du corps'),('Kickback triceps','Haltères')],
'Abdominaux':[('Roue abdominale à genoux, amplitude courte','Roue'),('Dead bug','Poids du corps'),('Gainage avant','Poids du corps'),('Crunch contrôlé','Poids du corps'),('Gainage latéral','Poids du corps')],
'Fessiers':[('Pont fessier','Poids du corps'),('Fentes arrière','Poids du corps'),('Soulevé de terre roumain','Haltères'),('Pont fessier une jambe','Poids du corps')],
'Cuisses':[('Squats','Poids du corps'),('Squat gobelet','Haltères'),('Fentes alternées','Poids du corps'),('Chaise au mur','Poids du corps')],
'Mollets':[('Montées sur pointes','Poids du corps'),('Montées sur pointes avec haltères','Haltères'),('Montées sur pointes unilatérales','Poids du corps')]
}

def init():
 with m.connect() as db:
  db.execute('CREATE TABLE IF NOT EXISTS free_sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, completed_at TEXT NOT NULL, duration INTEGER NOT NULL, difficulty TEXT NOT NULL, muscles TEXT NOT NULL, exercises TEXT NOT NULL, effort INTEGER NOT NULL, estimated_kcal INTEGER NOT NULL)')

def history():
 init()
 with m.connect() as db:
  return db.execute('SELECT * FROM free_sessions ORDER BY completed_at DESC').fetchall()

def generate(muscles, duration, difficulty, equipment):
 """Build a varied circuit with time-aware rounds and no adjacent duplicates."""
 pool=[]
 for muscle in muscles:
  for name,gear in EXOS[muscle]:
   if (equipment=='Sans matériel' and gear=='Poids du corps') or (equipment=='Avec matériel' and gear!='Poids du corps') or equipment=='Mixte':
    pool.append((muscle,name,gear))
 if not pool:return []
 random.shuffle(pool)
 # A movement is performed once per tour; each subsequent tour changes order.
 count=min(len(pool),max(3,round(duration/5)))
 count=max(1,count)
 selected=pool[:count]
 seconds_per_ex={'Débutant':90,'Intermédiaire':105,'Avancé':115}[difficulty]
 rounds=max(1,min(6,int((duration*60-240)/(count*seconds_per_ex))))
 rounds=max(1,rounds)
 reps={'Débutant':8,'Intermédiaire':12,'Avancé':15}[difficulty]
 plan=[]
 for tour in range(rounds):
  current=selected.copy()
  random.shuffle(current)
  if plan and len(current)>1 and plan[-1]['name']==current[0][1]:
   current.append(current.pop(0))
  for zone,name,gear in current:
   timed=any(t in name.lower() for t in ('gainage','chaise','cercles'))
   plan.append({'tour':tour+1,'zone':zone,'name':name,'gear':gear,'target':f'{30 if difficulty=="Débutant" else 40 if difficulty=="Intermédiaire" else 50} secondes' if timed else f'{reps} répétitions'})
 return plan

def page(profile):
 init()
 st.markdown('<div class="fe-free-hero"><h1>🦇 SÉANCE LIBRE · GOTHAM</h1><p>Choisis tes muscles, ta durée et ton niveau. Ton circuit s’adapte à ton matériel et varie à chaque génération.</p></div>',unsafe_allow_html=True)
 left,right=st.columns([1.2,1],gap='large')
 with left:
  st.markdown('<div class="fe-muscle-title">01 · Zones musculaires</div>',unsafe_allow_html=True)
  st.caption('Choisis une ou plusieurs zones musculaires sous le mannequin. Les exercices sont adaptés à tes choix.')
  if 'free_muscles' not in st.session_state:
   st.session_state.free_muscles=['Pectoraux','Abdominaux']
  if 'free_last_click' not in st.session_state:st.session_state.free_last_click=None
  for zone in EXOS:
   st.session_state.setdefault('free_zone_'+zone,zone in st.session_state.free_muscles)
  current=[zone for zone in EXOS if st.session_state['free_zone_'+zone]]
  clicked,coords=mannequin.choose(current)
  if coords is not None and coords!=st.session_state.free_last_click:
   st.session_state.free_last_click=coords
   if clicked:
    st.session_state['free_zone_'+clicked]=not st.session_state['free_zone_'+clicked]
    st.rerun()
  st.caption('👆 Touche un muscle sur la vue FACE ou DOS, ou utilise les cases ci-dessous.')
  zones=[]
  cols=st.columns(3)
  for i,zone in enumerate(EXOS):
   with cols[i%3]:
    if st.checkbox(zone,key='free_zone_'+zone):zones.append(zone)
  st.session_state.free_muscles=zones
  if zones: st.markdown('<div class="fe-dashboard-panel">🎯 <b>Zones ciblées :</b> '+ ' · '.join(zones)+'</div>',unsafe_allow_html=True)
  else: st.warning('Sélectionne au moins une zone musculaire.')
 with right:
  st.markdown('<div class="fe-muscle-title">02 · Paramètres</div>',unsafe_allow_html=True)
  duration=st.slider('Durée souhaitée',10,90,30,5,format='%d min')
  difficulty=st.segmented_control('Difficulté',['Débutant','Intermédiaire','Avancé'],default='Intermédiaire')
  equipment=st.radio('Matériel',['Mixte','Sans matériel','Avec matériel'],horizontal=True)
  st.caption('🏋️ 2 haltères de 7,5 kg chacun (charge adaptable) · roue abdominale · poids du corps. Ajuste la charge et l’amplitude à tes capacités.')
  st.markdown('<div class="fe-muscle-title">03 · Génération</div>',unsafe_allow_html=True)
  st.info('💡 Astuce : sélectionne 2 à 4 zones pour une séance équilibrée. Tu peux régénérer le circuit pour changer les exercices.')
  if st.button('⚡ GÉNÉRER MON CIRCUIT',type='primary',use_container_width=True,disabled=not zones):
   st.session_state['free_plan']=generate(zones,duration,difficulty,equipment)
   st.session_state['free_config']=(zones.copy(),duration,difficulty)
  if st.button('🎲 Séance surprise',use_container_width=True):
   chosen=random.sample(list(EXOS),k=random.randint(2,4))
   st.session_state['free_plan']=generate(chosen,duration,difficulty,equipment)
   st.session_state['free_config']=(chosen,duration,difficulty)
 plan=st.session_state.get('free_plan')
 if plan:
  zones_saved,duration_saved,diff_saved=st.session_state['free_config']
  st.subheader('🏋️ Ton circuit personnalisé')
  st.caption('🦇 Séance libre · '+str(duration_saved)+' min · '+diff_saved+' · '+', '.join(zones_saved))
  st.progress(min(1.0,len(set(x['name'] for x in plan))/max(1,len(plan))),text='Variété des mouvements dans le circuit')
  st.caption(f'{len(plan)} passages · {len(set(x["name"] for x in plan))} exercices distincts · environ {duration_saved} min avec échauffement et récupération')
  for tour in sorted(set(x['tour'] for x in plan)):
   with st.expander(f'🔁 Tour {tour}',expanded=tour==1):
    for i,ex in enumerate((x for x in plan if x['tour']==tour),1):
     st.markdown(f'**{i}. {ex["name"]}** · {ex["target"]} · {ex["zone"]} · {ex["gear"]}')
     st.caption('⏱️ 30 secondes de récupération après cet exercice')
  st.markdown('### 🎬 Coach animé et chronomètre · Séance libre')
  st.caption('Démarre le coach pour suivre ton circuit : démonstrations 3D indicatives, compte à rebours, pauses, récupération et passage automatique au mouvement suivant.')
  work_seconds=st.slider('Temps par exercice (hors exercices chronométrés)',20,120,45,5,key='free_coach_work')
  rest_seconds=st.slider('Récupération entre exercices (secondes)',0,90,30,5,key='free_coach_rest')
  guide_2d.show_free_plan(plan,diff_saved,work_seconds,rest_seconds)
  st.info('Prévois un échauffement. Arrête tout exercice douloureux. La durée est indicative : adapte le rythme à tes capacités.')
  with st.form('save_free_session'):
   actual=st.number_input('Minutes réellement effectuées',1,240,duration_saved)
   effort=st.slider('Effort ressenti (1–10)',1,10,6)
   met={'Débutant':3.5,'Intermédiaire':5.0,'Avancé':6.0}[diff_saved]
   weight=float(profile['weight']) if profile else 70.0
   kcal=m.estimate_calories(weight,actual,met)
   st.metric('🔥 Calories estimées (non mesurées)',f'{kcal} kcal')
   if st.form_submit_button('💾 Terminer et enregistrer',type='primary'):
    with m.connect() as db:
     db.execute('INSERT INTO free_sessions(completed_at,duration,difficulty,muscles,exercises,effort,estimated_kcal) VALUES(?,?,?,?,?,?,?)',(datetime.now().isoformat(timespec='seconds'),actual,diff_saved,json.dumps(zones_saved,ensure_ascii=False),json.dumps(plan,ensure_ascii=False),effort,kcal))
    del st.session_state['free_plan']
    st.success('Séance enregistrée dans ton historique !')
    st.rerun()
 st.subheader('📜 Historique des séances libres')
 rows=history()[:12]
 if not rows:st.caption('Aucune séance libre enregistrée pour le moment.')
 for h in rows:
  st.write(f'🦇 {h["completed_at"][:16]} · {h["duration"]} min · {h["difficulty"]} · Effort {h["effort"]}/10 · ~{h["estimated_kcal"]} kcal')
