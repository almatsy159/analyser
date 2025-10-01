# Analyser project v2

## Project 

### old version

see readmev0.md 

many problem occured (concurency, exploiting data,monolith) so a new version mod oriented to handle different part of program

see readmev1.md

many change have been made in the architecture of the project (anaylse, uv, module...), many issue have been solved since v1 (llm call 'not anymore revelant for now' , display widget...) 

### architecture plan

main2.py : should run the overlay/ui part and launch (and leave properly) other server needed

dockerise ? we may need to dockerise the app to handle (run and quit) server and port

each part of pgm will have dedicated port to send/recieve data 

### effective architecture

right now here is what is implemented :
overlay_socket.py (listen on 5002), handler.py (5000), server_cv.py (5001), main2.py


### gestion d'environement

- add virtual env (analyser)
- Use uv
- pyproject.toml
- utilise : pip install -e . (permet de gerer les fichiers comme des packages (import de log.py,db.py,setup.py, implementation des tests...) dans tout le projet)

## Component

### main2


### analyse

theme extraction (lda) implemented , generate a dataset (with main2.py) 
### handler

handler get ui message and forward it to the correct server

routes : 

- /portal
...

--- 

Description

handler.py provides a Flask-based HTTP API for handling image and text data, processing it with external services, and sending results to overlays. It also includes classes to manage sender/receiver structures for content.

Dependencies

Flask

Flask-SocketIO

requests

numpy

cv2

socket

pgm.contract (local module)

Global Variables

open_cv_addr: URL for external image processing service.

overlay_addr: URL or socket for sending processed data.

default_model: Default LLM model name.

ollama_addr: URL for LLM API.

default_process_addr: Default image processing URL.

default_prompt: Template for LLM prompts.

Classes
Sender_handler

Manages multiple senders.

Attributes:

rhid: Class-level ID counter.

senders: Dictionary mapping sender IDs to receiver objects.

Methods:

add_sender(reciever): Adds a new sender.

check_reciever(reciever): Checks if a receiver exists; adds it if not.

ContentStructure

Represents structured content and extracts key fields.

Constructor:

```python
ContentStructure(content)

```
Parameters:

content (dict): Content to structure.

Attributes:

structure: List of expected keys.

file, process, sid, context, cid: Extracted fields.

extracted: Dictionary of extracted fields.

Methods:

extract_content(): Extracts key fields from content.

Reciever

Represents a receiver of content.

Constructor:
```python
Reciever(sender_id, content)

```

Parameters:

sender_id (int): ID of the sender.

content (dict): Content received.

Attributes:

sender_id, reciever_id, content

Methods:

__add__(self, other): Placeholder for combining receiver content.

Reciever_Handler

Manages multiple Reciever instances.

Attributes:

recievers: Dictionary mapping receiver IDs to Reciever instances.

Methods:

add_reciever(reciever): Adds a new receiver.

Flask Routes
POST /portal

Handles image uploads and routes them based on process field.

For "default" process, forwards image to default_process_addr.

Returns JSON with status and message.

GET /aggregate

Placeholder route for aggregating results.

POST /process_image

Processes a single image by forwarding it to the OpenCV service.

Reads image from request.

Returns JSON with status and response.

POST /cv_txt

Processes incoming text via LLM (ollama) and sends structured results to overlay via TCP socket.

Parameters:

Raw text data in request body.

Returns:

JSON with status and message.

Utility Functions
send_data_to_overlay(data, host='127.0.0.1', port=5002)

Sends string data to overlay via TCP socket.

make_prompt(txt_to_handle, prompt=default_prompt, model=default_model)

Generates a prompt to send to the LLM API.

Parameters:

txt_to_handle (str): Text to process.

prompt (str): Prompt template.

model (str): LLM model.

Returns:

LLM API response text.

Example Usage

```python
from handler import make_prompt, send_data_to_overlay

text = "Analyze this text and return structured JSON."
response = make_prompt(text)
send_data_to_overlay(response)

```

### server_cv

### ollama

already running on local just a call and a make_llm_call implemented (too much latency, error in the format)

### db

db.py
#### Description

db.py provides a Database class for interacting with a SQLite database. It includes CRUD operations for users, sessions, apps, app_contexts, and captures tables. Logging is integrated using log.py.

#### Dependencies

sqlite3

log and init_log from log.py


#### Database

Handles connection and operations on a SQLite database.

##### Constructor:

