import tkinter as tk
from tkinter import ttk

# Create main window
root = tk.Tk()

# Create a frame that will be scrollable
frame = ttk.Frame(root)

# Create canvas to hold the frame and add vertical scrollbar
canvas = tk.Canvas(root)
canvas.pack(fill="both", expand=True, padx=10, pady=5)

# Create vertical scrollbar
v_scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
v_scrollbar.pack(side="right", fill="y")

# Configure the canvas to use the vertical scrollbar
canvas.configure(yscrollcommand=v_scrollbar.set)

# Create a frame inside the canvas
frame_inside_canvas = ttk.Frame(canvas)
canvas.create_window((0, 0), window=frame_inside_canvas, anchor="nw")

# Add widgets to the frame_inside_canvas (for demonstration)
for i in range(50):  # Adding 50 labels as an example
    label = ttk.Label(frame_inside_canvas, text=f"Label {i + 1}")
    label.grid(row=i, column=0, padx=5, pady=2)

# Update the scrollregion of the canvas to encompass the entire frame
def update_scrollregion(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

canvas.bind("<Configure>", update_scrollregion)

root.mainloop()
