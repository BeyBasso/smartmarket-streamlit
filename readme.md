# SmartMarket — Marketing Analytics (Streamlit)

## 🌐 Lien vers l’application (Streamlit)
➡️ Application en ligne : https://smartmarket-app-gtqwojjwcw3v32rkpff6rr.streamlit.app/


## 📌 Contexte & objectifs
SmartMarket mène plusieurs campagnes marketing (Emailing, Facebook Ads, Instagram Ads, LinkedIn) et souhaite analyser la performance multi-canaux sur une période définie afin d’optimiser les investissements.

L’objectif du projet est de :
- sélectionner les données selon un périmètre imposé,
- réaliser une analyse **univariée** et **bivariée**,
- produire des **visualisations pertinentes** ,
- concevoir un **tableau de bord synthétique** ,
- rédiger une **note d’analyse métier**,
- documenter un **carnet technique** (problèmes rencontrés + solutions).

---

## 🎯 Périmètre d’analyse
- **Période** : du **2025-09-01** au **2025-09-30** (septembre 2025 uniquement)
- **Axes métier** :
  - performance des campagnes (CTR, CVR, coût par lead),
  - comparaison des canaux,
  - analyse des segments (région, secteur, taille d’entreprise),
  - qualité business via le CRM (MQL → SQL → Client).

---

## 📁 Données utilisées
Le projet repose sur 3 sources :

### 1 `data/leads_smartmarket.csv`
- **Colonnes** : `lead_id`, `date`, `channel`, `device`
- **Rôle** : volume de leads, canal d’acquisition, filtrage temporel

### 2 `data/campaign_smartmarket.json`
- **Colonnes** : `campaign_id`, `channel`, `cost`, `impressions`, `clicks`, `conversions`
- **Rôle** : performance média et coûts (CTR, CVR, CPC/CPA/CPL)

### 3 `data/crm_smartmarket.xlsx`
- **Colonnes** : `lead_id`, `company_size`, `sector`, `region`, `status`
- **Rôle** : segmentation et qualité business (MQL/SQL/Client)

---

## ✅ Sélection des observations & variables 
### Filtrage du périmètre
- Conservation uniquement des lignes dont `date` ∈ [2025-09-01 ; 2025-09-30]
- Suppression des doublons sur `lead_id` (évite de gonfler artificiellement les KPI)

### Variables conservées (et justification)
- `lead_id` : clé de jointure entre leads et CRM
- `date` : contrôle du périmètre temporel
- `channel` : comparaison des canaux (objectif central)
- `device` : lecture UX/comportement (utile pour optimisation)
- `cost`, `impressions`, `clicks`, `conversions` : calcul CTR/CVR et coûts
- `company_size`, `sector`, `region` : segmentation métier
- `status` : mesure de la qualité (MQL/SQL/Client)

### Variables exclues
- Variables non présentes dans les fichiers
- Toute donnée identifiante (nom/email/téléphone) : non utile + risque RGPD
- Lignes hors période (hors septembre 2025)

---

## 📈 Analyse univariée & bivariée 
### Analyse univariée
- Variables qualitatives : fréquences / répartitions
  - canaux, région, secteur, statut CRM, device
- Variables quantitatives : statistiques descriptives
  - coût, impressions, clics, conversions (moyenne, médiane, min, max)

### Analyse bivariée (croisements métiers)
- **Canal × Statut CRM** : identifie les canaux qui génèrent le plus de clients
- **Région × Taux client** : repère les zones géographiques les plus rentables
- **Secteur × Taux client** : repère les segments sectoriels les plus convertisseurs

Interprétation attendue :
- un canal performant n’est pas seulement celui qui génère du volume, mais celui qui génère de la **qualité** (clients) à un coût maîtrisé.

---

## 📊 Visualisations — questions métier couvertes
L’application propose des graphiques répondant à des questions claires :
1. **Volume de leads par canal** : quels canaux génèrent le plus de leads ?
2. **Statut CRM par canal** : quels canaux génèrent le plus de SQL / Clients ?
3. **Taux de clients par région** : quelles régions convertissent le mieux ?
4. **CTR et CVR par canal** : efficacité média des canaux (clics et conversions)
5. **CPL estimé par canal** : coût d’acquisition d’un lead selon le canal

Bonnes pratiques :
- titres explicites,
- axes lisibles,
- légendes lorsque nécessaire,
- pas de redondance (volume ≠ qualité ≠ coût ≠ segmentation).

---

## 📌 Dashboard (vue décideur)
Le tableau de bord synthétise les indicateurs clés et permet une lecture rapide.

### KPI affichés (6 max)
- **Leads** : nombre de leads (après filtres)
- **Coût total** : somme des coûts campagnes (canaux filtrés)
- **CTR** : clics / impressions
- **CVR** : conversions / clics
- **CPL** : coût / leads
- **Taux client** : clients CRM / leads

### Filtres
- filtres **globaux** : Canaux + Régions
- appliqués à toutes les pages analytiques (Sélection / Analyse / Visualisations / Dashboard)
- **non appliqués** à : Accueil, Note métier, Carnet technique
- comportement : aucun filtre pré-sélectionné, mais si l’utilisateur ne choisit rien, l’app affiche le résultat global (tous canaux + toutes régions).

---

## 📝 Note d’analyse métier (contenu dans l’application)
La note contient :
- rappel du contexte et des objectifs,
- résultats marquants (volume vs qualité vs coût),
- interprétation métier (CTR ≠ rentabilité ; importance du CRM),
- recommandations opérationnelles :
  - réallocation budget (CPL + taux client),
  - optimisation parcours (CTR haut / CVR faible),
  - ciblage segments rentables (régions/secteurs),
  - alignement marketing ↔ sales (MQL → SQL → Client).

---

## 🛠️ Carnet technique (contenu dans l’application)
Liste des problèmes documentés :
- fichiers introuvables / chemins,
- nettoyage catégories (`strip()`),
- doublons sur `lead_id`,
- divisions par zéro,
- distinction conversions campagnes vs clients CRM,
- export des données filtrées (CSV) et KPI.

---

## 🚀 Fonctionnalités de l’application
- Navigation multi-pages (Streamlit)
- Filtres globaux (canal + région)
- Tableaux d’analyse uni/bivariée
- Visualisations Plotly
- Dashboard KPI
- Exports CSV :
  - données filtrées
  - KPI

---

## 🛠️ Technologies
- Python 3.x
- Streamlit
- Pandas / NumPy
- Plotly Express
- openpyxl (lecture Excel)

---

## 📦 Installation locale
### 1 Cloner le dépôt
```bash
git clone https://github.com/BeyBasso/smartmarket-streamlit.git
cd <smartmarket-streamlit>
