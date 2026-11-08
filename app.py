"""Fit Evolution V6.1 - coach sportif maison sur iPhone et PC en Wi-Fi local."""
from datetime import date,timedelta
from pathlib import Path
import json
import security
import streamlit as st
import streamlit.components.v1 as components
import moteur as m
import coach as c
import gotham_radio as radio
import journal as j
import catalogue as cat
import dashboard as dash
import planning_plus as pp
import bilan_hebdo as bh
import guide_2d
import seance_libre as sl
st.set_page_config(page_title='Fit Evolution V6.1',page_icon='🦇',layout='wide',initial_sidebar_state='expanded')
security.require_login()
j.init()
c.init()
st.markdown(dash.STYLE,unsafe_allow_html=True)
NAV=['🏠 Tableau de bord','👤 Profil & objectifs','📅 Programme','🏋️ Séance guidée','🥗 Nutrition','🍎 Journal alimentaire & pas','🔎 Scanner & aliments','📊 Progression','🏆 Motivation','📚 Exercices','📻 Gotham Radio','📱 iPhone & PC','📈 Bilan coach','🗓️ Calendrier & rappels','👟 Objectifs de pas','✨ Encouragements','🥑 Macros & bilan 30 jours','📋 Mon bilan hebdomadaire']
GROUPS={
 '🏠 Accueil':[NAV[0]],
 '🏋️ Entraînement':[NAV[2],NAV[3],'🦇 Séance libre',NAV[9],NAV[13]],
 '📈 Progression':[NAV[7],NAV[12],NAV[14],NAV[17]],
 '🏆 Motivation':[NAV[8],NAV[15]],
 '⚙️ Paramètres':[NAV[1],NAV[10],NAV[11]],
}
def go_to_profile():
 st.session_state['fe_group']='⚙️ Paramètres'
 st.session_state['fe_page_⚙️ Paramètres']=NAV[1]

with st.sidebar:
 st.markdown('<div class="sidebar-brand">🦇 FIT EVOLUTION <small>V6.1</small><div class="sidebar-sub">GOTHAM TRAINING · ÉDITION 1989</div></div>',unsafe_allow_html=True)
 group=st.radio('Rubrique',list(GROUPS),key='fe_group',label_visibility='collapsed')
 pages=GROUPS[group]
 if len(pages)>1:
  page=st.radio('Pages',pages,key='fe_page_'+group,label_visibility='collapsed')
 else:page=pages[0]
 st.markdown('<div class="sidebar-footer">💪 Un jour après l’autre.<br>📱 iPhone + PC · PostgreSQL Supabase</div>',unsafe_allow_html=True)
 if st.button('🔒 Déconnexion',use_container_width=True):
  st.session_state.pop('authenticated',None);st.rerun()
dash.header()
radio.header_player()
p=m.profile(); prog=m.active_program(); ws=m.workouts(prog['id']) if prog else []

def msg():
 if m.weekly_loss()>=.75:st.warning('Une perte visée de 0,75 à 1 kg/semaine peut être inadaptée. L’application ne compense pas cet objectif par du HIIT intensif ni par des restrictions alimentaires.')

def save_session(w):
 with st.form('session_'+str(w['id'])):
  effort=st.slider('Effort ressenti (1 à 10)',1,10,6)
  technique=st.selectbox('Exécution des mouvements',['Bonne','À améliorer','Douleur / gêne'])
  note=st.text_area('Comment s’est passée ta séance ?',max_chars=500)
  st.markdown('**🔥 Estimation des calories de cette séance**')
  actual_minutes=st.number_input('Durée réellement effectuée (minutes)',min_value=1,max_value=240,value=int(p['duration']) if p else 30,step=1,key='mins_'+str(w['id']))
  activity=st.selectbox('Intensité / type de séance',list(m.MET_OPTIONS),index=2 if 'renforcement' in w['title'].lower() else 3,key='activity_'+str(w['id']))
  weight_kg=float(p['weight']) if p else 69.0
  met=m.MET_OPTIONS[activity]
  st.info(f'🔥 Environ **{m.estimate_calories(weight_kg,actual_minutes,met)} kcal** dépensées (estimation, pas une mesure).')
  if st.form_submit_button('✅ Enregistrer la séance',type='primary'):
   delta=m.complete(w['id'],effort,technique,note)
   kcal=m.save_calories(w['id'],actual_minutes,met,weight_kg)
   st.success(f'🔥 Dépense estimée enregistrée : {kcal} kcal')
   if technique=='Douleur / gêne':st.warning('Arrête les mouvements douloureux et demande un avis médical si nécessaire.')
   else:st.success('Séance enregistrée ! '+('La prochaine sera légèrement plus exigeante.' if delta>0 else 'La difficulté est adaptée.'))
   st.rerun()

