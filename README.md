# TBM Tram Proche

![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024+-41BDF5?logo=home-assistant&logoColor=white)
![HACS](https://img.shields.io/badge/HACS-Compatible-41BDF5)
![Platform](https://img.shields.io/badge/Platform-TBM%20Bordeaux-00AEEF)
![iPhone Widget](https://img.shields.io/badge/iPhone-Widget-black?logo=apple)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=benoit-ha33&repository=tbm_tram_proche)

Intégration Home Assistant pour afficher les prochains passages TBM autour de soi en temps réel.

## Fonctionnalités

- Détection de l’arrêt TBM le plus proche
- Prochains passages en temps réel
- Lignes et destinations
- Couleurs des lignes tram
- Retards et annulations
- Affichage “En approche”
- Distance jusqu’à l’arrêt
- Temps estimé à pied
- Capteur résumé pour widget iPhone / Siri
- Compatible HACS

## Captures d’écran

<p align="center">
  <img src="screenshots/dashboard-ha.jpg" width="320">
  <img src="screenshots/widget-iphone.jpg" width="140">
</p>

## Fonctionnement

L’intégration utilise la géolocalisation Home Assistant pour détecter automatiquement l’arrêt TBM le plus proche.

Les données récupérées incluent :

- Prochains passages en temps réel
- Retards
- Annulations
- Temps à pied jusqu’à l’arrêt
- Distance jusqu’à l’arrêt
- Destinations des trams
- Statut “En approche”

L’intégration crée également un capteur résumé optimisé pour les widgets iPhone et Siri.

## Prérequis

Avant l’installation :

### Home Assistant

- Home Assistant 2024+
- Application mobile Home Assistant installée
- Géolocalisation activée sur le téléphone
- `device_tracker` fonctionnel

### HACS

Pour une installation simple :

- HACS installé : https://hacs.xyz/

Ajouter ensuite ce dépôt comme dépôt personnalisé :

```text
https://github.com/benoit-ha33/tbm_tram_proche

```

Catégorie :

```text
Integration
```

### Cartes Lovelace recommandées

Pour reproduire le dashboard présenté dans les captures, installer via HACS :

- Mushroom Cards
- Bubble Card
- Card Mod
- Button Card
- Layout Card (optionnel)

### iPhone

Pour les widgets iPhone :

- Application Scriptable
- Application Raccourcis Apple
- Home Assistant Cloud (Nabu Casa) recommandé

### Permissions recommandées

#### Application Home Assistant

- Localisation :
  - Toujours autoriser
  - Position précise activée
- Actualisation en arrière-plan activée

#### Scriptable

- Désactiver le mode économie d’énergie
- Ouvrir régulièrement Scriptable pour améliorer les refresh widgets

## Installation manuelle

Copier le dossier :

```text
custom_components/tbm_tram_proche
```

dans :

```text
/config/custom_components/
```

Puis redémarrer Home Assistant.

## Configuration

Dans Home Assistant :

```text
Paramètres → Appareils et services → Ajouter une intégration
```

Chercher :

```text
TBM Tram Proche
```

## Entités créées

- `sensor.tbm_arret_tram_proche`
- `sensor.tbm_distance_arret_tram`
- `sensor.tbm_prochains_passages`
- `sensor.tbm_resume_iphone`

## Siri

Exemple :

```text
Dis Siri, prochain tram
```

## Notes

Cette intégration utilise les données ouvertes TBM / Bordeaux Métropole.

## Licence

MIT
