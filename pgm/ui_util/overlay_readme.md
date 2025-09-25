# overlay.py => overlay_socket_save.py

 Changements notables par rapport au fichier précédent
## Imports

Ajoutés :

threading

socket

Changement :

handler_addr = "http://localhost:5000/process_image" est maintenant défini (dans le premier fichier, il était seulement commenté).

Supprimés/absents :

La partie Flask en bas du fichier est supprimée (la route recieve_data n’existe plus, elle était commentée avant).

## Capture d’écran

Fonction capture_window : identique à la version précédente, sauf qu’elle utilise désormais la variable handler_addr active.

## Gestion des événements (clavier/souris)

Pas de modification dans ctrl_event, event_appened, listen_keyboard, ou listen_mouse.

Toujours un potentiel core dump si aucun mouvement souris avant clic (commentaire conservé).

## Nouvelle fonctionnalité ajoutée : serveur socket

Nouvelle classe : SocketServerThread(threading.Thread)

Lance un serveur TCP sur 0.0.0.0:5002.

Accepte des connexions entrantes.

Reçoit des données (recv(1024)).

Affiche "recived from handler : " et appelle un callback si défini (ici → Overlay.set_text).

Ce mécanisme permet de mettre à jour l’overlay depuis un autre processus via un simple envoi sur le port 5002.

## Overlay

Ajout d’un serveur socket dans l’overlay 
set_text a changé :

Avant : si text == None → reprenait self.text.

Maintenant : si text == "" → reprend self.text.

🏁 main()

Identique, sauf que la partie Flask (create_route) n’existe plus.

Toujours : récupère la fenêtre active, crée l’overlay, démarre listeners clavier/souris, affiche l’overlay PyQt5.

##  Synthèse des différences

### Ajouts :

threading et socket.

Classe SocketServerThread pour communication via TCP.

Démarrage automatique du serveur socket dans Overlay.

### Modifications :

set_text : logique ajustée ("" au lieu de None comme fallback).

handler_addr activé (non plus commenté).

Suppressions :

Tout le code Flask (même commenté dans la V1).

Commentaires sur create_route.

## En résumé :
Le deuxième fichier ajoute une communication réseau via socket TCP (port 5002), permettant de mettre à jour dynamiquement le texte de l’overlay depuis un programme externe, en remplacement du début d’API Flask de la première version.

# overlay_socket_save.py => overlay_socket.py

## Changements par rapport au fichier précédent
 Fonction capture_window

Ajout de logs 
Vérification taille 
→ Avant, le code tentait toujours la capture. Maintenant, il saute si la taille est nulle.

Gestion des erreurs réseau :
→ Avant, le requests.post était direct et pouvait crasher.
→ Maintenant, c’est entouré d’un try/except/finally

🖱️ Fonction ctrl_event

Le comportement du clic souris a changé :

Avant : une logique avec if event is None, elif type(event) == mouse.Events.Click, etc.

Maintenant : cette logique est commentée et remplacée par une boucle bloquante :
→ Plus simple, mais bloquant tant qu’aucun clic n’est fait.

Ajout de messages de progression :

"first click achieved"

"second click achieved"

📝 Résumé des différences
Zone	Ancien comportement	Nouveau comportement
capture_window	Pas de check sur largeur/hauteur, envoi direct au handler	Vérifie si w ou h = 0 → skip. Ajout logs "executing capture". Gestion erreurs réseau avec try/except/finally.
ctrl_event	Vérification conditionnelle if/elif/while sur événements souris	Remplacé par boucle bloquante while type(event) != mouse.Events.Click. Ajout de logs "first click achieved", "second click achieved".
Divers	Docstring collé à la signature de fonction	Ligne vide avant docstring.

# overlay_socket.py => overlay_test.py

1️⃣ Changements majeurs
a) Gestion des raccourcis clavier (Hotkeys)

Nouveau dictionnaire actions :
→ Définit des actions associées à certaines touches.

listen_keyboard(qwidget, context) :

Passage de la simple écoute des touches (on_press) à l’utilisation de keyboard.GlobalHotKeys :



    Cela permet de déclencher :

        change_mod() → changer le mode/couleur de l’overlay.

        leave_app() → quitter l’application.

        capture() → capture de la zone définie par deux clics.

Fonction change_mod() ajoutée pour gérer la modification du mode dans Overlay.

b) Overlay évolué

La classe Overlay a été améliorée pour supporter plusieurs “modes” visuels :

Nouvel attribut self.mod et liste de couleurs self.colors.

Nouvelle méthode change_mod() :

Incrémente le mode actif et appelle generate_interface().

Nouvelle méthode generate_interface() :

Reconstruit le QLabel avec la couleur correspondant au mode courant.

Permet de changer dynamiquement l’affichage de l’overlay (couleur).

