
from pynput import mouse

def listen_mouse():
    def on_move():
        pass
    def on_scroll(x,y,dx,dy,injected=False):
        print(f"Scrolled {'down' if dy<0 else 'up'} at {x},{y} for {dx},{dy} and it was {'faked' if injected else 'not faked'}")

    def on_click():
        return False

    listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll)
    listener.start()
    listener.join()
       

listen_mouse()