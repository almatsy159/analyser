# Analyser project

## objectives 

analyse various window type (mostly browser but could be applied to terminal,editor, other software)
to obtain info about the current action.

see the gpt_conv_link file to get the initial prompt

## structure of project

os tools => psutils,os,subprocess command ...
ui : mss + opencv + pytesseract ?
event : pynput

overlay : pyqt5
automated action :xdotool,pyautogui, selenium ?


## info

### state

the project has been prototyped. main.py run an overlay that recieve data from event listener (mouse and keyboard), when a window change occur a screen capture is run (need to deactivate os variable and uncomment process capture and call of this function to make it work). there is a conflict between overlay and pyqt. If cv2 run , the overlay don't and reciprocaly.

### upgrade

the open cv analysis doesn't work as expected, and the trigger of capture by changing window detection doesn't seem quite revelant.
the main should be replaced by only a function that run subprocess docker cmd . So it would allow to run and leave the environnement composed of multiple server. On for the overlay, one for open cv etc... this would allow to communicate without conflict.
Also it would be revelant that instead of taking a screen capture ,that you could select a target area manually. Then the text extraction would have less non revelant data to process, and this would also be better for privacy.
Several capture mode could be considered. saving the last area, implementing scrolll ...
Finally once the data extracted are clean this would be awesome to analyse the post itself by pormpting an llm considering the elements mentionned in the second link of gpt_conv_links

Lastly we should consider the ui part so we could see throught the text printed (alpha on overlay ?)

