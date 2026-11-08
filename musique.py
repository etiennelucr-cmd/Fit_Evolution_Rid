"""Bibliothèque audio locale et playlists, sans téléchargement de musique commerciale."""
import base64
import html
import json
import mimetypes
import re
import sqlite3
import uuid
from pathlib import Path
from urllib.parse import quote
import streamlit as st
import streamlit.components.v1 as components
import moteur as m

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / 'ma_musique'
MAX_UPLOAD = 30 * 1024 * 1024
MAX_PLAYER = 75 * 1024 * 1024
EXTS = {'.mp3':'audio/mpeg','.wav':'audio/wav','.ogg':'audio/ogg','.m4a':'audio/mp4'}

def init():
    AUDIO.mkdir(exist_ok=True)
    with m.connect() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS music_tracks(id TEXT PRIMARY KEY,title TEXT NOT NULL,artist TEXT NOT NULL DEFAULT '',file_name TEXT NOT NULL UNIQUE,bytes INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS music_playlists(id INTEGER PRIMARY KEY,title TEXT NOT NULL UNIQUE);
        CREATE TABLE IF NOT EXISTS music_playlist_tracks(playlist_id INTEGER NOT NULL REFERENCES music_playlists(id) ON DELETE CASCADE,track_id TEXT NOT NULL REFERENCES music_tracks(id) ON DELETE CASCADE,position INTEGER NOT NULL,PRIMARY KEY(playlist_id,track_id));
        INSERT OR IGNORE INTO music_playlists(id,title) VALUES(1,'Ma motivation');
        ''')

def tracks():
    init()
    return m.all_rows('SELECT * FROM music_tracks ORDER BY artist COLLATE NOCASE,title COLLATE NOCASE')

def playlists():
    init()
    return m.all_rows('SELECT * FROM music_playlists ORDER BY id')

def tracks_in(pid):
    return m.all_rows('''SELECT t.* FROM music_playlist_tracks pt JOIN music_tracks t ON t.id=pt.track_id WHERE pt.playlist_id=? ORDER BY pt.position''',(pid,))

def add(upload,artist=''):
    init()
    suffix=Path(upload.name).suffix.lower()
    if suffix not in EXTS: raise ValueError('Format non pris en charge : MP3, WAV, OGG, M4A uniquement.')
    data=upload.getvalue()
    if not data or len(data)>MAX_UPLOAD:raise ValueError('Chaque fichier doit contenir entre 1 octet et 30 Mo.')
    title=Path(upload.name).stem[:160]
    fid=uuid.uuid4().hex
    filename=fid+suffix
    path=AUDIO/filename
    path.write_bytes(data)
    try:
        with m.connect() as db:
            db.execute('INSERT INTO music_tracks VALUES(?,?,?,?,?)',(fid,title,artist.strip()[:120],filename,len(data)))
            pos=db.execute('SELECT COALESCE(MAX(position),0)+1 FROM music_playlist_tracks WHERE playlist_id=1').fetchone()[0]
            db.execute('INSERT INTO music_playlist_tracks VALUES(1,?,?)',(fid,pos))
    except Exception:
        path.unlink(missing_ok=True)
        raise

def remove(track):
    with m.connect() as db:
        row=db.execute('SELECT file_name FROM music_tracks WHERE id=?',(track,)).fetchone()
        if not row:return
        db.execute('DELETE FROM music_playlist_tracks WHERE track_id=?',(track,))
        db.execute('DELETE FROM music_tracks WHERE id=?',(track,))
    (AUDIO/row['file_name']).unlink(missing_ok=True)

def create_playlist(title):
    title=title.strip()[:90]
    if not title:raise ValueError('Indique un nom de playlist.')
    with m.connect() as db:db.execute('INSERT INTO music_playlists(title) VALUES(?)',(title,))

def set_playlist(pid,track_ids):
    with m.connect() as db:
        db.execute('DELETE FROM music_playlist_tracks WHERE playlist_id=?',(pid,))
        for idx,tid in enumerate(track_ids):db.execute('INSERT INTO music_playlist_tracks VALUES(?,?,?)',(pid,tid,idx+1))

def player(items,key='main'):
    available=[]
    total=0
    for track in items:
        path=AUDIO/track['file_name']
        if not path.is_file():continue
        size=path.stat().st_size
        if total+size>MAX_PLAYER:break
        total+=size
        available.append({'title':track['title'],'artist':track['artist'],'src':'data:'+EXTS[path.suffix.lower()]+';base64,'+base64.b64encode(path.read_bytes()).decode('ascii')})
    if not available:
        st.info('Aucun morceau lisible dans cette sélection.')
        return
    if len(available)<len(items):st.warning('La playlist est limitée à 75 Mo par chargement pour préserver la fluidité. Crée une playlist plus courte pour écouter les morceaux restants.')
    payload=json.dumps(available,ensure_ascii=False).replace('<','\\u003c')
    components.html('''<div style="font:15px system-ui;background:#142b35;color:#f7fafc;border-radius:16px;padding:18px">
    <div style="font-size:21px;font-weight:750">🎧 Lecteur Fit Evolution</div><div id="now" style="padding:14px 0">Prêt à démarrer</div>
    <audio id="audio" controls preload="none" style="width:100%"></audio>
    <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">
    <button onclick="prev()">⏮ Précédent</button><button onclick="next()">⏭ Suivant</button>
    <label><input id="shuffle" type="checkbox"> Aléatoire</label><label><input id="repeat" type="checkbox" checked> Répéter</label></div>
    <div id="queue" style="margin-top:14px;max-height:220px;overflow:auto"></div>
    <div style="font-size:12px;color:#bed4df;margin-top:10px">La lecture démarre après un clic. Changer de page Streamlit peut interrompre le lecteur.</div></div>
    <script>
    const tracks=__TRACKS__;const audio=document.getElementById('audio');let i=0;
    function load(n,play){i=(n+tracks.length)%tracks.length;audio.src=tracks[i].src;document.getElementById('now').textContent=(tracks[i].artist?tracks[i].artist+' — ':'')+tracks[i].title;render();if(play)audio.play().catch(()=>{});}
    function next(){if(document.getElementById('shuffle').checked && tracks.length>1){let n=i;while(n===i)n=Math.floor(Math.random()*tracks.length);load(n,true)}else if(i<tracks.length-1)load(i+1,true);else if(document.getElementById('repeat').checked)load(0,true);else{audio.pause();audio.currentTime=0}}
    function prev(){load(i-1,true)}
    function render(){document.getElementById('queue').innerHTML='';tracks.forEach((t,n)=>{let b=document.createElement('button');b.textContent=(n===i?'▶ ':'')+(t.artist?t.artist+' — ':'')+t.title;b.style='display:block;width:100%;text-align:left;padding:7px;margin:3px 0;background:#294654;color:white;border:0;border-radius:6px;cursor:pointer';b.onclick=()=>load(n,true);document.getElementById('queue').appendChild(b)})}
    audio.addEventListener('ended',next);load(0,false);
    </script>'''.replace('__TRACKS__',payload),height=410,scrolling=False)

def session_music():
    init()
    ps=playlists()
    chosen=st.selectbox('🎵 Musique pour cette séance', ['Boucle motivation intégrée']+[p['title'] for p in ps],key='session_music')
    if chosen=='Boucle motivation intégrée':
        path=ROOT/'motivation.wav'
        if path.exists():st.audio(str(path),format='audio/wav',loop=True)
    else:
        pid=next(p['id'] for p in ps if p['title']==chosen)
        player(tracks_in(pid),'session')

def page():
    init()
    st.title('🎵 Ma musique')
    st.caption('Tes fichiers audio restent sur ton ordinateur. Aucun morceau commercial n’est fourni ni téléchargé par l’application.')
    tab1,tab2,tab3=st.tabs(['🎧 Lecteur & playlists','➕ Importer ma musique','🌐 Spotify & YouTube Music'])
    with tab1:
        ps=playlists()
        pid=st.selectbox('Playlist', [p['id'] for p in ps],format_func=lambda v:next(p['title'] for p in ps if p['id']==v),key='music_playlist')
        current=tracks_in(pid)
        if current:player(current)
        else:st.info('Cette playlist est vide. Ajoute des fichiers dans l’onglet Importer.')
        with st.expander('Modifier les morceaux de la playlist'):
            library=tracks()
            selected=st.multiselect('Morceaux',options=[x['id'] for x in library],default=[x['id'] for x in current],format_func=lambda tid:next((f"{x['artist']} — {x['title']}" if x['artist'] else x['title'] for x in library if x['id']==tid),tid),key='music_members')
            if st.button('Enregistrer cette playlist'):
                set_playlist(pid,selected);st.success('Playlist enregistrée.');st.rerun()
        with st.form('new_playlist'):
            title=st.text_input('Nouvelle playlist (ex. Rap US / HIIT / R&B)')
            if st.form_submit_button('Créer la playlist'):
                try:create_playlist(title);st.rerun()
                except sqlite3.IntegrityError:st.error('Cette playlist existe déjà.')
                except ValueError as exc:st.error(str(exc))
    with tab2:
        st.write('Importe des **MP3, WAV, OGG ou M4A** que tu as le droit d’utiliser. Maximum 30 Mo par fichier.')
        artist=st.text_input('Artiste (facultatif, pour les fichiers importés maintenant)')
        uploaded=st.file_uploader('Choisir des morceaux',type=['mp3','wav','ogg','m4a'],accept_multiple_files=True)
        if st.button('Importer les morceaux',disabled=not uploaded,type='primary'):
            ok=0
            for f in uploaded:
                try:add(f,artist);ok+=1
                except (ValueError,OSError,sqlite3.Error) as exc:st.error(f'{f.name} : {exc}')
            if ok:st.success(f'{ok} morceau(x) importé(s).');st.rerun()
        st.subheader('Ma bibliothèque')
        for t in tracks():
            left,right=st.columns([5,1])
            left.write(f"🎶 **{t['title']}**"+(f" — {t['artist']}" if t['artist'] else ''))
            if right.button('Supprimer',key='del_music_'+t['id']):remove(t['id']);st.rerun()
        st.caption('Supprimer un morceau efface son fichier audio et le retire de toutes les playlists.')
    with tab3:
        st.info('Spotify et YouTube Music s’ouvrent dans leurs services officiels. Leurs flux ne peuvent pas être importés dans le lecteur MP3 local.')
        st.link_button('🎧 Ouvrir Spotify', 'https://open.spotify.com/')
        st.link_button('▶ Ouvrir YouTube Music', 'https://music.youtube.com/')
        st.subheader('Rechercher un artiste ou un album')
        query=st.text_input('Artiste, album ou mixtape',value='Soulja Boy King Soulja 4')
        if query.strip():
            st.link_button('Rechercher sur Spotify','https://open.spotify.com/search/'+quote(query.strip(),safe=''))
            st.link_button('Rechercher sur YouTube Music','https://music.youtube.com/search?q='+quote(query.strip(),safe=''))
        st.caption('La lecture de ces services dépend de ton compte, de leur catalogue et de leurs conditions d’utilisation.')
