import tkinter as tk
from tkinter import font
import time
import threading  # Import the threading module

class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master = master
        self._geom = '200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth(), master.winfo_screenheight()))

        # Create a Text widget to display RFID tags
        self.rfid_display = tk.Text(master, wrap=tk.WORD, height=10, width=40)
        self.rfid_display.grid(sticky=tk.NSEW, padx=20, pady=20)

        # Configure a default font
        myfont = font.Font(family='Helvetica', size=20, weight="bold")
        myfont2 = font.Font(family='Helvetica', size=12, weight="bold")

        # Left Frame and its contents
        leftFrame = tk.Frame(master, bg='#EDEDED')
        leftFrame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)

        # Right Frame and its contents
        rightFrame = tk.Frame(master, bg='#EDEDED')
        rightFrame.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        # Create Ready to Race circleCanvas
        self.circleCanvas = tk.Canvas(leftFrame, width=200, height=200, bg='#EDEDED')
        self.circleCanvas.grid(row=0, columnspan=2, pady=(0, 20), sticky=tk.NSEW)
        self.circleCanvas.create_oval(10, 10, 190, 190, width=0, fill='white')

        # Start the color cycling thread
        self.color_thread = threading.Thread(target=self.color_cycle)
        self.color_thread.daemon = True  # Make the thread a daemon so it exits when the main program exits
        self.color_thread.start()

        # Add Race counter
        tk.Label(leftFrame, text="Race Counter", font=myfont, bg='#EDEDED').grid(row=2, columnspan=2, pady=(0, 10), sticky=tk.NSEW)
        RCounter = tk.Text(leftFrame, width=5, height=1, takefocus=0, font=myfont2)
        RCounter.grid(row=3, columnspan=2, pady=(0, 20), sticky=tk.NSEW)

        # Fastest Racer Today
        tk.Label(leftFrame, text="Fastest Time Today", font=myfont, bg='#EDEDED').grid(row=4, columnspan=2, pady=(0, 10), sticky=tk.NSEW)

        labels = ["Lane", "Time", "Race"]
        for i, label in enumerate(labels):
            tk.Label(leftFrame, text=label, font=myfont2, bg='#EDEDED').grid(row=5, column=i, padx=5, pady=5)

        for i in range(1, 4):
            tk.Text(leftFrame, width=12, height=1, takefocus=0, font=myfont2).grid(row=6, column=i-1, padx=5, pady=5)

        # Labels on Right Frame
        tk.Label(rightFrame, text="Current Race", font=myfont, bg='#EDEDED').grid(row=0, columnspan=2, pady=(0, 10), sticky=tk.NSEW)

        RaceLog = tk.Text(rightFrame, width=30, height=10, takefocus=0)
        RaceLog.grid(row=1, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)

    def color_cycle(self):
        colors = ['red', 'yellow', 'green']
        idx = 0
        while True:
            self.circleCanvas.create_oval(10, 10, 190, 190, width=0, fill=colors[idx])
            self.master.update()
            idx = (idx + 1) % len(colors)
            time.sleep(3)

def run_gui():
    global root  # Make root a global variable
    root = tk.Tk()
    app = FullScreenApp(root)
    root.wm_title("Race Day")
    root.config(background="#FFFFFF")

    # Start the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    # Run the GUI
    run_gui()