Connexion du signal update_mod dans Overlay 

c) Suppression/commentaires de certaines fonctions

Plusieurs appels à event_appened et mise à jour de context ont été commentés dans listen_keyboard et listen_mouse :

→ Probablement pour simplifier l’écoute et éviter les conflits lors du test des hotkeys.

Le double get_active_window() défini dans ce fichier (répétition du code) semble être un copier-coller de l’ancien fichier.

d) Socket server

SocketServerThread :

Le callback de server_thread dans Overlay est maintenant directement :


Plus besoin de wrapper une fonction : les données reçues sont directement envoyées à l’overlay

e) Capture d’écran

Pas de changements majeurs dans capture_window() ; reste la même fonctionnalité (capture de fenêtre ou zone, envoi HTTP).

f) Nettoyage et améliorations mineures

Certaines impressions/commentaires ont été ajustés.

L’architecture du clavier permet maintenant plusieurs touches combinées pour déclencher des actions simultanées.

Suppression de quelques doublons et commentaires inutiles.

2️⃣ Fonctionnalités nouvelles ou modifiées
Fonction / Classe	Changements / Nouveautés
Overlay	Support de plusieurs modes visuels (couleurs), méthode change_mod() et generate_interface().
listen_keyboard	Passage à keyboard.GlobalHotKeys pour gérer les combinaisons de touches et actions multiples.
SocketServerThread	Callback direct vers comm.update_text.emit.
Signal update_mod	Ajout pour changer le mode de l’overlay via raccourci clavier.
ctrl_event()	Inchangé, toujours gestion de capture avec deux clics.
actions	Nouveau dictionnaire définissant les touches pour les actions.

# overlay_test.py => overlay_test2.py

Résumé des fonctionnalités implémentées

Gestion des actions clavier :

Les touches sont maintenant gérées via un set pressed et un mappage controls et actions.

L’utilisateur peut appuyer sur Ctrl+Alt puis sur une touche (c pour capture, m pour changer le mode) pour déclencher des actions.

La touche Ctrl+Esc quitte l’application.

Ajout des fonctions wait_for_two_clicks() et wait_for_action() pour gérer les clics et les actions de manière séquentielle.

Capture d’écran :

La fonction capture_window() reste similaire.

Ajout de la fonction capture_info(first, second) pour calculer la position et la taille à partir de deux clics de souris.

Affichage des informations :

Nouvelle classe DisplayInfo(QWidget) pour afficher un dictionnaire hiérarchique de données dans un overlay.

Support récursif des dictionnaires imbriqués.

Style visuel amélioré : fonds semi-transparents, coins arrondis, polices et couleurs personnalisées.

Méthodes generate_view(), create_info_widget() et set_infos() pour gérer dynamiquement l’affichage des infos.

Communication avec le serveur :

SocketServerThread décode maintenant les données JSON reçues et les transmet via le signal update_infos.

Gestion du format attendu par le handler : { "from_server": {...}, "result": {...} }.

Overlay HUD :

L’overlay est maintenant plein écran (screen.size()), pas juste une petite fenêtre fixe.

info_widget (DisplayInfo) est intégré dans l’overlay et affiché uniquement quand mod == 0.

Signal update_infos relié à set_display_widget_infos() pour mettre à jour dynamiquement les infos dans l’overlay.

generate_interface() gère l’affichage conditionnel du label et de l’info_widget selon le mode.

Différences majeures par rapport au premier fichier
Aspect	Ancien fichier	Nouveau fichier
Gestion du clavier	Simple listener global, action Ctrl+Alt+C pour capture	Système plus robuste avec set pressed, actions différenciées (c capture, m change mode), appui séquentiel Ctrl+Alt + action
Capture de zone	Direct dans ctrl_event() avec boucle sur mouse.Events()	Nouveau mécanisme wait_for_two_clicks() + capture_info(), plus clair et séquentiel
Affichage des infos	Pas d’affichage de dictionnaires	Classe DisplayInfo pour afficher des infos hiérarchiques avec styles et couleurs, intégrée dans Overlay
Overlay	Overlay limité avec label et changement de couleur	Overlay plein écran, intégration de DisplayInfo, mode cyclique qui affiche/masque l’info_widget
Communication serveur	SocketServerThread envoie texte brut	Décodage JSON, signal update_infos pour mise à jour dynamique des infos dans l’overlay
Structure du code	Moins modulable, fonctions dispersées	Plus modulaire avec separation DisplayInfo, gestion clavier/actions plus claire, meilleure intégration avec l’overlay
JSON et handler	Non présent	Ajout du support JSON pour handler_addr http://localhost:5000/process_image

# overlay_test2.py => overlay_test3.py

Voici un rapport détaillé sur ce nouveau fichier et les différences avec le précédent que tu m’as envoyé :