```python 
Database(db_name="app.db")
```

##### Parameters:

db_name (str): Name of the SQLite database file. Defaults to "app.db".

###### Attributes:

conn: SQLite connection object.

##### Methods:

Database Utilities

show_tables(): Returns a list of all table names in the database.

create_tables(): Creates default tables (users, sessions, apps, app_contexts, captures) if they do not exist.

get_all_items_from_table(table): Returns all rows from the specified table.

##### Users CRUD

add_user(idu, email, password): Adds a new user. Returns True if successful, False if the user already exists.

get_user(idu): Returns a user row by idu.

update_user(idu, email=None, password=None): Updates the email or password of a user.

delete_user(idu): Deletes a user by idu.

verify_user(idu, password): Returns True if the user exists with the given password.

user_exist(idu): Checks if a user exists.

##### Sessions CRUD

add_session(idu): Adds a session for the given user. Returns session ID or None if insertion fails.

get_sessions(idu=None): Returns all sessions, or sessions for a specific user.

get_session(idu=None): Returns the latest session ID.

delete_session(session_id): Deletes a session by ID.

##### Apps CRUD

add_app(name, description=None): Adds a new app. Returns app ID.

get_apps(): Returns all apps.

update_app(app_id, name=None, description=None): Updates app name and/or description.

delete_app(app_id): Deletes an app by ID.

##### App Contexts CRUD

add_app_context(app_id, key, value): Adds a new app context. Returns context ID.

get_app_contexts(app_id=None): Returns all app contexts or contexts for a specific app.

update_app_context(context_id, key=None, value=None): Updates the key or value of an app context.

delete_app_context(context_id): Deletes an app context by ID.

###### Captures CRUD

add_capture(session_id, app_id, lang=None): Adds a new capture. Returns capture ID.

get_captures(session_id=None, app_id=None): Returns captures filtered by session or app.

delete_capture(capture_id): Deletes a capture by ID.

###### Database Management

close(): Closes the database connection.

###### Example Usage

```python
from db import Database

db = Database("main.db")
db.create_tables()

# Users
db.add_user("user1", "user1@example.com", "pass123")
print(db.get_user("user1"))

# Apps
app_id = db.add_app("MyApp", "Test application")
print(db.get_apps())

# Sessions
session_id = db.add_session("user1")
print(db.get_sessions("user1"))

# Capture
capture_id = db.add_capture(session_id, app_id, "en")
print(db.get_captures(session_id=session_id))

db.close()

```


### log

log.py

#### Description

log.py provides a logging utility using the Loguru library. It allows logging messages at different levels (INFO, DEBUG, TRACE, SUCCESS, WARNING, ERROR, CRITICAL) and serializes logs into a JSONL file.

#### Dependencies

loguru

datetime

#### Variables

log_file (str): Default log file path (log.jsonl).

#### Functions

- init_log(log_file=log_file)

Initializes the logger by configuring it to write logs to a file in JSON format.

##### Parameters:

log_file (str, optional): Path to the log file. Defaults to log.jsonl.

##### Usage:

    ```python
    from log import init_log
    init_log()  # initializes with default log file
    ```


- log(method, message="", extra="")

 Logs a message at the specified level.

##### Parameters:

method (str): A single-letter code representing the log level:

"i" → INFO

"t" → TRACE

"d" → DEBUG

"s" → SUCCESS

"w" → WARNING

"e" → ERROR

"c" → CRITICAL

Any other → defaults to INFO

message (str): The message to log.

extra (str): Additional information to include (currently logged as part of the format string).

Usage:

```python
from log import log
log("i", "This is an info message")
log("e", "This is an error message", extra="user_id=123")

```

### DisplayWidget

displaywidget.py

#### Description

displaywidget.py provides a PyQt5-based GUI widget for dynamically displaying hierarchical information as a collapsible, scrollable interface. The main class DisplayInfo allows creating a resizable, draggable window to visualize nested dictionaries.

#### Dependencies

PyQt5.QtWidgets

PyQt5.QtCore

sys

#### Classes
DisplayInfo(QWidget)

Displays hierarchical information in a resizable and draggable PyQt5 widget.

##### Constructor:
```python
DisplayInfo(infos, parent=None, main=False)
```

##### Parameters:

infos (dict): Nested dictionary of information to display.

parent (QWidget, optional): Parent widget. Defaults to None.

main (bool, optional): If True, sets the widget as a main top-level window with a close button. Defaults to False.

