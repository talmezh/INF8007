# INF8007 - Projet Web scraper

Le but du projet est de développer un script qui permet aux développeurs web de détecter la présence de liens morts sur leur site. Le développeurs n'a qu'à fournir le lien URL vers son site web et le script lui fournit un rapport de tous les sites vérifiés ainsi que leur status, soit fonctionnel ou non avec le code correspondant.

## Installation et utilisation du script
Une fois que le repo est clôné, l'exécution de la commande suivante permet de créer un environement anaconda contenant toutes les librairies nécessaires pour l'utilisation de notre script:
```
conda env create -f INF8007_env.yml
```
Ensuite, pour exécuter le code il suffit d'activer l'environnement anaconda crée:
```
conda activate INF8007
```
Puis lancer le script en donnant le site web à analyser comme argument:
```
python WebScrapping.py https://www.nom-du-site.com
```
À la sortie, le fichier `link_repost.csv` contient les résultats de l'analyse avec tous les sites vérifiés ainsi que leur code de status

## Outils

* [Python](https://www.python.org/) - Langage de script
* [Anaconda](https://anaconda.org/) - Gestion de libraries

## Auteurs

* **Denis Corbin** - *Initial work* - [cacoool](https://github.com/cacoool)
* **Tal Mezheritsky** - *Initial work* - [talmezh](https://github.com/talmezh)
