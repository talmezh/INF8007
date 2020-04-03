# INF8007 - Projet Web scraper

Le but du projet est de développer un script qui permet aux développeurs web de détecter la présence de liens morts sur leur site. Le développeurs n'a qu'à fournir le lien URL vers son site web et le script lui fournit un rapport de tous les sites vérifiés ainsi que leur status, soit fonctionnel ou non avec le code correspondant.

## Installation et utilisation du script
Une fois que le repo est clôné, l'exécution de la commande suivante permet de créer un environement anaconda contenant toutes les librairies nécessaires pour l'utilisation de notre script:
```
conda env create -f INF8007_env.yml
```
Ensuite, avant d'exécuter le code il faut activer l'environnement anaconda crée:
```
conda activate INF8007
```
Puis lancer le script en donnant les arguments désirés:
```
python web_scrapping.py --IN arg1 arg2 ... --TYPE arg3 arg4 ... --CRAWL arg5 arg6 ...
```
À la sortie, le fichier `link_repost.csv` contient les résultats de l'analyse avec tous les sites vérifiés ainsi que leur code de status

## Précisions sur les arguments acceptés
Le script s'attends à recevoir des arguments selon la structure suivante: 
```
--IN arg1 arg2 ... --TYPE arg3 arg4 ... --CRAWL arg5 arg6 ...
```
`--IN` représente les éléments à analyser. Ils sont présenté sous forme de `string` et peuvent représenter soit un site URL, un fichier .html ou bien un fichier text. 

`--TYPE` représente les types d'éléments  analyser. Les types accéptés sont `h` pour un fichier .html, `u` pour un URL ou `f` pour un fichier texte

`--CRAWL` représente l'activation du crawling. Le script accepte soit `False` pour désactiver le crawling ou `True` pour l'activer

Les arguments doivent être séparés d'espaces. Le script peut accepter multiple entrées pour chaque argument pourvu que le nombre est le même pour chacun. Par exemple:
```
python web_scrapping.py --IN test.html http://localhost:3000/ --TYPE h u --CRAWL False True
```
Ici le script analysera un fichier .html et un site en désactivant le crawling pour le fichier .html
Il est également possible de donner un fichier texte au script (en spécifiant la l'option `f` pour l'argument `--TYPE`). Le fichier texte doit contenir tous les triplets d'arguments `--IN`, `--TYPE`, `--CRAWL` séparés par des virgules avec les options décrites précédemment.

## Utilisation du script bash
Le script bash inclus dans ce repo sous le nom `script_bash` permet à l'utilisateur d'exécuter le scirpt `web_scraping.py` sur un serveur node contenu dans un repo github.

Afin de lancer le script l'utilisateur doit tout d'abord d'activer l'environnement conda approprié:
```
conda activate INF8007
```
Ensuite, il faut appeller le script bash en lui fournissant 2 arguments. L'argument 1 contient le lien vers le repo github qui contient le serveur Node à initialiser. L'argument 2 est le numéro de port où le serveur sera lancé (localhost:PORT).
```
bash script_bash https://github.com/user/repo.git PORT
```

## Utilisation et vérification du typage
Afin de vérifier que le typage ne comporte pas d'erreur dans le code, nous avons utilisé MyPy qui détecte les erreurs de typage. Si l'utilisateur souhaite vérifier que le typage est adéquat, il peut le faire comme suit en activant d'abord l'environnement Conda:
```
conda activate INF8007
```
Puis appeler le module sur le script python devant être analysé:
```
python -m mypy web_scrapping.py
```
Les erreurs qui apparaissaient ici on été corrigé au cours du projet.

## Linter
Un Linter (PyLint) est appelé au début du script lors de son exécution et les outputs sont loggés dans StdOut et StdErr.

## Outils

* [Python](https://www.python.org/) - Langage de script
* [Anaconda](https://anaconda.org/) - Gestion de libraries

## Auteurs

* **Denis Corbin** - *Initial work* - [cacoool](https://github.com/cacoool)
* **Tal Mezheritsky** - *Initial work* - [talmezh](https://github.com/talmezh)
