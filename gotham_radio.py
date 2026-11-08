# Gotham Radio MP3 local library
import base64
import hashlib
import html
import json
import os
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import moteur as m

AUDIO_DIR = Path(__file__).resolve().parent / 'gotham_mp3'
MAX_FILE = 30 * 1024 * 1024
MAX_EMBED = 45 * 1024 * 1024

def init():
    AUDIO_DIR.mkdir(exist_ok=True)
    with m.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS gotham_mp3 (id TEXT PRIMARY KEY, filename TEXT NOT NULL, stored_name TEXT NOT NULL UNIQUE, bytes INTEGER NOT NULL, added_at TEXT DEFAULT CURRENT_TIMESTAMP)')
        db.execute('CREATE TABLE IF NOT EXISTS gotham_radio_settings (name TEXT PRIMARY KEY, value TEXT NOT NULL)')

def tracks():
    init()
    with m.connect() as db:
        return list(db.execute('SELECT id, filename, stored_name, bytes FROM gotham_mp3 ORDER BY added_at, rowid'))

def add_file(upload):
    name = Path(upload.name).name
    if Path(name).suffix.lower() != '.mp3':
        return 'Seuls les fichiers MP3 sont acceptés.'
    content = upload.getvalue()
    if not content or len(content) > MAX_FILE:
        return 'Fichier vide ou supérieur à 30 Mo.'
    if not (content[:3] == b'ID3' or (len(content)>1 and content[0] == 0xff and (content[1] & 0xe0) == 0xe0)):
        return 'Le fichier ne semble pas être un MP3 valide.'
    digest = hashlib.sha256(content).hexdigest()
    init()
    with m.connect() as db:
        if db.execute('SELECT 1 FROM gotham_mp3 WHERE id=?',(digest,)).fetchone():
            return 'Ce morceau est déjà enregistré (doublon).'
        stored = digest + '.mp3'
        (AUDIO_DIR / stored).write_bytes(content)
        db.execute('INSERT INTO gotham_mp3(id,filename,stored_name,bytes) VALUES(?,?,?,?)',(digest,name,stored,len(content)))
    return 'Morceau ajouté : ' + name

def remove(digest, stored):
    with m.connect() as db:
        db.execute('DELETE FROM gotham_mp3 WHERE id=?',(digest,))
    (AUDIO_DIR / stored).unlink(missing_ok=True)

def get_volume():
    init()
    with m.connect() as db:
        row=db.execute("SELECT value FROM gotham_radio_settings WHERE name='volume'").fetchone()
    try:return max(0,min(100,int(row[0]))) if row else 50
    except (ValueError,TypeError):return 50

def save_volume(v):
    with m.connect() as db:
        db.execute("INSERT INTO gotham_radio_settings(name,value) VALUES('volume',?) ON CONFLICT(name) DO UPDATE SET value=excluded.value",(str(v),))

