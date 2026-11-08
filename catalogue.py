"""Recherche volontaire dans Open Food Facts (Internet nécessaire)."""
import json
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

BASE='https://world.openfoodfacts.org'
HEADERS={'User-Agent':'FitEvolution/5.3 (personal fitness journal; contact: local-app-user)', 'Accept':'application/json'}

def _get(url):
 req=Request(url,headers=HEADERS)
 with urlopen(req,timeout=9) as response:
  return json.load(response)

def normalize(product):
 n=product.get('nutriments') or {}
 name=(product.get('product_name_fr') or product.get('product_name') or '').strip()
 kcal=n.get('energy-kcal_100g')
 if kcal is None and n.get('energy-kj_100g') is not None:
  kcal=float(n['energy-kj_100g'])/4.184
 try:kcal=float(kcal)
 except (TypeError,ValueError):return None
 if not 0<=kcal<=900:return None
 return {'name':name or 'Produit sans nom','brand':str(product.get('brands') or '')[:90], 'barcode':str(product.get('code') or ''), 'kcal_100g':round(kcal,1), 'proteins':n.get('proteins_100g'), 'carbs':n.get('carbohydrates_100g'), 'fat':n.get('fat_100g')}

def search(query):
 query=query.strip()[:100]
 if len(query)<2:return []
 params=urlencode({'search_terms':query,'search_simple':1,'action':'process','json':1,'page_size':15,'fields':'code,product_name,product_name_fr,brands,nutriments'})
 data=_get(BASE+'/cgi/search.pl?'+params)
 return [p for raw in data.get('products',[]) if (p:=normalize(raw)) is not None]

def barcode(code):
 code=''.join(x for x in code if x.isdigit())
 if not 8<=len(code)<=14:raise ValueError('Le code-barres doit contenir 8 à 14 chiffres.')
 data=_get(BASE+'/api/v2/product/'+quote(code)+'.json?fields=code,product_name,product_name_fr,brands,nutriments')
 if data.get('status')!=1:return None
 return normalize(data.get('product') or {})

def camera_decode(image):
 try:
  import zxingcpp
  from PIL import Image
 except ImportError:
  return None, 'Lecture caméra indisponible : installer zxing-cpp et Pillow ou saisir le code manuellement.'
 try:
  image.seek(0)
  result=zxingcpp.read_barcode(Image.open(image).convert('RGB'))
  return (result.text,None) if result else (None,'Aucun code lisible : réessayer avec plus de lumière ou saisir le code.')
 except Exception:
  return None,'Impossible de décoder cette photo.'