1️⃣ Ce qui est implémenté dans ce fichier
Modules et dépendances

Toujours PyQt5, pynput pour clavier/souris, mss pour capture écran.

Ajout notable : sqlite3 pour la gestion d’une base de données locale.

Ajout du module queue et threading pour gérer une queue de tâches (task_queue) et un worker thread.

Import de connection pour récupérer l’ID utilisateur (probablement un module externe pour gérer l’authentification ou la connexion).

Nouvelle classe : Database

Gestion d’une base SQLite locale (app.db) avec une table sessions.

Méthodes :

add_session(idu) : ajoute une session utilisateur.

get_current_session(idu) : récupère l’ID de la dernière session.

Gestion du nom de l’application

Fonction extract_application_from_window_name(context) :

Extrait le nom de l’application depuis le titre de la fenêtre active à l’aide d’une regex.

Retourne un nom simplifié ou complet si pas de correspondance.

Task Queue et Worker

Une queue de tâches (queue.Queue()) est créée.

Thread worker (worker) qui exécute les fonctions mises dans la queue.

Exemple d’utilisation : capture_window peut maintenant être exécuté dans le thread worker pour éviter de bloquer l’UI.

Modification de capture_window

capture_window prend maintenant un contexte (context) en argument pour récupérer le window_name.

L’envoi HTTP vers le handler inclut maintenant des données JSON supplémentaires avec le nom de la fenêtre.

Modifications dans les événements clavier

listen_keyboard accepte maintenant la task queue pour mettre des tâches asynchrones (ex. capture d’écran).

Les actions déclenchent maintenant le worker via la queue 

La fonction event_appened gère le changement de fenêtre et met à jour le contexte.

Overlay

Overlay prend maintenant un context et un display_dict.

Nouvelle méthode get_display_dict_str pour convertir le dictionnaire d’affichage en texte.

La méthode set_text2 met à jour le label avec le contenu de display_dict (au lieu de seulement un texte statique).

Ajout de la base Database pour créer et récupérer la session de l’utilisateur.

Suppression de certains paramètres obsolètes et simplification de l’UI (label unique affichant display_dict).

Main

Nouveau main :

Initialise la queue de tâches et le worker.

Crée le contexte avec window et user.

Utilise Overlay avec display_dict pour afficher le nom de la fenêtre.

Intègre l’ID utilisateur depuis connection.main().

2️⃣ Différences majeures avec le précédent fichier
Aspect	Ancien fichier	Nouveau fichier	Commentaire
Gestion utilisateur	Pas d’utilisateur	Gestion d’utilisateur via connection et Database	Ajout d’une logique de session locale
Capture d’écran	Synchrone	Asynchrone via task queue et worker	L’UI ne bloque plus pendant la capture
Context / Window	context minimal	context étendu avec window_name et session	Facilite le suivi des changements de fenêtre
Overlay affichage	Texte statique ou DisplayInfo	Label affichant display_dict et DisplayInfo	Plus dynamique et lié au contexte actuel
Event clavier	Direct	Queue pour les actions asynchrones	UI plus réactive
Socket server	Thread TCP simple	Même principe mais intégré au contexte avec Overlay	Aucun changement fonctionnel majeur ici
Suppression	Certaines fonctions inutilisées/commentées	Nettoyage et suppression du code mort	Plus clair et structuré

# overlay_test3.py => overlay_test4.py

1. Imports

De nombreux modules PyQt5 ont été ajoutés :

QTabWidget, QListWidget, QMenuBar, QAction, QDockWidget, QMenu, QTreeWidget, QTreeWidgetItem, QPoint.

Ajout de QPoint pour gérer le drag & drop de la fenêtre.

2. Gestion des tables SQLite

Renommage de create_table() → create_tables().

Ajout de nouvelles tables et colonnes :

Activation des clés étrangères : PRAGMA foreign_keys = ON.

Table users avec id, idu, email, password_hash, created_at.

Table sessions avec clé étrangère vers users(id).

Table apps et captures avec clés étrangères.

Modifications du calcul des id pour les sessions si aucun résultat trouvé (res = 1).

3. Capture de fenêtre

Ajout de l’argument process dans capture_window().

Passage à MSS pour la capture complète de la fenêtre (sct.grab), création d’une image PIL et sauvegarde PNG.

Implémentation d’un envoi de l’image vers un handler via send_image_to_handler().

Gestion des erreurs et sauvegarde en cas d’échec d’envoi.

4. Traitement des noms de fenêtres

Nettoyage des espaces dans my_match.group(1) et context["window"]["name"] via re.sub(" ","", ...).

5. Interface utilisateur et overlay

Modification du comportement des widgets :

Gestion des événements de drag (mousePressEvent, mouseMoveEvent, mouseReleaseEvent).

Ajout de FullModeApp pour un mode plein écran avec barre de menu et arbre des sessions/captures.

