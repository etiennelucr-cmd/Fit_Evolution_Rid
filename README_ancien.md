# Correctif V5.8.1

Correction des deux boutons de navigation vers le profil : utilisation de `on_click` avant instanciation des widgets Streamlit. Aucune modification de la base SQLite.

# Fit Evolution V5.8 — Refonte interface Bordeaux & Noir

## Nouveautés
- Navigation regroupée en **6 rubriques** (Accueil, Entraînement, Nutrition, Progression, Motivation, Paramètres), avec sous-pages. Les 18 écrans précédents restent accessibles.
- Tableau de bord de bienvenue même avant la création du profil : cartes « À renseigner », étapes de démarrage, bouton de configuration.
- Harmonisation des cartes, boutons, bandeau météo/horloge, menu et styles sur PC et iPhone.
- Conservation des fonctionnalités V5.7 : programme, séances, HIIT, calories estimées, nutrition, pas, bilan hebdomadaire, calendrier, musique et accès Wi-Fi local.

## Installation Windows
1. Fermer la version précédente.
2. Sauvegarder `fit_evolution.db`, `acces_local.json` et le dossier `ma_musique/` (s’ils existent).
3. Décompresser l’archive ZIP V5.8 et copier les données sauvegardées dans son dossier, sans écraser les scripts Python.
4. Double-cliquer sur `Lancer_Fit_Evolution_Reseau.bat`. Python 3.10+ est nécessaire.
5. Depuis l’iPhone connecté au **même Wi-Fi**, ouvrir dans Safari l’adresse `http://ADRESSE_DU_PC:8501` affichée sur le PC.

**Important :** PC allumé et application lancée. Utiliser uniquement un réseau privé de confiance : HTTP local non chiffré. Ne jamais exposer le port 8501 sur Internet.

**Limites :** météo et Open Food Facts demandent Internet. Les calories et prévisions sont indicatives. Les rappels ne sont pas des notifications push. La navigation et l’affichage n’ont pas été vérifiés sur un iPhone physique.

---
# Fit Evolution V5.7 — Bilan hebdomadaire personnalisé

Cette version ajoute **📋 Mon bilan hebdomadaire** à la V5.6, sans supprimer les autres fonctions.

Le bilan réunit les séances réalisées/prévues, effort moyen, calories sportives estimées, pas, calories alimentaires et protéines renseignées, poids moyen, et conseils de régularité/récupération. Choix de la semaine via sa date de fin, graphiques et export CSV. Les jours sans saisie ne sont pas comptés comme zéro calorie. Les conseils ne sont pas des prescriptions médicales et aucune prédiction de poids ne découle directement des calories ou des pas.

## Installation
1. Fermer Fit Evolution V5.6.
2. Sauvegarder `fit_evolution.db`, `acces_local.json` et `ma_musique/` si présents.
3. Décompresser le ZIP V5.7.
4. Copier les éléments sauvegardés dans le dossier V5.7 (ne pas écraser les scripts Python).
5. Lancer `Lancer_Fit_Evolution_Reseau.bat` sur Windows.
6. Depuis Safari sur iPhone, ouvrir l'adresse locale du PC sur le même Wi-Fi. Le PC doit rester allumé.

**Sécurité :** accès HTTP local non chiffré, réseau Wi-Fi privé uniquement ; ne pas exposer le port 8501 sur Internet.

---

# Fit Evolution V5.6 — Macros et bilan de progression

## Nouveautés
- Saisie des protéines, glucides et lipides par portion dans le journal alimentaire.
- Récapitulatif quotidien et historique nutritionnel sur 30 jours.
- Graphiques calories, macros, pas, poids, calories sportives et mesures disponibles.
- Export CSV du bilan nutritionnel.
- Les anciens aliments restent accessibles et sont indiqués comme « macros non renseignées ».
- La base SQLite existante est migrée automatiquement à l'ouverture de l'application.

**Important :** les macros sont facultatives, les données d'étiquetage peuvent être approximatives, et le bilan ne prescrit pas de déficit calorique. La projection de poids est calculée uniquement à partir des pesées.

