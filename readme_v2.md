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

---

## État de l’art des fonctionnalités développées

### 1. Capture d’écran
- Initialement simple capture de fenêtre via PIL/mss.
- Ajout de vérifications taille, logs et gestion erreurs.
- Passage à capture asynchrone via task queue pour non-blocage de l’UI.
- Envoi JSON enrichi au handler.

### 2. Overlay
- Passage d’un simple QLabel à un overlay multi-mode (label + info_widget).
- Support plein écran, couleurs dynamiques selon mode.
- Modes : partial, passive, full.
- Gestion dynamique de contenu via DisplayInfo pour dictionnaires imbriqués.
- Intégration de QTreeWidget et QLineEdit pour sessions/captures avec filtres.

### 3. Événements clavier/souris
- Écoute initiale via `pynput`.
- Passage à hotkeys globaux (`keyboard.GlobalHotKeys`) avec actions associées.
- Séquençage pour capture ou changement de mode.
- Boucles de clic souris remplacées par fonctions `wait_for_two_clicks()`.

### 4. Communication réseau
- TCP socket server pour mises à jour texte/infos.
- Support JSON pour communication avec handler et socket.
- Callback direct vers overlay (signal/slot PyQt5).

### 5. Gestion utilisateur et sessions
- Base SQLite locale avec tables users, sessions, apps, captures.
- Gestion des sessions et context utilisateur.
- Contexte enrichi (window, user, session) via objet `Context`.

### 6. Architecture et modularité
- Passage progressif d’un code linéaire vers un code modulaire, clair et structuré.
- Séparation Overlay, DisplayInfo, worker thread, context.
- Logging centralisé.
- Support multi-mode et interaction complète UI.

### 7. UI / Ergonomie
- Widget plein écran, drag & drop, onglets closables.
- Treeview pour sessions et captures avec filtre dynamique.
- Styles visuels améliorés (semi-transparence, coins arrondis, couleurs).
- Collapsible pour dictionnaires imbriqués.

---

**Remarque :**  
L’architecture finale (`overlay_test5.py`) est modulable, intègre la capture asynchrone, la gestion utilisateur via DB, l’overlay multi-mode et l’affichage dynamique des informations. Le logging et la communication réseau sont centralisés et robustes.
