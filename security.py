"""Mot de passe local, PBKDF2; accès LAN uniquement (HTTP non chiffré)."""
import hashlib
import hmac
import json
import secrets
from pathlib import Path
import streamlit as st
CONFIG=Path(__file__).with_name('acces_local.json')
def derive(password,salt):
    return hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),bytes.fromhex(salt),260000).hex()
def setup(password):
    if CONFIG.exists():return False
    if len(password)<10:raise ValueError('Choisis au moins 10 caractères.')
    salt=secrets.token_hex(16)
    CONFIG.write_text(json.dumps({'salt':salt,'hash':derive(password,salt)}),encoding='utf-8')
    return True
def check(password):
    if not CONFIG.exists():return False
    try:
        cfg=json.loads(CONFIG.read_text(encoding='utf-8'))
        return hmac.compare_digest(derive(password,cfg['salt']),cfg['hash'])
    except (ValueError,KeyError,TypeError):return False
def require_login():
    if not CONFIG.exists():
        st.error('Configuration nécessaire sur le PC : lance d’abord Lancer_Fit_Evolution_Reseau.bat.')
        st.stop()
    if st.session_state.get('authenticated'):return
    st.title('🔒 Fit Evolution V5')
    st.caption('Ton coach sportif personnel, accessible sur ton réseau Wi-Fi privé.')
    with st.form('login'):
        password=st.text_input('Mot de passe local',type='password')
        submit=st.form_submit_button('Se connecter',type='primary')
    if submit:
        if check(password):st.session_state['authenticated']=True;st.rerun()
        else:st.error('Mot de passe incorrect.')
    st.stop()