def player(selected, volume=50, compact=False):
    """Keep the HTMLAudioElement in the parent page across Streamlit reruns.

    Browser iframe security may prohibit parent access; in that case the player
    displays a clear diagnostic instead of silently resetting the music.
    """
    payload=[]
    for digest,name,stored,size in selected:
        f=AUDIO_DIR/stored
        if f.is_file():
            payload.append({'id':digest,'title':name,'src':'data:audio/mpeg;base64,'+base64.b64encode(f.read_bytes()).decode('ascii')})
    if not payload:
        return
    js=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c')
    markup=r'''<!doctype html><html lang="fr"><meta charset="utf-8"><style>
    body{background:transparent;color:#f5c546;font:13px system-ui;margin:0}
    #fallback{padding:8px;color:#f5c546;background:#101a27;border-radius:9px}
    </style><div id="fallback">📻 Gotham Radio · initialisation…</div><script>
    (()=>{
      const songs=__SONGS__;
      const fallback=document.getElementById('fallback');
      let root;
      try { root=window.parent.document; if(!root.body)throw Error('document non prêt'); }
      catch(e){fallback.textContent='⚠️ Lecteur permanent non autorisé par ce navigateur. Ouvre Gotham Radio dans un onglet dédié.';return;}
      const host=window.parent;
      let box=root.getElementById('gotham-radio-persistent');
      if(!box){
        box=root.createElement('div');box.id='gotham-radio-persistent';
        box.style.cssText='position:fixed;z-index:999990;top:40px;left:33%;width:38%;min-width:280px;max-width:620px;background:#101a27ee;border:1px solid #a98326;border-radius:12px;color:#f5c546;padding:7px 12px;box-sizing:border-box;font:12px system-ui;box-shadow:0 3px 18px #0008';
        box.innerHTML='<div style="display:flex;align-items:center;gap:7px"><b style="white-space:nowrap">📻 GOTHAM</b><span id="gotham-song" style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#fff">Prêt</span><button id="gotham-play" title="Lecture/Pause">▶</button><button id="gotham-next" title="Suivant">⏭</button><span>🔊</span><input id="gotham-volume" aria-label="Volume" type="range" min="0" max="100" value="50" style="width:75px;accent-color:#f5c546"/></div><div id="gotham-status" style="font-size:10px;color:#d2b879;white-space:nowrap;overflow:hidden;text-overflow:ellipsis"></div>';
        root.body.appendChild(box);
      }
      const styleBtn=el=>{el.style.cssText='border:0;background:#f5c546;color:#101a27;border-radius:6px;cursor:pointer;font-weight:bold;padding:4px 8px'};
      styleBtn(box.querySelector('#gotham-play'));styleBtn(box.querySelector('#gotham-next'));
      let state=host.__gothamPersistent;
      if(!state){
        const audio=root.createElement('audio');audio.id='gotham-audio-element';audio.preload='auto';audio.style.display='none';root.body.appendChild(audio);
        state={audio,songs:[],bag:[],current:-1,volume:__VOLUME__,signature:''};
        host.__gothamPersistent=state;
        audio.volume=state.volume/100;
        audio.addEventListener('ended',()=>host.__gothamPersistent?.next?.());
        audio.addEventListener('error',()=>{const s=host.__gothamPersistent;if(s){s.status('MP3 illisible · morceau suivant');s.next?.();}});
      }
      const sig=songs.map(x=>x.id).join('|');
      if(sig!==state.signature){
        const oldId=state.songs[state.current]?.id;
        state.songs=songs;state.signature=sig;state.bag=[];
        state.current=songs.findIndex(x=>x.id===oldId);
        // Never reset an already playing song just because Streamlit reran.
      }
      state.status=message=>{const el=root.getElementById('gotham-status');if(el)el.textContent=message;};
      state.play=()=>{
        if(state.current<0){state.next();return;}
        state.audio.play().then(()=>state.status('Lecture aléatoire · musique continue pendant la navigation')).catch(e=>state.status('Clique sur ▶ pour autoriser le son : '+e.message));
      };
      state.next=()=>{
        if(!state.songs.length)return;
        if(!state.bag.length){state.bag=state.songs.map((_,i)=>i);for(let i=state.bag.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[state.bag[i],state.bag[j]]=[state.bag[j],state.bag[i]];}
          if(state.bag.length>1&&state.bag[state.bag.length-1]===state.current){const j=state.bag.findIndex(x=>x!==state.current);if(j>=0)[state.bag[j],state.bag[state.bag.length-1]]=[state.bag[state.bag.length-1],state.bag[j]];}}
        state.current=state.bag.pop();state.audio.src=state.songs[state.current].src;state.audio.load();state.play();
        const label=root.getElementById('gotham-song');if(label)label.textContent=state.songs[state.current].title;
      };
      const play=box.querySelector('#gotham-play'),next=box.querySelector('#gotham-next'),vol=box.querySelector('#gotham-volume');
      play.onclick=()=>{if(state.audio.paused){state.play();play.textContent='⏸';}else{state.audio.pause();state.status('En pause');play.textContent='▶';}};
      next.onclick=()=>{state.next();play.textContent='⏸';};
      // Direct browser volume update: no Streamlit rerun, no song change.
      vol.value=String(state.volume);
      vol.oninput=()=>{state.volume=Number(vol.value);state.audio.volume=state.volume/100;};
      const label=box.querySelector('#gotham-song');
      if(state.current>=0&&state.songs[state.current])label.textContent=state.songs[state.current].title;
      play.textContent=state.audio.paused?'▶':'⏸';
      fallback.textContent='🎵 Lecteur actif dans le bandeau supérieur · volume sans changement de morceau.';
    })();
    </script></html>'''.replace('__SONGS__',js).replace('__VOLUME__',str(volume))
    components.html(markup,height=35,scrolling=False)


def header_player():
    library=tracks()
    if not library:
        return
    selected=[];total=0
    for item in library:
        if total+item[3]<=MAX_EMBED:
            selected.append(item);total+=item[3]
    if selected:
        player(selected,get_volume(),compact=True)

def page():
    st.title('📻 GOTHAM RADIO · MP3')
    st.caption('Importe tes MP3 autorisés : ils sont conservés localement et les doublons sont refusés. Aucun lecteur YouTube intégré.')
    with st.form('gotham_mp3_import',clear_on_submit=True):
        files=st.file_uploader('Ajouter des fichiers MP3',type=['mp3'],accept_multiple_files=True)
        submit=st.form_submit_button('➕ Importer dans la bibliothèque',type='primary')
    if submit:
        if not files:st.warning('Sélectionne au moins un MP3.')
        else:
            for f in files:
                result=add_file(f)
                (st.success if result.startswith('Morceau ajouté') else st.warning)(result)
    library=tracks()
    st.metric('Morceaux MP3 enregistrés',len(library))
    st.caption('🔊 Volume, lecture et morceau suivant : commandes dans le bandeau supérieur. Le volume ne recharge plus la page.')
    if library:
        total=0;selected=[]
        for item in library:
            if total+item[3] <= MAX_EMBED:
                selected.append(item);total+=item[3]
        if len(selected)<len(library):
            st.warning('La radio charge les premiers MP3 dans une limite de 45 Mo pour préserver la mémoire du navigateur. Supprime ou réduis les fichiers volumineux pour modifier la sélection.')
        if selected:st.info('Utilise les commandes 📻 GOTHAM dans le bandeau supérieur.')
        else:st.warning('Aucun fichier ne peut être chargé dans le lecteur.')
        with st.expander('📚 Bibliothèque MP3',expanded=False):
            for digest,name,stored,size in library:
                a,b=st.columns([5,1]);a.write(f'{name} · {size/1024/1024:.1f} Mo')
                if b.button('🗑️',key='mp3_del_'+digest):remove(digest,stored);st.rerun()
    else:st.info('Ajoute des MP3 pour démarrer ta radio.')
    st.caption('Le lecteur reste actif lors des changements de rubrique Streamlit, sous réserve des restrictions du navigateur. Fermer ou recharger complètement l’onglet arrête la lecture. Les liens YouTube historiques restent conservés.')
