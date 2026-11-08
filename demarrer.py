"""Initialisation du mot de passe et affichage des adresses LAN."""
import getpass
import socket
from security import CONFIG,setup
if not CONFIG.exists():
    print('PREMIER DEMARRAGE : definis un mot de passe local (10 caracteres minimum).')
    while True:
        p=getpass.getpass('Nouveau mot de passe : ')
        p2=getpass.getpass('Confirmer : ')
        if p!=p2:print('Les mots de passe ne correspondent pas.');continue
        try:setup(p);break
        except ValueError as e:print(e)
print('\nFIT EVOLUTION V5 — RESEAU LOCAL')
print('PC : http://localhost:8501')
ips=set()
try:
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
        s.connect(('192.0.2.1',80));ips.add(s.getsockname()[0])
except OSError:pass
try:
    for info in socket.getaddrinfo(socket.gethostname(),None,family=socket.AF_INET):
        ips.add(info[4][0])
except OSError:pass
for ip in sorted(ips):
    if not ip.startswith('127.') and not ip.startswith('169.254.'):
        print('iPhone (meme Wi-Fi) : http://'+ip+':8501')
print('Si le pare-feu Windows demande une autorisation : reseaux prives uniquement.')
print('Ne transfere jamais le port 8501 sur Internet.\n')
