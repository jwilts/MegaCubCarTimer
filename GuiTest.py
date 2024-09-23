import tkinter as tk
import random
import time

class DragRaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drag Race Tracker")
        
        self.lane_count = 2  # Default number of lanes
        self.lanes = []

        self.create_widgets()
        
    def create_widgets(self):
        self.start_button = tk.Button(self.root, text="Start Race", command=self.start_race)
        self.start_button.pack()

        self.add_lane_button = tk.Button(self.root, text="Add Lane", command=self.add_lane)
        self.add_lane_button.pack()

        self.remove_lane_button = tk.Button(self.root, text="Remove Lane", command=self.remove_lane)
        self.remove_lane_button.pack()

        self.lane_frame = tk.Frame(self.root)
        self.lane_frame.pack()

    def add_lane(self):
        if self.lane_count < 6:
            self.lane_count += 1
            self.update_lane_display()

    def remove_lane(self):
        if self.lane_count > 2:
            self.lane_count -= 1
            self.update_lane_display()

    def update_lane_display(self):
        for lane in self.lanes:
            lane.destroy()
        self.lanes = []

        for i in range(self.lane_count):
            lane_label = tk.Label(self.lane_frame, text=f"Lane {i+1}:")
            lane_label.grid(row=i, column=0)

            driver_entry = tk.Entry(self.lane_frame)
            driver_entry.grid(row=i, column=1)

            race_duration_label = tk.Label(self.lane_frame, text="Race Duration:")
            race_duration_label.grid(row=i, column=2)

            race_duration_display = tk.Label(self.lane_frame, text="00:00.00")
            race_duration_display.grid(row=i, column=3)

            self.lanes.append((lane_label, driver_entry, race_duration_display))

    def start_race(self):
        for i in range(self.lane_count):
            self.update_race_time(i)

    def update_race_time(self, lane_index):
        def update_time():
            duration = random.uniform(5, 10)  # Simulated race duration between 5 and 10 seconds
            start_time = time.time()
            while time.time() - start_time < duration:
                minutes, seconds = divmod(int(time.time() - start_time), 60)
                milliseconds = int((time.time() - start_time - int(time.time() - start_time)) * 100)
                race_time = f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
                self.lanes[lane_index][2].config(text=race_time)
                self.root.update()
            self.lanes[lane_index][2].config(text=f"{duration:.2f}")
        
        self.root.after(0, update_time)

if __name__ == '__main__':
    root = tk.Tk()
    app = DragRaceApp(root)
    root.mainloop()
