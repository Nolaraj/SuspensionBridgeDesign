import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fancy Plotting Application")
        self.root.geometry("1000x600")

        # Use ttkbootstrap theme for a modern look
        self.style = tb.Style("darkly")

        # Create main frame with two vertical sections
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for user input
        self.input_frame = ttk.Frame(self.main_frame, width=300)
        self.input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Right frame for plot display
        self.plot_frame = ttk.Frame(self.main_frame, relief=tk.RIDGE, borderwidth=2)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # User input fields
        ttk.Label(self.input_frame, text="Select Plot Type:", font=("Arial", 12)).pack(pady=5)
        self.plot_types = ["Line", "Scatter", "Bar", "Histogram", "Pie", "Box", "Area", "Step", "Polar", "Hexbin"]
        self.plot_var = tk.StringVar(value=self.plot_types[0])
        self.plot_dropdown = ttk.Combobox(self.input_frame, textvariable=self.plot_var, values=self.plot_types,
                                          state="readonly")
        self.plot_dropdown.pack(pady=5)
        ttk.Button(self.input_frame, text="Generate Plot", command=self.update_plot).pack(pady=10)

        # Toggle Data View Button
        self.show_data = False
        self.data_button = ttk.Button(self.input_frame, text="👁 Show Data", command=self.toggle_data)
        self.data_button.pack(pady=5)

        # Navigation buttons
        self.left_button = ttk.Button(self.plot_frame, text="⬅", command=self.prev_plot)
        self.right_button = ttk.Button(self.plot_frame, text="➡", command=self.next_plot)
        self.left_button.place(relx=0.02, rely=0.5, anchor="center")
        self.right_button.place(relx=0.98, rely=0.5, anchor="center")

        self.data_label = None
        self.current_plot_index = 0
        self.create_plot()

    def create_plot(self, plot_type="Line"):
        # Clear previous plots
        for widget in self.plot_frame.winfo_children():
            if widget not in [self.left_button, self.right_button]:
                widget.destroy()

        x = np.linspace(0, 10, 500)
        y = np.sin(x) + np.random.normal(0, 0.1, 500)

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)

        if plot_type == "Line":
            ax.plot(x, y, color='cyan', linewidth=2)
            ax.set_title("Line Plot")
        elif plot_type == "Scatter":
            ax.scatter(x, y, color='magenta', alpha=0.7)
            ax.set_title("Scatter Plot")
        elif plot_type == "Bar":
            bars = np.random.rand(10) * 10
            ax.bar(range(10), bars, color='lime')
            ax.set_title("Bar Chart")
        elif plot_type == "Histogram":
            data = np.random.randn(2000)
            ax.hist(data, bins=50, color='blue', alpha=0.7)
            ax.set_title("Histogram")
        elif plot_type == "Pie":
            slices = np.random.rand(5) * 10
            ax.pie(slices, labels=["A", "B", "C", "D", "E"], autopct='%1.1f%%')
            ax.set_title("Pie Chart")
        elif plot_type == "Box":
            data = np.random.randn(200)
            ax.boxplot(data)
            ax.set_title("Box Plot")
        elif plot_type == "Area":
            ax.fill_between(x, y, color='skyblue', alpha=0.5)
            ax.set_title("Area Plot")
        elif plot_type == "Step":
            ax.step(x, y, color='orange')
            ax.set_title("Step Plot")
        elif plot_type == "Polar":
            theta = np.linspace(0, 2 * np.pi, 100)
            r = np.abs(np.sin(theta))
            ax = fig.add_subplot(111, projection='polar')
            ax.plot(theta, r, color='purple')
            ax.set_title("Polar Plot")
        elif plot_type == "Hexbin":
            x = np.random.randn(2000)
            y = np.random.randn(2000)
            ax.hexbin(x, y, gridsize=50, cmap='Blues')
            ax.set_title("Hexbin Plot")

        ax.grid(True, linestyle="--", alpha=0.5)

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_plot(self):
        plot_type = self.plot_var.get()
        self.create_plot(plot_type)

    def prev_plot(self):
        self.current_plot_index = (self.current_plot_index - 1) % len(self.plot_types)
        self.plot_var.set(self.plot_types[self.current_plot_index])
        self.create_plot(self.plot_types[self.current_plot_index])

    def next_plot(self):
        self.current_plot_index = (self.current_plot_index + 1) % len(self.plot_types)
        self.plot_var.set(self.plot_types[self.current_plot_index])
        self.create_plot(self.plot_types[self.current_plot_index])

    def toggle_data(self):
        if self.data_label:
            self.data_label.destroy()
            self.data_label = None
            self.show_data = False
            self.data_button.config(text="👁 Show Data")
        else:
            self.show_data = True
            self.data_label = ttk.Label(self.input_frame, text="Sample Data: \n" + str(np.random.randn(10)),
                                        font=("Arial", 10), wraplength=280)
            self.data_label.pack(pady=5, fill=tk.X)
            self.data_button.config(text="❌ Hide Data")


if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()