## Installation et migration
1. Fermer la V5.5.
2. Sauvegarder `fit_evolution.db`, `acces_local.json` et `ma_musique/`.
3. Décompresser le ZIP V5.6, copier les éléments sauvegardés dans le dossier V5.6.
4. Sur Windows, lancer `Lancer_Fit_Evolution_Reseau.bat`.
5. Sur iPhone, ouvrir l'adresse locale indiquée par le PC (même Wi-Fi, PC allumé).

## Remarque
Les aliments ajoutés via la recherche Open Food Facts conservent leur saisie calorique historique. Pour renseigner les macros, utiliser le formulaire du journal alimentaire. Le tableau de bord et le lecteur musical des versions précédentes sont conservés.

---

# Fit Evolution V5.5 — Bordeaux & Noir

Application sportive maison en Python Streamlit, accessible depuis Windows et un iPhone connecté au **même Wi-Fi**.

## Nouveautés V5.5
- **Calendrier mensuel visuel** : séances planifiées, réalisées et jours de récupération.
- **Rappels personnels** datés et cochables, conservés dans SQLite. Ils s’affichent **dans l’application uniquement** (pas de notifications système ni de messages push).
- **Objectif de pas personnalisable** (2 000 à 20 000 pas), progression du jour, graphique et nombre de jours réussis.
- **Encouragements** activables et rappel des tâches en attente sur le tableau de bord.
- Interface bordeaux, noir et blanc cassé, météo et horloge conservées.

Toutes les fonctions précédentes restent incluses : programme adaptatif, séances et calories estimées, HIIT, musique MP3 et liens Apple Music/Spotify/YouTube Music, nutrition, Open Food Facts, journal alimentaire, pas, poids, tour de taille, projections prudentes, niveaux, streaks et bilan coach.

## Installation Windows
1. Décompresser le ZIP.
2. Installer Python 3.10+ si nécessaire.
3. Double-cliquer sur `Lancer_Fit_Evolution_Reseau.bat`.
4. Suivre l’adresse affichée dans la console. Le premier lancement peut installer les dépendances.
5. Depuis l’iPhone, sur le **même réseau Wi-Fi**, ouvrir l’adresse `http://IP_DU_PC:8501` dans Safari. Le PC doit rester allumé.

## Migration depuis V5.4
Fermer l’application. **Sauvegarder** puis copier `fit_evolution.db`, `acces_local.json` et `ma_musique/` depuis le dossier V5.4 dans le dossier V5.5. Ne pas écraser les fichiers sources Python. Les nouvelles tables SQLite se créent automatiquement.

## Sécurité et limites
- Application locale via HTTP non chiffré : utiliser exclusivement un Wi-Fi privé et **ne jamais ouvrir le port 8501 sur Internet**.
- Les rappels ne sont pas des notifications push ; ouvrir l’application pour les voir.
- La météo et la recherche Open Food Facts requièrent Internet.
- Les calories et les projections de poids sont des estimations ; aucun résultat n’est garanti.
- Les données Apple Santé ne sont pas importées automatiquement.

## Nouveauté V5.9 — Séance guidée 2D

La rubrique « Séance guidée » contient maintenant un personnage 2D animé, un minuteur par série, des récupérations automatiques, les commandes démarrer/pause/suivant/recommencer, un bip facultatif et des annonces vocales facultatives (selon navigateur). Le coach est illustratif : il ne contrôle pas la posture et n'enregistre pas automatiquement la séance. Pour les exercices à répétitions, la durée par série est une estimation réglable. Les animations sont embarquées localement et ne nécessitent pas Internet. Les annonces vocales peuvent interrompre la musique sur iPhone.


## Nouveautés V6.0
- Coach 2D avec préparation de 3 secondes avant chaque série.
- Conseils techniques propres aux principaux mouvements.
- Alerte vocale facultative à 10 secondes, annonces de transition.
- Mode plein écran (selon support navigateur), bouton pause, suivant et reprise.
- Bilan chronométré dans le coach en fin de séance.
- Enregistrement SQLite/XP/calories : toujours via le formulaire de validation sous le coach, car le composant HTML Streamlit ne peut pas écrire directement dans la base.
- Animations simplifiées, sans reconnaissance de posture ni garantie anatomique.