def exercise_list(w):
 details=m.workout_details(w)
 if not details:
  st.info('Aucun exercice pour cette séance.')
  return
 rounds=max(ex['sets'] for ex in details)
 st.caption(f'🔁 Entraînement en circuit : {rounds} tours. Un passage par exercice, puis retour au premier. Récupération de 30 secondes entre les exercices.')
 for tour in range(rounds):
  with st.expander(f'🔁 Tour {tour+1} / {rounds}', expanded=tour==0):
   for ex in details:
    if tour>=ex['sets']:continue
    targets=ex.get('targets', [ex['count']]*ex['sets'])
    target=targets[tour] if tour<len(targets) else ex['count']
    unit='sec' if ex['unit']=='sec' else 'rép.'
    st.markdown(f"**{ex['name']} — {target} {unit}**")
    family=next((k for k in c.GUIDES if k.lower() in ex['name'].lower()),None)
    if family:
     a,b,d=c.GUIDES[family]
     st.caption(f'Technique : {a} · Respiration : {b} · Plus facile : {d}')
    st.caption('⏱️ Pause : 30 secondes avant le prochain exercice' if not (tour==rounds-1 and ex is details[-1]) else '🏁 Fin du circuit')

if page==NAV[11]:
 st.title('📱 Fit Evolution sur iPhone et PC')
 st.success('Une seule application hébergée sur ton PC Windows : tes deux appareils utilisent la même base de données.')
 st.markdown('**1.** Lance `Lancer_Fit_Evolution_Reseau.bat` sur le PC.\n\n**2.** Connecte ton iPhone au **même Wi-Fi**.\n\n**3.** Ouvre Safari et saisis l’adresse affichée dans la fenêtre du PC, par exemple `http://192.168.1.20:8501`.\n\n**4.** Connecte-toi avec ton mot de passe local.')
 st.info('Safari → Partager → Sur l’écran d’accueil : crée ton raccourci Fit Evolution.')
 st.warning('Le PC doit rester allumé. Utilise uniquement un Wi-Fi privé de confiance : la connexion HTTP locale n’est pas chiffrée. Ne publie jamais le port 8501 sur Internet.')
 st.subheader('🎵 Mes plateformes')
 a,b,d=st.columns(3)
 a.link_button('Apple Music','https://music.apple.com/')
 b.link_button('Spotify','https://open.spotify.com/')
 d.link_button('YouTube Music','https://music.youtube.com/')
 st.caption('Les plateformes s’ouvrent séparément ; la musique protégée par abonnement n’est pas importable dans le lecteur MP3.')
 st.subheader('🔄 Synchronisation')
 st.write('Les changements faits sur iPhone ou PC sont enregistrés dans `fit_evolution.db` sur le PC. Pour sauvegarder, ferme l’application puis copie cette base et le dossier `ma_musique/`.')

elif page==NAV[1]:
 st.title('👤 Mon profil & mes objectifs')
 st.caption('Tes paramètres servent à personnaliser le programme. Tu peux conserver ta base V2.')
 with st.form('profile'):
  a,b,d=st.columns(3)
  age=a.number_input('Âge',18,100,int(p['age']) if p else 30)
  height=b.number_input('Taille (cm)',120.,230.,float(p['height']) if p else 175.)
  weight=d.number_input('Poids (kg)',30.,300.,float(p['weight']) if p else 75.,step=.5)
  goals=['Remise en forme','Renforcement musculaire','Endurance / cardio','Recomposition corporelle']
  goal=st.selectbox('Objectif sportif',goals,index=goals.index(p['goal']) if p and p['goal'] in goals else 0)
  level=st.selectbox('Niveau',m.LEVELS,index=m.LEVELS.index(p['level']) if p else 0)
  a,b,d=st.columns(3)
  days=a.number_input('Durée du programme (jours)',7,180,int(p['days']) if p else 30)
  freq=b.slider('Séances / semaine',2,6,int(p['sessions_week']) if p else 3)
  duration=d.select_slider('Minutes par séance',options=[15,20,30,40,45,60],value=int(p['duration']) if p else 30)
  diets=['Omnivore','Végétarien','Végétalien']
  diet=p['diet'] if p else diets[0]
  losses=[0.,.25,.5,.75,1.]
  loss=st.selectbox('Perte visée par semaine',losses,index=losses.index(m.weekly_loss()),format_func=lambda v:'Maintien' if v==0 else f'{v:g} kg / semaine')
  notes=st.text_area('Restrictions, blessures, allergies (mémo uniquement ; pas de filtrage automatique)',value=p['notes'] if p else '')
  if st.form_submit_button('💾 Enregistrer',type='primary'):
   m.save_profile(dict(age=age,height=height,weight=weight,goal=goal,level=level,days=days,sessions_week=freq,duration=duration,diet=diet,notes=notes))
   m.set_weekly_loss(loss);st.rerun()
 msg()
 st.info('Un programme actif garde son calendrier initial : archive-le avant de générer un programme avec les nouveaux paramètres.')

