# Fit Evolution — Correction calcul automatique des macros

Dans Scanner & aliments :
- Recherche Open Food Facts : indique le poids consommé, vois les calories et macros calculées automatiquement, puis ajoute au journal.
- Étiquette nutritionnelle : enregistre une fois les valeurs pour 100 g d’un produit (par exemple chorizo doux 341 kcal, 24 g protéines, 1,8 g glucides, 26 g lipides). Sélectionne ensuite le produit, indique 25 g et ajoute automatiquement 85,25 kcal, 6 g protéines, 0,45 g glucides et 6,5 g lipides.
- Les aliments enregistrés alimentent le journal et le bilan macros.

**Installation :** remplacer les fichiers `app.py` et `journal.py` dans ton dossier actuel, application fermée. Sauvegarder `fit_evolution.db` avant de relancer. La base personnelle n'est pas incluse.

**Important :** les anciennes saisies erronées ne sont pas modifiées automatiquement : supprime l'entrée incorrecte puis ajoute-la à nouveau avec la bonne quantité. Les valeurs d'étiquette sont un exemple et doivent être vérifiées pour les autres produits.
