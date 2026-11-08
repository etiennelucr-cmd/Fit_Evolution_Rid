"""Calendrier, objectifs de pas et rappels non intrusifs (locaux)."""
from datetime import date,timedelta
import calendar
import streamlit as st
import pandas as pd
import moteur as m
import journal as j
import coach as c

def init():
 with m.connect() as db:
  db.execute("CREATE TABLE IF NOT EXISTS fe_preferences (name TEXT PRIMARY KEY, value TEXT NOT NULL)")
  db.execute("CREATE TABLE IF NOT EXISTS fe_reminders (id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT NOT NULL, message TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)")

def get(name,default):
 row=m.one('SELECT value FROM fe_preferences WHERE name=?',(name,))
 return row['value'] if row else default

def set_pref(name,value):
 with m.connect() as db:db.execute('INSERT INTO fe_preferences(name,value) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET value=excluded.value',(name,str(value)))

def add_reminder(day,message):
 if not message.strip():return
 with m.connect() as db:db.execute('INSERT INTO fe_reminders(day,message) VALUES(?,?)',(day,message.strip()[:180]))

def reminders():return m.all_rows('SELECT * FROM fe_reminders ORDER BY day,id')

def mark_reminder(id,done):
 with m.connect() as db:db.execute('UPDATE fe_reminders SET done=? WHERE id=?',(int(done),id))

def calendar_page(prog,ws):
 import seance_libre as sl
 st.title('🗓️ Mon calendrier sportif')
 st.caption('Calendrier mensuel : entraînements, récupération, séances réalisées et rappels personnels.')
 today=date.today(); choice=st.date_input('Mois à afficher',today,key='fe_calendar_month'); y,mo=choice.year,choice.month
 by_day={w['planned_date']:w for w in ws}
 reminders_by_day={}
 for r in reminders():reminders_by_day.setdefault(r['day'],[]).append(r)
 weeks=calendar.Calendar(firstweekday=0).monthdatescalendar(y,mo)
 st.markdown(f'### {calendar.month_name[mo]} {y}')
 cols=st.columns(7)
 for col,dayname in zip(cols,['Lun','Mar','Mer','Jeu','Ven','Sam','Dim']):col.markdown('**'+dayname+'**')
 for week in weeks:
  cols=st.columns(7)
  for col,d in zip(cols,week):
   key=d.isoformat();w=by_day.get(key)
   with col:
    if d.month!=mo:st.caption(str(d.day));continue
    if w: symbol='✅' if w['status']=='done' else '🏋️';name=w['title'][:19]
    else:symbol='🌿';name='Repos' if prog and date.fromisoformat(prog['start_date'])<=d<date.fromisoformat(prog['start_date'])+timedelta(days=prog['days']) else '—'
    st.markdown(f'**{d.day}** {symbol}')
    st.caption(name)
    free=[f for f in sl.history() if f['completed_at'][:10]==key]
    if free:st.caption(f'🦇 {len(free)} séance(s) libre(s) · '+str(sum(f['duration'] for f in free))+' min')
    if reminders_by_day.get(key):st.caption('🔔 '+str(len(reminders_by_day[key]))+' rappel(s)')
 st.divider()
 st.subheader('🔔 Mes rappels personnels')
 st.caption('Les rappels apparaissent dans Fit Evolution lorsque tu ouvres l’application ; ils ne sont pas envoyés en notification iPhone ou Windows.')
 with st.form('fe_add_reminder'):
  when=st.date_input('Date du rappel',today)
  message=st.text_input('Message',placeholder='Ex. : mesurer mon tour de taille',max_chars=180)
  if st.form_submit_button('Ajouter le rappel'):
   if message.strip():add_reminder(when.isoformat(),message);st.rerun()
   else:st.warning('Saisis un message.')
 for r in reminders():
  if r['done']:continue
  a,b=st.columns([5,1]);a.write(f"**{r['day']}** · {r['message']}")
  if b.button('Fait ✓',key='rem_'+str(r['id'])):mark_reminder(r['id'],True);st.rerun()

def steps_page():
 st.title('👟 Objectifs de pas')
 target=int(get('steps_target','8000'))
 new=st.slider('Mon objectif quotidien',2000,20000,target,step=500)
 if st.button('💾 Enregistrer mon objectif',type='primary',key='save_steps_target'):
  set_pref('steps_target',new)
  st.success('Objectif quotidien enregistré !')
 st.subheader('📝 Mes pas du jour')
 today=date.today().isoformat()
 with st.form('steps_page_entry'):
  entered=st.number_input('Nombre de pas effectués',min_value=0,max_value=100000,value=int(j.steps(today)),step=100)
  if st.form_submit_button('💾 Enregistrer mes pas du jour'):
   j.save_steps(today,int(entered))
   st.success('Pas du jour enregistrés !')
   st.rerun()
 actual=j.steps(today);st.metric('Aujourd’hui',f'{actual:,} / {new:,} pas'.replace(',',' '))
 st.progress(min(1,actual/max(1,new)))
 st.caption('Un objectif adaptable : les jours de repos et de fatigue comptent aussi. Pas de pénalité si tu ne l’atteins pas.')
 rows=j.daily(30)
 if rows:
  df=pd.DataFrame(rows);df['day']=pd.to_datetime(df['day']);df=df.set_index('day').sort_index()
  st.line_chart(df['steps'],color='#8d2a49')
  count=sum(int(r['steps'])>=new for r in rows)
  st.info(f'{count} journée(s) avec objectif atteint parmi les journées enregistrées sur 30 jours.')
 st.caption('Les pas se saisissent directement ici. Aucune synchronisation automatique avec Apple Santé.')

def motivation_page():
 st.title('✨ Mes encouragements')
 enabled=get('motivation_enabled','1')=='1'
 enabled=st.toggle('Afficher les encouragements sur le tableau de bord',value=enabled)
 set_pref('motivation_enabled','1' if enabled else '0')
 st.write('**Rappels du jour**')
 due=[r for r in reminders() if not r['done'] and r['day']<=date.today().isoformat()]
 if due:
  for r in due:st.info(f"🔔 {r['day']} · {r['message']}")
 else:st.success('Aucun rappel en attente.')
 st.markdown('**Une progression durable se construit avec de la constance et de la récupération.**')

def home_notice():
 if get('motivation_enabled','1')!='1':return
 due=[r for r in reminders() if not r['done'] and r['day']<=date.today().isoformat()]
 if due:st.info(f'🔔 Tu as {len(due)} rappel(s) à consulter dans « Calendrier & rappels ».')
init()