##### Attributes:

MARGIN: Thickness of the window resize border (default: 20 pixels).

_drag_active, _drag_position, _dragging, _resizing, _resize_dir: Internal flags for drag/resizing behavior.

infos: Dictionary being displayed.

main_layout: Main layout of the widget.

##### Methods
create_info_widget(my_dict)

Recursively converts a nested dictionary into collapsible PyQt widgets.

##### Parameters:

my_dict (dict): Dictionary to convert into widgets.

##### Returns:

QWidget: Container with toggleable sections and labels.

#### generate_view(info_dict=None, main=False)

Rebuilds the displayed content from a dictionary, wrapping it in a scrollable area. Adds a close button if main=True.

##### Parameters:

info_dict (dict, optional): Dictionary to display. Defaults to self.infos.

main (bool): Indicates if the widget is a main window.

#### set_infos(infos=None)

Updates the displayed information.

##### Parameters:

infos (dict, optional): New dictionary to display.

#### _check_resize_zone(pos)

Checks if a mouse position is near the border of the widget to handle resizing.

##### Parameters:

pos (QPoint): Mouse position relative to widget.

##### Returns:

(bool, str): Tuple indicating whether resizing should occur and the resize direction.

Mouse Event Overrides

mousePressEvent(event): Handles initiating dragging or resizing.

mouseMoveEvent(event): Handles dragging, resizing, and updating the cursor.

mouseReleaseEvent(event): Ends dragging/resizing.

#### Example Usage

```python
import sys
from PyQt5.QtWidgets import QApplication
from displaywidget import DisplayInfo

app = QApplication(sys.argv)

default_infos = {
    "analyser": {
        "app": {
            "tips": {"actions": "Use ctrl+alt + key for actions."},
            "shortcuts": {"quit": "ctrl+esc"},
            "actions": {"single capture": "c", "feed capture": "f"}
        }
    }
}

win = DisplayInfo(default_infos, main=True)
win.show()
sys.exit(app.exec_())

```

## tests

## Data

## Overlay

Features

Capture active windows or user-defined regions.

Supports single capture, multiple captures, feed capture, and video capture modes.

Keyboard shortcuts and mouse actions to trigger captures.

Overlay HUD showing context, capture info, and session data.

Automatic sending of captured images to a backend handler via HTTP.

Database support for sessions and captures.

Multi-threaded worker queue for task management.

Partial and full overlay display modes.

Requirements

Python 3.10+

PyQt5

mss (for screen capturing)

pynput (for keyboard and mouse monitoring)

Pillow (for image processing)

imageio (for image I/O)

requests (for HTTP requests)

Optional: loguru, sqlite3 (for extended logging and database features)

Linux recommended (uses xdotool for active window info)

Usage

```bash
python3 overlay_test7.py
```

The program will:

Detect the active window.

Start the PyQt5 overlay with keyboard and mouse listeners.

Allow the user to trigger captures using configured shortcuts.

Keyboard Shortcuts
Action	Shortcut
Single Capture	Ctrl + Alt + C
Feed Capture	Ctrl + Alt + F
Video Capture	Ctrl + Alt + V
Stop Video Capture	Ctrl + Alt + S
Change Mode	Ctrl + Alt + M
Quit	Ctrl + Esc

Mouse Actions

Click to select capture regions.

Scroll to trigger feed captures.

Core Classes
Capture

Handles window region captures.

Saves images locally.

Computes hash of the image.

Can add captures to a Sender instance for sending to server.

Sender

Handles sending captured images to backend handlers.

Can send single or multiple captures.

Uses HTTP POST to send images and context.

Overlay

PyQt5 QWidget overlay:

Displays HUD with context and capture info.

Partial and full display modes.

Handles key and mouse events through Communicate signals.

Supports real-time updates from backend via socket server.

Context

Tracks current window, user, session, and application information.

Extracts application name from window title.

Provides JSON serialization for backend.

SocketServerThread

Background thread to receive messages from server and update overlay in real-time.

Backend Integration

Default handler endpoint: http://localhost:5000/process_image

Portal endpoint: http://localhost:5000/portal

Aggregation endpoint: http://localhost:5000/aggregate

Captured images and context are sent as multipart/form-data via HTTP POST.

Database

Built-in SQLite database (pgm.ui_util.db.Database) to store:

Users

Sessions

Captures

Automatically creates tables if missing.

Notes

Tested primarily on Linux with xdotool.

