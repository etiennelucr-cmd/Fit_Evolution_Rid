# Fit Evolution V6.1 — Coach intensif interactif

## Nouveautés
- Correctif des positions SVG incomplètes qui interrompaient l'animation.
- Chronomètre basé sur l'horloge réelle, résistant aux variations de fréquence d'affichage.
- Coach vocal français avec bouton « Tester la voix », activé par défaut. La disponibilité dépend des voix installées dans le navigateur et de ses autorisations audio.
- Bips sonores, compte à rebours de 3 secondes, encouragements, conseils de posture.
- Repos personnalisables de 10 à 90 secondes, 25 secondes par défaut, remplaçant les durées longues prévues dans le programme pour la séance guidée.
- Enchaînement automatique activable, pause, exercice suivant, recommencer et plein écran.
- Toutes les autres rubriques existantes sont conservées.

## Installation
1. Arrêter l'ancienne application.
2. Décompresser ce ZIP dans un **nouveau** dossier.
3. Copier depuis l'ancienne installation `fit_evolution.db`, `acces_local.json` et `ma_musique/` si nécessaire. **Ne pas écraser les scripts de la V6.1.**
4. Double-cliquer sur `Lancer_Fit_Evolution_Reseau.bat` sous Windows. Le PC et l'iPhone doivent être sur le même Wi-Fi privé.
5. Dans Séance guidée, cliquer d'abord sur **Tester la voix** puis **Démarrer**. Si Safari est silencieux, désactiver le mode silencieux et vérifier le volume ; le navigateur peut limiter la synthèse vocale.

## Précautions
Les animations sont illustratives et ne vérifient pas la posture. Ne pas augmenter l'intensité en cas de douleur, de fatigue importante ou de récupération insuffisante. Les calories ne sont que des estimations. L'accès réseau utilise HTTP local non chiffré : ne jamais ouvrir le port 8501 sur Internet.

## Confidentialité
Le ZIP ne contient **ni ta base de données personnelle ni ton fichier de mot de passe**. Les deux fichiers doivent être copiés depuis ton dossier précédent si tu souhaites conserver ton historique et ton accès.

## Tests
Compilation Python et intégrité du ZIP vérifiées. Les tests fonctionnels complets sur Windows et Safari iPhone restent à effectuer sur tes appareils.
