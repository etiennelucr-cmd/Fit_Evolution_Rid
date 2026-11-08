"""Streamlit Cloud password gate, no local credential files."""
import hashlib, hmac
import streamlit as st

def require_login():
    if st.session_state.get('authenticated'):
        return
    if 'auth' not in st.secrets:
        st.error('Configurer [auth] dans Streamlit Secrets.')
        st.stop()
    auth = st.secrets['auth']
    with st.form('fit_login'):
        st.title('🔒 Fit Evolution')
        password = st.text_input('Mot de passe', type='password')
        submit = st.form_submit_button('Se connecter')
    if submit:
        try:
            computed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(auth['salt']), 260000).hex()
            if hmac.compare_digest(computed, auth['password_hash']):
                st.session_state['authenticated'] = True
                st.rerun()
        except (ValueError, KeyError, TypeError):
            pass
        st.error('Mot de passe incorrect ou configuration invalide.')
    st.stop()