elif not p and page==NAV[0]:
 dash.welcome()
 a,b=st.columns([1.25,1])
 with a:
  st.markdown('<div class="fe-panel"><h3>🎯 Ton parcours commence ici</h3><p>Configure ton profil pour débloquer ton programme, tes séances et ton suivi.</p></div>',unsafe_allow_html=True)
  st.button('👤 Configurer mon profil',type='primary',use_container_width=True,on_click=go_to_profile)
 with b:
  st.markdown('<div class="fe-panel"><h3>📋 Les prochaines étapes</h3><p>① Ton profil & tes objectifs<br>② Générer ton programme<br>③ Enregistrer ta première séance<br>④ Suivre tes progrès</p></div>',unsafe_allow_html=True)
 st.subheader('Ce que tu pourras suivre')
 a,b,d=st.columns(3)
 a.info('🏋️ Entraînements et calories estimées')
 b.info('👟 Objectifs de pas et suivi quotidien')
 d.info('📈 Poids, pas et tour de taille')

elif not p:
 st.title('🔓 Active ton espace personnel')
 st.info('Renseigne ton profil dans ⚙️ Paramètres → 👤 Profil & objectifs pour utiliser cette rubrique.')
 st.button('Aller au profil',type='primary',on_click=go_to_profile)

elif page==NAV[0]:
 dash.overview(p,prog,ws)
 pp.home_notice()
 st.markdown('<div class="hero"><h2>💪 Ta progression commence aujourd’hui</h2><p>Une séance à la fois. La constance compte plus que la perfection.</p></div>',unsafe_allow_html=True)
 s=c.summary();a,b,d,e=st.columns(4)
 a.metric('Séances accomplies',s['done']);b.metric('Streak 🔥',s['streak']);d.metric('Niveau ⭐',s['level']);e.metric('Habitudes validées',s['habits'])
 if prog:
  done=sum(w['status']=='done' for w in ws);st.progress(done/max(1,len(ws)),text=f'{done} / {len(ws)} séances terminées')
  upcoming=next((w for w in ws if w['status']=='planned'),None)
  if upcoming:st.info(f"Prochaine séance : **{upcoming['title']}** · prévue le {upcoming['planned_date']}")
  else:st.success('Programme terminé ! Tu peux archiver puis recommencer.')
 else:st.info('Ton premier programme t’attend dans « Programme ».')
 st.subheader('🩺 Bilan forme du jour')
 check=c.today_checkin()
 with st.form('checkin'):
  a,b,d,e=st.columns(4)
  energy=a.slider('Énergie',1,5,int(check['energy']) if check else 3)
  sleep=b.slider('Sommeil',1,5,int(check['sleep']) if check else 3)
  soreness=d.slider('Courbatures',1,5,int(check['soreness']) if check else 1)
  mood=e.slider('Moral',1,5,int(check['mood']) if check else 3)
  note=st.text_input('Note personnelle',value=check['note'] if check else '')
  if st.form_submit_button('Enregistrer mon état'):c.save_checkin(energy,sleep,soreness,mood,note);st.rerun()
 status,advice=c.readiness();(st.warning if status=='repos' else st.info)(advice)
 st.subheader('🌱 Mes petites habitudes')
 existing=c.habits_today()
 for h in c.HABITS:
  checked=st.checkbox(h,value=existing.get(h,False),key='habit_'+h)
  if checked!=existing.get(h,False):c.save_habit(h,checked);st.rerun()
 st.caption(c.MOTIVATION[date.today().toordinal()%len(c.MOTIVATION)])

