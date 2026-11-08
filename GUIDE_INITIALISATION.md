# Fit Evolution — Initialisation Supabase partagée

Cette archive utilise le schéma PostgreSQL `fit_evolution`, distinct de `public` (Mi Español V9).

1. Faire une sauvegarde de la base Supabase et conserver une copie du dépôt GitHub précédent.
2. Vérifier que `fit_evolution` existe dans Supabase SQL Editor : `SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'fit_evolution';`
3. Remplacer les fichiers GitHub par ceux de cette archive, en excluant les secrets et les données privées.
4. Configurer les secrets `[postgres]` et `[auth]` **dans l'application Fit Evolution**, pas dans Mi Español.
5. Sur une machine disposant des secrets Streamlit locaux et des dépendances, exécuter :
   - macOS/Linux : `FIT_INIT_CONFIRM=fit_evolution python setup_supabase.py`
   - PowerShell : `$env:FIT_INIT_CONFIRM='fit_evolution'; python setup_supabase.py`
6. Vérifier les tables dans Supabase > Table Editor > `fit_evolution`.
7. Tester un enregistrement de poids, rafraîchir l'application et vérifier sa persistance.

Ne pas exécuter ce script avec les identifiants d'une autre base. Le script ne migre pas les anciennes données SQLite.

**Limites :** validation statique uniquement, pas de connexion réelle à Supabase; les fichiers audio locaux ne sont pas persistants sur Streamlit Cloud.
