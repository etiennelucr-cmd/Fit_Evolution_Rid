# Fit Evolution — vérification avant déploiement

1. Le schéma `fit_evolution` doit déjà exister sur le projet Supabase de Mi Español. Ne pas toucher à `public`.
2. Configurer les secrets de **Fit Evolution uniquement** : `[postgres]` (host, port, dbname, user, password) et `[auth]` (salt, password_hash).
3. Générer les valeurs d'authentification avec `python generate_password_hash.py`.
4. Le ZIP exclut volontairement la base SQLite, le fichier d'accès local et les fichiers compilés.
5. Vérifier les permissions SQL du compte PostgreSQL et sauvegarder la base avant toute initialisation.
6. Ne pas exécuter `setup_supabase.py` avant validation de tous les modules : la compatibilité complète PostgreSQL reste à tester.
7. Les MP3 ajoutés localement ne sont pas persistants sur Streamlit Cloud.
8. Si `acces_local.json` a déjà été publié sur GitHub, changer l'ancien mot de passe et retirer le fichier de l'historique Git.