Overlay uses click-through features; transparency may be adjusted.

Multi-threaded worker queue ensures non-blocking capture and sending.

Example

```python
from overlay_test7 import get_active_window, main
window = get_active_window()
main(window, user_id="test_user")

```

### Évolution des fichiers overlay*.py

Cette partie synthétise les changements, ajouts, suppressions et fonctionnalités des fichiers `overlay*.py` jusqu’à `overlay_test5.py`.

---

#### Tableau comparatif des évolutions

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

#### État de l’art des fonctionnalités développées

##### 1. Capture d’écran
- Initialement simple capture de fenêtre via PIL/mss.
- Ajout de vérifications taille, logs et gestion erreurs.
- Passage à capture asynchrone via task queue pour non-blocage de l’UI.
- **Nouvelle étape (v7) :** encapsulation dans la classe `Capture` avec sauvegarde sur disque, conversion PIL, et calcul MD5 de l’image pour détection de doublons. Support d’un mode *feed* pour captures répétées pilotées par le scroll souris.
- Envoi JSON/en-têtes et buffer via `requests` pour traitement par un handler externe.

##### 2. Overlay
- Passage d’un simple QLabel à un overlay multi-mode (label + info_widget).
- Support plein écran, couleurs dynamiques selon mode.
- Modes : partial, passive, full.
- Gestion dynamique de contenu via DisplayInfo pour dictionnaires imbriqués.
- Intégration de QTreeWidget et QLineEdit pour sessions/captures avec filtres.
- **Nouvelle étape (v7) :** DisplayInfo (`info_widget3`) mis à jour via `add_dict_to_info` ; `Overlay` démarre un `SocketServerThread` qui permet de recevoir des informations de traitement externes et de les injecter dans l’UI.

##### 3. Événements clavier/souris
- Écoute initiale via `pynput`.
- Passage à hotkeys globaux avec séquençage (Ctrl+Alt puis touche d’action).
- `wait_for_two_clicks()` pour sélectionner une zone.
- **Nouvelle étape (v7) :** ajout du *feed capture* piloté par le scroll souris (collecte multiple + envoi conditionnel), et meilleure intégration des signaux PyQt (`update_capture`, `update_timer`).

##### 4. Communication réseau
- TCP socket server pour mises à jour texte/infos (réintroduit et utilisé en v7).
- Support JSON pour communication entre handler et socket.
- Envoi HTTP multipart (`requests.post`) pour les images avec métadonnées (`context`, `process`, `sid`, `cid`).
- Trois endpoints de travail : handler (process-image), portal (envoi individualisé) et aggregate (envoi batch/flow).

##### 5. Gestion utilisateur et sessions
- Base SQLite locale via `pgm.ui_util.db.Database` gère users, sessions, captures.
- **v7 :** `Overlay` crée automatiquement une session à l’ouverture (`db.add_session`) et récupère l’id (`get_session`) ; ce `id_session` est appliqué au `Context`.

##### 6. Architecture et modularité
- Passage progressif d’un code linéaire vers un code modulaire, clair et structuré.
- Séparation Overlay, DisplayInfo, worker thread, context.
- **v7 :** pipeline Capture → Sender → task_queue/worker clairement établi. Le socket TCP permet un canal de retour asynchrone vers l’UI. Certains points restent à uniformiser (duplication de fonctions utilitaires, prints / traces temporaires à supprimer).


### ## 7. UI / Ergonomie
- Widget plein écran, drag & drop, onglets closables.
- Treeview pour sessions et captures avec filtre dynamique.
- Styles visuels améliorés (semi-transparence, coins arrondis, couleurs).
- `FullModeApp` enrichi d’une barre de menus basique, d’une barre de recherche fonctionnelle, et d’un `QTabWidget` closable pour ouvrir des analyses depuis la treeview. 
- **v7 :** DisplayWidget en module (dragable et scrollable). Fonction escape pour afficher masquer le widget (conflit probable avec le mode (necessite verification de l'etat avant affichage !))

---


**Remarque :**  

L’architecture actuelle (version overlay_test7.py) est modulaire et intègre la capture asynchrone, la gestion utilisateur via la DB, l’overlay multi-mode, l’affichage dynamique des informations et la communication réseau (HTTP et socket TCP).Le logging et la communication réseau sont centralisés et robustes. La version 7 introduit un pipeline Capture/Sender robuste avec déduplication MD5 et un mode feed pour captures continues.
