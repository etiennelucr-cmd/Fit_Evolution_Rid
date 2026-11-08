import getpass, hashlib, secrets
p=getpass.getpass('Choisis un mot de passe Fit Evolution (12 caractères minimum) : ')
if len(p)<12: raise SystemExit('Mot de passe trop court.')
s=secrets.token_hex(16)
h=hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(s),260000).hex()
print('[auth]\nsalt = "'+s+'"\npassword_hash = "'+h+'"')
