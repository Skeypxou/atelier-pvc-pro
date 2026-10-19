# Atelier PVC Pro

Application Streamlit en français pour la gestion de base d'un atelier de menuiserie PVC.

## Fonctionnalités

- Tableau de bord avec indicateurs clients, produits, devis, fabrication et encaissements
- Répertoire clients : création, recherche, modification et export CSV
- Catalogue : profils PVC, vitrages, accessoires et quincaillerie, avec prix et stock
- Devis avec plusieurs lignes, TVA, statut et téléchargement PDF
- Suivi des travaux de fabrication avec dimensions, finition, vitrage, statut et export CSV
- Factures créées à partir de devis acceptés, paiements partiels ou complets et export PDF
- Sauvegarde et restauration de la base JSON complète

## Lancement local (Windows)

1. Installe Python 3.11 ou 3.12.
2. Décompresse le projet dans un dossier.
3. Ouvre PowerShell dans ce dossier et lance :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

## Déploiement Streamlit Community Cloud

1. Crée un dépôt GitHub vide nommé `atelier-pvc-pro`.
2. Envoie **le contenu de ce dossier** à la racine du dépôt, en conservant les dossiers `atelier_pvc`, `pages` et `storage`.
3. Dans Streamlit Community Cloud, crée une application depuis ce dépôt et choisis `app.py` comme fichier principal.
4. Streamlit installe les dépendances à partir de `requirements.txt`.

## Stockage et sauvegardes

La base de données est le fichier `storage/data.json`, utilisé par tous les modules via `atelier_pvc/store.py`. Les écritures sont atomiques pour limiter le risque de corruption.

**Limite importante :** le système de fichiers local d'une application hébergée sur Streamlit Community Cloud n'est pas un stockage persistant garanti. Utilise la page **Sauvegarde** pour télécharger régulièrement un fichier JSON et conserve-le ailleurs. Pour des données d'entreprise critiques ou un usage multi-utilisateur, configure ensuite une base de données persistante.

## Limites fonctionnelles à connaître

- Les calculs des coupes PVC ne sont pas automatisés : les jeux, renforts, soudures et retraits varient selon le système de profilés et les instructions du fabricant.
- Le PDF est un modèle générique sans logo ni coordonnées commerciales personnalisés.
- Cette version ne comporte pas encore de système de connexion ni de rôles utilisateur. Ne publie pas de données confidentielles dans une application accessible publiquement.
