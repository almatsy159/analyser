# Évolution des fichiers overlay*.py

Ce document synthétise les changements, ajouts, suppressions et fonctionnalités des fichiers `overlay*.py` jusqu’à `overlay_test5.py`.

---

## Tableau comparatif des évolutions

| Fichier | Ajouts / Nouvelles fonctionnalités | Modifications | Suppressions / Nettoyage | Notes clés |
|---------|-----------------------------------|---------------|-------------------------|------------|
| **overlay.py → overlay_socket_save.py** | - Classe `SocketServerThread` (serveur TCP sur 5002)<br>- Démarrage automatique du serveur dans Overlay | - `set_text` : fallback sur `""` au lieu de `None`<br>- `handler_addr` activé | - Flask (routes/commentaires) supprimé | Permet mise à jour de l’overlay via TCP depuis un autre processus |
| **overlay_socket_save.py → overlay_socket.py** | - Logs dans `capture_window`<br>- Gestion erreurs réseau avec `try/except/finally` | - `ctrl_event` : boucle bloquante pour clic souris<br>- Messages progression ("first click achieved", "second click achieved") | - Docstring déplacé pour lisibilité | Capture écran plus sûre et robuste, simplification clic souris |
| **overlay_socket.py → overlay_test.py** | - Hotkeys avec `keyboard.GlobalHotKeys`<br>- Overlay multi-mode avec couleurs (`change_mod`, `generate_interface`)<br>- Callback socket direct | - Suppression de certaines fonctions/commentaires dans listeners | - Doublons et code obsolète nettoyés | Overlay devient dynamique avec mode cyclique et raccourcis clavier |
| **overlay_test.py → overlay_test2.py** | - Gestion clavier via `pressed` set et actions séquentielles (Ctrl+Alt + touche)<br>- `wait_for_two_clicks()`, `wait_for_action()`<br>- Classe `DisplayInfo` pour dictionnaires hiérarchiques<br>- Overlay plein écran, info_widget dynamique<br>- SocketServerThread décode JSON | - `capture_window` similaire, mais intégration info contextuelle | - Suppression code mort | UI plus dynamique et intégrée, capture et affichage des infos améliorés |
| **overlay_test2.py → overlay_test3.py** | - SQLite avec tables sessions et utilisateurs<br>- Task queue et worker thread pour capture asynchrone<br>- `extract_application_from_window_name()`<br>- Overlay affichage dynamique via `display_dict` | - `capture_window` async via queue<br>- Context enrichi avec session et window_name | - Suppression de paramètres obsolètes, simplification UI | UI réactive, capture non bloquante, gestion utilisateur locale |
| **overlay_test3.py → overlay_test4.py** | - Nouveaux widgets PyQt5 (QTabWidget, QTreeWidget, etc.)<br>- FullModeApp (menus, onglets, treeview)<br>- Gestion drag & drop<br>- Plusieurs modes overlay (partial, passive, full)<br>- Base de données étendue : users, apps, captures, sessions | - Capture de fenêtre via MSS + PIL<br>- send_image_to_handler() avec erreurs gérées<br>- Nettoyage noms de fenêtres | - Code mort et commentaires temporaires supprimés | Version fortement modulaire, interface complète et interactive, captures gérées proprement |
| **overlay_test4.py → overlay_test5.py** | - Context devient objet `Context` avec méthodes associées<br>- Base de données via module externe `db.Database`<br>- Logging centralisé (`log()`)<br>- DisplayInfo amélioré avec collapsible pour dictionnaires imbriqués<br>- Barre de recherche/filter pour treeview<br>- Sérialisation JSON pour captures | - set_text2() et overlay adaptatifs selon mode<br>- capture_window envoie JSON enrichi | - Suppression de la classe Database interne<br>- print remplacés par log | Code plus structuré et professionnel, UI et overlay modulaires, logging et base de données centralisés |
| **overlay_test5.py → overlay_test7.py** | - Introduction de la classe `Capture` (gestion complète de la capture, sauvegarde, calcul MD5 pour déduplication).<br>- Classe `Sender` : gestion des captures côté client, envoi batch via `send_all`, SID pour traces.<br>- Réintégration d'un `SocketServerThread` (TCP sur 127.0.0.1:5002) qui décode JSON et appelle un callback (émission `update_infos`).<br>- Ajout d'un mode *feed capture* (capture multiple pilotée par le scroll souris) avec logique de déduplication par hash.<br>- Endpoints HTTP configurables : `handler_addr`, `handler_portal`, `handler_aggregate` et envoi via `requests` (buffer `io.BytesIO`).<br>- `FullModeApp` enrichi : barre de menu (File/Edit/Help), barre de recherche, QTreeWidget dynamique avec filtre et QTabWidget closable.<br>- Intégration `connection.main()` pour récupérer `user_id` à l'exécution.<br>- Utilisation systématique du `task_queue` + `worker` pour exécuter captures/envois de façon asynchrone. | - `Overlay` initialise la DB (`Database()`), crée les tables et ajoute la session (`db.add_session`) au démarrage ; `context.session` est mis à jour avec l'ID retourné.<br>- `set_text2()` est remplacé par un flux `add_dict_to_info()` qui met à jour `display_dict` et rafraîchit `DisplayInfo` (`info_widget3`).<br>- `worker()` et l'envoi (`Sender.send_capture/send_all`) sont robustifiés (logs, gestion d'erreurs, retries basiques absents mais journalisation présente).<br>- `Capture.capture()` utilise `mss` + `PIL` et sauvegarde par défaut dans `data/img`, calcule un hash MD5 pour la détection de doublons.<br>- `Communicate` est étendu avec `update_capture` (emission d'objet `Capture`) et `update_infos` (réception du JSON socket). | - Nettoyage partiel : suppression de vieux tests et commentaires redondants.<br>- Restent encore des `print()` et quelques traces de debug, ainsi que des duplications (deux implémentations similaires de `extract_application_from_window_name`) à corriger ultérieurement.<br>- Petits bugs/cases limites observés (quelques typos/commentaires résiduels, bloc `if self.packet_send > 0:v` erroné) — nécessite un nettoyage de code. | Pipeline de capture/envoi structuré (Capture → Sender → queue/worker). Socket TCP pour retours JSON vers UI. Feed capture et déduplication MD5 permettent envoi batched et réduction du bruit. |

---

## État de l’art des fonctionnalités développées

### 1. Capture d’écran
- Initialement simple capture de fenêtre via PIL/mss.
- Ajout de vérifications taille, logs et gestion erreurs.
- Passage à capture asynchrone via task queue pour non-blocage de l’UI.
- **Nouvelle étape (v7) :** encapsulation dans la classe `Capture` avec sauvegarde sur disque, conversion PIL, et calcul MD5 de l’image pour détection de doublons. Support d’un mode *feed* pour captures répétées pilotées par le scroll souris.
- Envoi JSON/en-têtes et buffer via `requests` pour traitement par un handler externe.

### 2. Overlay
- Passage d’un simple QLabel à un overlay multi-mode (label + info_widget).
- Support plein écran, couleurs dynamiques selon mode.
- Modes : partial, passive, full.
- Gestion dynamique de contenu via DisplayInfo pour dictionnaires imbriqués.
- Intégration de QTreeWidget et QLineEdit pour sessions/captures avec filtres.
- **Nouvelle étape (v7) :** DisplayInfo (`info_widget3`) mis à jour via `add_dict_to_info` ; `Overlay` démarre un `SocketServerThread` qui permet de recevoir des informations de traitement externes et de les injecter dans l’UI.

### 3. Événements clavier/souris
- Écoute initiale via `pynput`.
- Passage à hotkeys globaux avec séquençage (Ctrl+Alt puis touche d’action).
- `wait_for_two_clicks()` pour sélectionner une zone.
- **Nouvelle étape (v7) :** ajout du *feed capture* piloté par le scroll souris (collecte multiple + envoi conditionnel), et meilleure intégration des signaux PyQt (`update_capture`, `update_timer`).

### 4. Communication réseau
- TCP socket server pour mises à jour texte/infos (réintroduit et utilisé en v7).
- Support JSON pour communication entre handler et socket.
- Envoi HTTP multipart (`requests.post`) pour les images avec métadonnées (`context`, `process`, `sid`, `cid`).
- Trois endpoints de travail : handler (process-image), portal (envoi individualisé) et aggregate (envoi batch/flow).

### 5. Gestion utilisateur et sessions
- Base SQLite locale via `pgm.ui_util.db.Database` gère users, sessions, captures.
- **v7 :** `Overlay` crée automatiquement une session à l’ouverture (`db.add_session`) et récupère l’id (`get_session`) ; ce `id_session` est appliqué au `Context`.

### 6. Architecture et modularité
- Passage progressif d’un code linéaire vers un code modulaire, clair et structuré.
- Séparation Overlay, DisplayInfo, worker thread, context.
- **v7 :** pipeline Capture → Sender → task_queue/worker clairement établi. Le socket TCP permet un canal de retour asynchrone vers l’UI. Certains points restent à uniformiser (duplication de fonctions utilitaires, prints / traces temporaires à supprimer).


### 7. UI / Ergonomie
- Widget plein écran, drag & drop, onglets closables.
- Treeview pour sessions et captures avec filtre dynamique.
- Styles visuels améliorés (semi-transparence, coins arrondis, couleurs).
- `FullModeApp` enrichi d’une barre de menus basique, d’une barre de recherche fonctionnelle, et d’un `QTabWidget` closable pour ouvrir des analyses depuis la treeview. 
- **v7 :** DisplayWidget en module (dragable et scrollable). Fonction escape pour afficher masquer le widget (conflit probable avec le mode (necessite verification de l'etat avant affichage !))

---

**Remarque :**  
L’architecture finale (`overlay_test5.py`) est modulable, intègre la capture asynchrone, la gestion utilisateur via DB, l’overlay multi-mode et l’affichage dynamique des informations. Le logging et la communication réseau sont centralisés et robustes.