Création de nouvelles méthodes pour gérer différents modes de l’overlay :

setup_partial_mode()

setup_full_mode()

setup_passive_mod()

Changement de police et gestion de l’affichage selon le mode.

Ajustement de la transparence et des flags de la fenêtre selon le mode.

6. Écoute des entrées utilisateur

Modification de listen_mouse() pour inclure task_queue.

Suppression de nombreux print() temporaires, mais certains restent pour debug.

7. Améliorations UI

Ajout de self.create_interface() pour initialiser l’interface et les widgets.

Gestion de QLabel et QWidget avec self comme parent pour meilleure hiérarchie.

Ajout de WordWrap pour les labels.

Ajout des modes (partial, passive, full) dans self.mods.

Mise à jour des méthodes set_text2() et display_dict.

8. Refactor et nettoyage

Suppression de nombreux commentaires et code mort.

Réorganisation des fonctions pour une meilleure lisibilité.

Correction de bugs liés à window_name.

Remplacement de chaînes de caractères statiques et prints pour un usage plus dynamique.

9. Nouveaux composants et fonctionnalités

FullModeApp :

Barre de menu avec actions (New Session, Quit, Preferences, About).

Arborescence des sessions et captures.

Onglets closables pour chaque analyse.

Gestion des événements utilisateur pour interagir avec le tree view et les onglets.

Résumé global

Le fichier overlay_test4.py est une version significativement améliorée et étendue de overlay_test3.py :

Base de données enrichie avec tables utilisateurs, applications, captures et sessions.

Gestion complète des captures de fenêtres avec envoi à un handler.

Amélioration de l’interface PyQt5 avec plusieurs modes d’affichage et plein écran.

Refactorisation majeure pour modularité, lisibilité et évolutivité.

Ajout de composants interactifs comme menus, onglets et arbre de sessions/captures.

# overlay_test4.py => overlay_test5.py

1. Importations

Ajout de nouveaux modules PyQt5 : QLineEdit et QToolButton.

Suppression de l’import direct de sqlite3 et loguru; ajout d’un module de logging personnalisé log et d’un module db.Database

2. Initialisation et données par défaut

Ajout de l’appel init_log().

Nouveau dictionnaire default_infos2 introduit pour stocker des informations par défaut supplémentaires.

default_infos existant conservé.

3. Gestion de la base de données

La classe Database interne a été entièrement supprimée.

Remplacée par l’utilisation de Database depuis le module db.

4. Remplacement de print par log

Tous les appels à print pour le suivi et le debug ont été remplacés par log("niveau", message) avec différents niveaux (i, s, d, w, c).

Exemple :

5. Contexte

Introduction de la classe Context pour gérer window, user, session et window_name.

Méthodes ajoutées :

extract_application_from_window_name

change_window

to_json pour sérialisation.

Impact :

Suppression de l’ancien usage de context comme dictionnaire.

context devient maintenant un objet avec méthodes associées.

6. Overlay et info widget

DisplayInfo modifié pour accepter des dimensions personnalisées (xi, yi, w, h).

Vue améliorée pour les dictionnaires imbriqués :

Ajout d’un bouton collapsible pour chaque sous-dictionnaire (QToolButton).

Gestion de l’affichage et du masquage via toggle.

Suppression des anciens print pour l’affichage des infos, remplacés par log.

7. Gestion des modes d’overlay

passive mode extrait en méthode séparée setup_passive_mod.

partial mode légèrement modifié.

fullmode géré avec activateWindow() et gestion des attributs Qt.

8. Gestion des captures

Changement de nommage et sérialisation des images :

Conversion du context en JSON lors de l’envoi au handler.

Logging des actions de capture et d’envoi au lieu des prints.

9. UI - Arborescence et filtres

Ajout d’un QLineEdit pour filtrer les sessions/captures dans l’arborescence.

Méthode filter_tree ajoutée pour filtrer dynamiquement les items.

Méthode populate_tree ajoutée pour peupler la treeview.

10. Correction et nettoyage

Plusieurs corrections mineures :

Alignement de styles dans DisplayInfo.

Suppression ou commentaire de lignes print inutiles.

Ajout de log pour toutes les actions importantes (clics, touches pressées, événements).

Gestion plus robuste des sessions (avec logs pour ID de session par défaut).

11. Résumé des impacts principaux

Architecture : Passage de context dictionnaire à objet Context.

Logging : print → log avec niveaux.

Base de données : Utilisation d’une classe externe Database avec méthodes centralisées.

UI :

Collapsible pour dictionnaires imbriqués.

Ajout barre de recherche pour sessions/captures.

Affichage des informations amélioré et dynamique.

Modes overlay : Code plus structuré et modulaire (setup_passive_mod).

Captures : Sérialisation JSON et noms de fichiers enrichis.