elif page==NAV[2]:
 st.title('📅 Mon programme personnalisé')
 if not prog:
  st.write(f"**{p['days']} jours** · **{p['sessions_week']} séances / semaine** · **{p['duration']} min** · {p['level']}")
  if st.button('✨ Générer mon programme',type='primary'):m.generate(p);st.rerun()
 else:
  done=sum(w['status']=='done' for w in ws)
  st.progress(float(done)/max(1,len(ws)),text=f'{done}/{len(ws)} séances · {100*done/max(1,len(ws)):.1f} %')
  week=st.selectbox('Semaine',list(range(1,(prog['days']+6)//7+1)),format_func=lambda x:f'Semaine {x}')
  start=(week-1)*7
  calendar=[]
  for i in range(start,min(start+7,prog['days'])):
   day=date.fromisoformat(prog['start_date'])+timedelta(days=i)
   w=next((x for x in ws if x['day_no']==i+1),None)
   calendar.append({'Date':day.strftime('%a %d/%m'),'Jour':i+1,'Activité':w['title'] if w else 'Récupération','État':'✅ Fait' if w and w['status']=='done' else '🏋️ À faire' if w else '🧘 Repos'})
  st.markdown(calendar.to_html(index=False,classes='gotham-table',border=0,escape=True) if hasattr(calendar,'to_html') else __import__('pandas').DataFrame(calendar).to_html(index=False,classes='gotham-table',border=0,escape=True),unsafe_allow_html=True)
  for w in ws:
   if start < w['day_no'] <= start+7:
    with st.expander(('✅ ' if w['status']=='done' else '🏋️ ')+f"Jour {w['day_no']} · {w['title']}"):
     exercise_list(w)
     if w['status']=='done':st.success(f"Terminée · effort {w['effort']}/10")
     elif w['planned_date']<=date.today().isoformat():save_session(w)
     else:st.caption('Séance planifiée pour plus tard.')
  with st.expander('⚙️ Archiver ce programme'):
   st.warning('L’archivage conserve toutes les données.')
   if st.button('Archiver et préparer un nouveau programme'):m.archive(prog['id']);st.rerun()

elif page=='🦇 Séance libre':
 sl.page(p)
elif page==NAV[3]:
 st.title('🏋️ Ma séance guidée')
 status,advice=c.readiness();(st.warning if status=='repos' else st.info)(advice)
 st.caption('La radio YouTube est accessible dans Paramètres → Gotham Radio. Elle peut s’arrêter lors d’un changement de page.')
 next_w=next((w for w in ws if w['status']=='planned' and w['planned_date']<=date.today().isoformat()),None)
 if not next_w:
  st.info('Aucune séance actuellement due. Vérifie ton programme ou profite de la récupération.')
 else:
  st.subheader(next_w['title']);st.caption('Échauffement doux 3–5 minutes · technique d’abord · retour au calme 3–5 minutes')
  details=m.workout_details(next_w)
  exercise_list(next_w)
  if status=='repos':st.warning('Le bilan forme recommande de ne pas forcer aujourd’hui. Tu peux reporter cette séance.')
  st.subheader('🔥 Coach interactif · Avatar 3D animé')
  st.caption('La difficulté dépend de ton niveau et de ton ressenti, jamais de ton objectif de perte de poids. Vise une technique propre et un effort soutenu, pas l’épuisement.')
  if status=='repos':
   st.error('Ton bilan forme recommande du repos : le mode intensif est désactivé aujourd’hui.')
  else:
   previous=c.pref('challenge_rpe',None)
   if previous is not None:
    st.info(f'Dernier effort ressenti enregistré : {previous}/10. Ajuste le circuit à tes capacités et à ta récupération.')
   mode=st.radio('Format de séance',['Programme original','Circuit dynamique','Challenge avancé'],horizontal=True,key='fe_challenge_mode')
   if mode=='Programme original':
    work=st.slider('Effort par série (secondes)',15,90,35,5,key='fe_work')
    rest=st.slider('Récupération (secondes)',10,90,30,5,key='fe_rest')
    guided=details
   else:
    advanced=mode=='Challenge avancé'
    work=st.slider('Effort par atelier (secondes)',20,60,45 if advanced else 35,5,key='fe_work')
    rest=st.slider('Récupération (secondes)',15,75,25 if advanced else 30,5,key='fe_rest')
    rounds=st.slider('Nombre de tours',2,5,3 if advanced else 2,key='fe_rounds')
    circuit=[('Squats classiques','squat'),('Pompes classiques','pushup'),('Fentes alternées contrôlées','lunge'),('Mountain climbers','mountain'),('Gainage avant','plank')]
    if advanced:circuit.insert(3,('Burpees adaptés','burpee'))
    guided=[{'name':name,'sets':rounds,'count':work,'unit':'sec','rest':rest} for name,_ in circuit]
    st.info(f'Circuit : {len(circuit)} ateliers × {rounds} tours · {work} s effort / {rest} s repos. Commence plus lentement si la technique se dégrade.')
    st.warning('Les circuits sont des propositions, pas une prescription personnalisée. Adapte les impacts et interromps en cas de douleur, vertige ou malaise.')
   guide_2d.show(guided,work,rest)
   with st.expander('🎯 Évaluer la difficulté et ajuster la prochaine séance'):
    with st.form('fe_challenge_feedback'):
     rpe=st.slider('Effort ressenti (0 = aucun effort, 10 = maximal)',0.0,10.0,7.0,0.5)
     technique_ok=st.checkbox('J’ai conservé une bonne technique',value=True)
     if st.form_submit_button('Enregistrer mon ressenti'):
      c.save_pref('challenge_rpe',rpe)
      if not technique_ok:st.warning('Privilégie la qualité du mouvement et augmente la récupération avant de chercher plus de difficulté.')
      elif rpe<4:st.success('Séance facile : essaie un tour supplémentaire ou 5 secondes d’effort en plus la prochaine fois, sans tout augmenter d’un coup.')
      elif rpe>8:st.info('Séance très intense : maintiens ou réduis la charge et accorde-toi suffisamment de récupération.')
      else:st.success('Bonne zone d’effort : conserve ce niveau jusqu’à ce que le circuit devienne plus facile.')
  st.info('Le suivi animé fonctionne dans le navigateur, sans connexion Internet. Le minuteur reste actif tant que cette page est ouverte. Pour enregistrer le bilan dans SQLite et gagner des XP, utilise le formulaire sous le coach.')
  st.divider();save_session(next_w)

elif page==NAV[7]:
 st.title('📊 Ma progression')
 s=c.summary();a,b,d=st.columns(3);a.metric('Séances',s['done']);b.metric('Niveau',s['level']);d.metric('Streak',s['streak'])
 with st.form('weight'):
  weight=st.number_input('Nouvelle pesée (kg)',30.,300.,float(p['weight']),step=.1)
  if st.form_submit_button('Enregistrer mon poids'):m.log_weight(weight);st.rerun()
 history=m.weight_history()
 if history:
  import pandas as pd
  df=pd.DataFrame(history);df['Date']=pd.to_datetime(df['measured'])
  import altair as alt
  df['Poids']=pd.to_numeric(df['weight'],errors='coerce')
  chart=alt.Chart(df.dropna(subset=['Poids'])).mark_line(color='#f4c747',strokeWidth=3,point=True).encode(
   x=alt.X('Date:T',axis=alt.Axis(format='%d/%m',labelAngle=0,labelOverlap=True,tickCount=5,labelColor='#d5cdbd',gridColor='#283541',title=None)),
   y=alt.Y('Poids:Q',scale=alt.Scale(zero=False),axis=alt.Axis(labelColor='#d5cdbd',gridColor='#283541',title='kg')),
   tooltip=['Date:T','Poids:Q']).properties(height=290,background='#111923').configure_view(strokeOpacity=0)
  st.altair_chart(chart,use_container_width=True,theme=None)
  if len(history)>1:st.metric('Évolution depuis la première pesée',f"{history[-1]['weight']-history[0]['weight']:+.1f} kg")
 cal_hist=m.calories_history()
 if cal_hist:
  st.subheader('🔥 Calories estimées dépensées')
  st.metric('Total enregistré',f"{sum(r['estimated_kcal'] for r in cal_hist):.0f} kcal")
  st.caption('Estimations MET, repos inclus. Ne pas interpréter comme des calories à manger en plus.')
  import pandas as pd
  cal_df=pd.DataFrame(cal_hist)
  cal_df['Séance']=cal_df['completed_at'].str[:10]+' #'+cal_df['workout_id'].astype(str)
  st.bar_chart(cal_df.set_index('Séance')['estimated_kcal'])
 st.subheader('🔮 Tendance du poids (indicative)')
 with st.form('goal_weight'):
  target=st.number_input('Mon poids cible (kg)',30.0,300.0,float(j.goal()),0.5)
  if st.form_submit_button('Enregistrer mon objectif de poids'):j.set_goal(target);st.rerun()
 fc=j.weight_forecast()
 if fc['status']=='ok':
  a,b,d=st.columns(3)
  a.metric('Dernière pesée',f'{fc["current"]:.1f} kg')
  b.metric('Tendance demain',f'{fc["tomorrow"]:.1f} kg')
  d.metric('Tendance dans 7 jours',f'{fc["week"]:.1f} kg')
  st.caption(f'Tendance observée : {fc["weekly_change"]:+.2f} kg/semaine sur {fc["observations"]} pesées. Incertitude indicative au moins ±{fc["uncertainty"]:.1f} kg, souvent davantage au jour le jour. Ce n’est pas une prédiction de la balance demain.')
 else:st.info(fc['message'])
 st.caption('Les projections reposent uniquement sur la tendance des pesées, pas sur une conversion automatique des pas ou calories en kilos. Hydratation, sel, digestion et entraînement influencent fortement le poids du lendemain.')
 st.subheader('🎯 Records et objectifs sportifs')
 t=c.targets();best=c.best_records()
 for name,unit in [('Pompes','répétitions'),('Gainage','secondes'),('Squats','répétitions')]:
  with st.expander(f"{name} · record {best.get(name,'—')} · objectif {t[name]['value'] if name in t else '—'}"):
   goal=st.number_input(f'Objectif {name}',1,1000,int(t[name]['value']) if name in t else (20 if name!='Gainage' else 60),key='target_'+name)
   if st.button('Enregistrer objectif',key='save_target_'+name):c.set_target(name,goal,unit);st.rerun()
   achieved=st.number_input(f'Ma performance actuelle ({unit})',0,1000,0,key='record_'+name)
   if st.button('Ajouter une performance',key='save_record_'+name):c.add_record(name,achieved,unit);st.rerun()
   if name in t and name in best:st.progress(min(1,best[name]/max(1,t[name]['value'])))
 records=c.records()
 if records:st.dataframe(records,hide_index=True,use_container_width=True)
 st.subheader('📆 Bilan des 7 derniers jours')
 report=c.weekly_report();st.write(f"{report['done']} séance(s) terminée(s) sur {report['scheduled']} prévue(s) · effort moyen : {report['average_effort'] if report['average_effort'] is not None else '—'}/10")
 st.download_button('📥 Exporter mon historique de séances (CSV)',c.export_csv(),'fit_evolution_seances.csv','text/csv')

elif page==NAV[8]:
 st.title('🏆 Motivation & récompenses')
 s=c.summary();st.metric('Niveau Fit Evolution',s['level']);st.metric('Série de séances',s['streak']);st.metric('Habitudes cochées',s['habits'])
 for n in [3,7,14,30,50,100]:st.write(('🏅' if s['done']>=n else '🔒')+f' {n} séances accomplies')
 st.subheader('💬 Ton coach te conseille')
 for tip in c.recommendations():st.info(tip)
 st.success(c.MOTIVATION[date.today().toordinal()%len(c.MOTIVATION)])
 st.caption('Les jours de repos ne sont pas des échecs. Le streak mesure la continuité des séances prévues, pas une obligation de s’entraîner tous les jours.')

elif page==NAV[9]:
 st.title('📚 Bibliothèque des exercices')
 st.caption('Consignes textuelles et variantes maison. En cas de doute sur la technique, demande conseil à un professionnel qualifié.')
 for name,(technique,breath,easier) in c.GUIDES.items():
  with st.expander(name):
   st.write('**Technique :**',technique);st.write('**Respiration :**',breath);st.write('**Variante plus facile :**',easier)
   if name in m.EXERCISES:
    info=m.EXERCISES[name]
    st.write('**Progressions :**',info['beginner'],'→',info['intermediate'],'→',info['advanced'])

if p and page==NAV[12]:
 dash.coach_page(p,prog,ws)
if page==NAV[10]:
 radio.page()

if page==NAV[13]:
 pp.calendar_page(prog,ws)
elif page==NAV[14]:
 pp.steps_page()
elif page==NAV[15]:
 pp.motivation_page()

if page==NAV[17] and p:
 bh.page()
