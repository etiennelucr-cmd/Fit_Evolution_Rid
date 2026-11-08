"""Mannequin Gotham cliquable, sélection multiple synchronisée avec Streamlit."""
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from streamlit_image_coordinates import streamlit_image_coordinates

W,H=700,420
# Polygones volontairement larges pour l'utilisation tactile.
PARTS={
 'Pectoraux':[(125,105),(195,105),(195,145),(125,145)],
 'Abdominaux':[(135,150),(185,150),(185,220),(135,220)],
 'Biceps':[(92,125),(120,125),(115,205),(85,205)],
 'Épaules':[(110,92),(205,92),(215,123),(100,123)],
 'Cuisses':[(125,225),(195,225),(200,310),(120,310)],
 'Mollets':[(125,315),(195,315),(200,375),(120,375)],
 'Dos':[(475,105),(545,105),(545,180),(475,180)],
 'Triceps':[(445,125),(470,125),(465,205),(435,205)],
 'Fessiers':[(475,185),(545,185),(545,235),(475,235)],
}
# Les régions de chaque côté ont une correspondance anatomique.
EXTRA={
 'Biceps':[[(200,125),(225,125),(235,205),(205,205)]],
 'Triceps':[[(550,125),(575,125),(585,205),(555,205)]],
 'Épaules':[[(460,92),(555,92),(565,123),(450,123)]],
 'Cuisses':[[(475,240),(545,240),(550,310),(470,310)]],
 'Mollets':[[(475,315),(545,315),(550,375),(470,375)]],
}

def _inside(point,polygon):
 x,y=point; odd=False; j=len(polygon)-1
 for i in range(len(polygon)):
  xi,yi=polygon[i]; xj,yj=polygon[j]
  if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:odd=not odd
  j=i
 return odd

def zone_at(x,y):
 for zone,poly in PARTS.items():
  if _inside((x,y),poly) or any(_inside((x,y),p) for p in EXTRA.get(zone,[])):
   return zone
 return None

def render(selected):
 im=Image.new('RGB',(W,H),'#0a111a'); d=ImageDraw.Draw(im)
 gold='#e8b635'; normal='#247cbe'; active='#ff455d'
 for offset in (160,510):
  d.polygon([(offset-26,45),(offset-33,27),(offset-43,48),(offset-45,72),(offset-35,90),(offset+35,90),(offset+45,72),(offset+43,48),(offset+33,27),(offset+26,45)],fill='#1b2734',outline=gold,width=3)
  d.polygon([(offset-45,96),(offset+45,96),(offset+62,130),(offset+83,207),(offset+64,215),(offset+40,154),(offset+40,235),(offset+50,378),(offset+15,382),(offset,253),(offset-15,382),(offset-50,378),(offset-40,235),(offset-40,154),(offset-64,215),(offset-83,207),(offset-62,130)],fill='#1b2734',outline=gold,width=3)
 for zone,poly in PARTS.items():
  d.polygon(poly,fill=active if zone in selected else normal)
  for extra in EXTRA.get(zone,[]):d.polygon(extra,fill=active if zone in selected else normal)
 d.text((145,394),'FACE',fill=gold)
 d.text((495,394),'DOS',fill=gold)
 return im

def choose(selected,key='gotham_mannequin'):
 """Retourne le muscle cliqué ou None. Les coordonnées sont celles de l'image source."""
 image=render(selected)
 click=streamlit_image_coordinates(image,key=key)
 if click and click.get('x') is not None:
  return zone_at(click['x'],click['y']), (click['x'],click['y'])
 return None,None
