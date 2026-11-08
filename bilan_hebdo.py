"""Bilan hebdomadaire personnel, basé uniquement sur les données enregistrées."""
from datetime import date,timedelta,datetime
import csv,io,statistics
import streamlit as st
import pandas as pd
import moteur as m
import journal as j
import dashboard as dash

def summarize(end=None):
 end=end or date.today(); start=end-timedelta(days=6)
 lo,hi=start.isoformat(),end.isoformat()
 workouts=m.all_rows('SELECT planned_date,status,effort FROM workouts WHERE planned_date BETWEEN ? AND ?',(lo,hi))
 done=[x for x in workouts if x['status']=='done']
 calories=m.all_rows("""SELECT c.estimated_kcal,w.completed_at FROM calories c JOIN workouts w ON w.id=c.workout_id WHERE w.status='done' AND substr(w.completed_at,1,10) BETWEEN ? AND ?""",(lo,hi))
 foods=m.all_rows("""SELECT f.day, SUM(f.quantity*f.kcal_unit) kcal,SUM(f.quantity*COALESCE(x.protein,0)) protein,COUNT(*) n, SUM(CASE WHEN x.food_id IS NOT NULL THEN 1 ELSE 0 END) macros FROM food_log f LEFT JOIN food_macros x ON x.food_id=f.id WHERE f.day BETWEEN ? AND ? GROUP BY f.day ORDER BY f.day""",(lo,hi))
 steps=m.all_rows('SELECT day,steps FROM step_log WHERE day BETWEEN ? AND ? ORDER BY day',(lo,hi))
 weights=m.all_rows('SELECT substr(measured,1,10) day,AVG(weight) weight FROM measurements WHERE substr(measured,1,10) BETWEEN ? AND ? GROUP BY substr(measured,1,10) ORDER BY day',(lo,hi))
 previous=m.all_rows('SELECT AVG(weight) avg_weight FROM measurements WHERE substr(measured,1,10) BETWEEN ? AND ?',((start-timedelta(days=7)).isoformat(),(start-timedelta(days=1)).isoformat()))
 try: waist=m.all_rows('SELECT day,waist_cm FROM waist_log WHERE day BETWEEN ? AND ? ORDER BY day',(lo,hi))
 except Exception: waist=[]
 avg=lambda seq: round(statistics.mean(seq),1) if seq else None
 return {'start':lo,'end':hi,'planned':len(workouts),'done':len(done),'effort':avg([x['effort'] for x in done if x['effort'] is not None]),'sport_kcal':round(sum(x['estimated_kcal'] for x in calories)),'food_days':len(foods),'food_kcal_avg':avg([x['kcal'] for x in foods]),'protein_avg':avg([x['protein'] for x in foods]),'macro_days':sum(x['n']==x['macros'] for x in foods),'step_days':len(steps),'steps_avg':avg([x['steps'] for x in steps]),'weight_avg':avg([x['weight'] for x in weights]),'weight_previous':round(previous[0]['avg_weight'],1) if previous and previous[0]['avg_weight'] is not None else None,'weight_days':len(weights),'waist_first':waist[0]['waist_cm'] if waist else None,'waist_last':waist[-1]['waist_cm'] if waist else None,'waist_days':len(waist),'food':foods,'steps':steps,'weights':weights}

def advice(s):
 tips=[]
 if s['planned']:
  ratio=s['done']/s['planned']
  if ratio>=.8: tips.append('Belle régularité : tu as effectué au moins 80 % des séances prévues. Préserve aussi tes jours de repos.')
  elif ratio<.5: tips.append('Tu as réalisé moins de la moitié des séances prévues. Un planning un peu plus léger peut aider à retrouver de la constance.')
 else: tips.append('Aucune séance programmée cette semaine : crée un programme pour suivre ta régularité.')
 if s['effort'] is not None and s['effort']>=9: tips.append('Effort moyen très élevé : privilégie une récupération suffisante avant de chercher à augmenter l’intensité.')
 if s['step_days']<4:tips.append('Renseigne tes pas sur davantage de jours pour interpréter la tendance hebdomadaire.')


 if s['weight_days']<3:tips.append('Quelques pesées supplémentaires, prises dans des conditions comparables, rendront la tendance du poids plus utile.')
 if s['weight_avg'] is not None and s['weight_previous'] is not None:
  diff=s['weight_avg']-s['weight_previous']
  tips.append(('Le poids moyen a baissé' if diff<-.15 else 'Le poids moyen a augmenté' if diff>.15 else 'Le poids moyen est globalement stable')+f' ({diff:+.1f} kg par rapport à la semaine précédente). Ne tire pas de conclusion sur une seule semaine.')
 if s['waist_days']>=2:
  delta=s['waist_last']-s['waist_first']
  tips.append(f'Tour de taille : {delta:+.1f} cm entre les deux mesures extrêmes de la période. Vérifie la constance des conditions de mesure.')
 return tips

def page():
 st.title('📋 Mon bilan hebdomadaire')
 st.caption('Résumé personnalisé sur 7 jours, construit à partir des données réellement saisies. Aucune calorie ni perte de poids n’est inventée.')
 end=st.date_input('Dernier jour de la période',value=date.today(),max_value=date.today(),key='report_end')
 s=summarize(end)
 st.markdown(f'**Période : {s["start"]} → {s["end"]}**')
 a,b,c,d=st.columns(4)
 a.metric('Séances',f'{s["done"]}/{s["planned"]}')
 b.metric('Calories sport estimées',f'{s["sport_kcal"]} kcal')
 c.metric('Pas moyens enregistrés',f'{s["steps_avg"]:,.0f}' if s['steps_avg'] is not None else '—')
 d.metric('Poids moyen enregistré',f'{s["weight_avg"]:.1f} kg' if s['weight_avg'] is not None else '—')
 st.metric('Effort moyen des séances',f'{s["effort"]}/10' if s['effort'] is not None else '—')
 st.caption(f'Couverture : pas {s["step_days"]}/7 jours, poids {s["weight_days"]}/7 jours.')
 st.subheader('💬 Bilan du coach')
 for tip in advice(s):st.info(tip)
 st.subheader('📈 Évolution enregistrée')
 left,right=st.columns(2)
 with left:
  if s['steps']:st.bar_chart(pd.DataFrame(s['steps']).set_index('day')[['steps']],color='#912542')
  else:st.caption('Aucun nombre de pas renseigné sur cette période.')
 with right:
  if s['weights']:st.line_chart(pd.DataFrame(s['weights']).set_index('day')[['weight']],color='#912542')
  else:st.caption('Aucune pesée sur cette période.')
 output=io.StringIO();writer=csv.writer(output,delimiter=';')
 writer.writerow(['Indicateur','Valeur'])
 for key in ('start','end','planned','done','effort','sport_kcal','step_days','steps_avg','weight_days','weight_avg','weight_previous','waist_first','waist_last'):
  writer.writerow([key,s[key] if s[key] is not None else ''])
 st.download_button('📥 Exporter mon bilan hebdomadaire (CSV)',output.getvalue().encode('utf-8-sig'),f'fit_evolution_bilan_{s["end"]}.csv','text/csv')
