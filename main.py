import tkinter as tk
from tkinter import ttk, Menu, messagebox
from ttkbootstrap import Style
from datetime import datetime
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, filedialog, scrolledtext
import threading
import SuspendedBridge_Calculations
import Basic_Scripts
import textwrap
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import xlsxwriter


class PlotManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.plots = []
        self.current_plot_index = 0

        width = max(1, self.parent_frame.winfo_width())  # Avoid division by zero
        height = max(1, self.parent_frame.winfo_height())
        figsize = (width / 100, height / 100)

        self.figure = Figure(figsize=figsize, dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.parent_frame)

        # Pack the canvas below the controls frame (dropdown, buttons)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

        self.controls_frame = tk.Frame(self.parent_frame)
        self.controls_frame.pack()

        self.prev_button = tk.Button(self.controls_frame, text="Previous", command=self.previous_plot, width=12)
        self.prev_button.pack(side=tk.LEFT, padx=10)

        self.plot_type_var = tk.StringVar()
        self.plot_dropdown = ttk.Combobox(self.controls_frame, textvariable=self.plot_type_var, state="readonly", width=12)
        self.plot_dropdown['values'] = ["Line", "Scatter", "Bar", "Pie", "Histogram", "Boxplot", "Violin", "Hexbin",
                                        "Quiver", "Contour", "Stem", "Step", "Area", "Bubble", "Sunburst", "Stream",
                                        "Error Bar", "Polar", "3D Surface", "Density"]
        self.plot_dropdown.pack(side=tk.LEFT, padx=10)
        self.plot_dropdown.bind("<<ComboboxSelected>>", self.update_plot_type)

        self.popup_button = tk.Button(self.controls_frame, text="Popup", command=self.show_popup, width=12)
        self.popup_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(self.controls_frame, text="Next", command=self.next_plot, width=12)
        self.next_button.pack(side=tk.LEFT, padx=10)



    def add_plot(self, x_data, y_data, title="Plot", xlabel="X", ylabel="Y", plot_type="Line"):
        # Add plot to the list
        self.plots.append((x_data, y_data, title, xlabel, ylabel, plot_type))

        if len(self.plots) == 1:
            # Set dropdown value to the plot type and create the plot
            self.plot_type_var.set(plot_type)
            self.draw_plot()

    def draw_plot(self, index=0):
        self.current_plot_index = index
        x, y, title, xlabel, ylabel, plot_type = self.plots[index]

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Draw the selected plot type
        if plot_type == "Line":
            ax.plot(x, y, marker='o')
        elif plot_type == "Scatter":
            ax.scatter(x, y)
        elif plot_type == "Bar":
            ax.bar(x, y)
        elif plot_type == "Pie":
            ax.pie(y, labels=x, autopct='%1.1f%%')
        elif plot_type == "Histogram":
            ax.hist(y, bins=10)
        elif plot_type == "Boxplot":
            ax.boxplot(y)
        elif plot_type == "Violin":
            ax.violinplot(y)
        elif plot_type == "Hexbin":
            ax.hexbin(x, y, gridsize=20, cmap='Blues')
        elif plot_type == "Quiver":
            U = np.cos(x)
            V = np.sin(y)
            ax.quiver(x, y, U, V)
        elif plot_type == "Contour":
            X, Y = np.meshgrid(np.linspace(min(x), max(x), 30), np.linspace(min(y), max(y), 30))
            Z = np.sin(X) * np.cos(Y)
            ax.contour(X, Y, Z)
        elif plot_type == "Stem":
            ax.stem(x, y)
        elif plot_type == "Step":
            ax.step(x, y)
        elif plot_type == "Area":
            ax.fill_between(x, y, alpha=0.4)
        elif plot_type == "Bubble":
            sizes = np.abs(y) * 100
            ax.scatter(x, y, s=sizes, alpha=0.5)
        elif plot_type == "Sunburst":
            ax.pie(y, labels=x, autopct='%1.1f%%', wedgeprops=dict(width=0.3))
        elif plot_type == "Stream":
            ax.streamplot(x, y, np.cos(x), np.sin(y))
        elif plot_type == "Error Bar":
            errors = np.random.rand(len(y)) * 0.5
            ax.errorbar(x, y, yerr=errors, fmt='o')
        elif plot_type == "Polar":
            ax = self.figure.add_subplot(111, projection='polar')
            ax.plot(x, y)
        elif plot_type == "3D Surface":
            ax = self.figure.add_subplot(111, projection='3d')
            X, Y = np.meshgrid(x, y)
            Z = np.sin(X) * np.cos(Y)
            ax.plot_surface(X, Y, Z, cmap='viridis')
        elif plot_type == "Density":
            ax.hist2d(x, y, bins=30, cmap='Blues')

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        # Redraw the canvas
        self.canvas.draw_idle()

    def previous_plot(self):
        if self.plots:
            self.current_plot_index = (self.current_plot_index - 1) % len(self.plots)
            self.draw_plot(self.current_plot_index)

    def next_plot(self):
        if self.plots:
            self.current_plot_index = (self.current_plot_index + 1) % len(self.plots)
            self.draw_plot(self.current_plot_index)

    def show_popup(self):
        if not self.plots:
            return

        popup = tk.Toplevel()
        popup.title("Plot Popup")
        popup.geometry("800x600")

        menubar = tk.Menu(popup)
        popup.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Show Data", command=lambda: self.show_data(popup))
        file_menu.add_command(label="Save Plot", command=self.save_plot)
        menubar.add_cascade(label="Options", menu=file_menu)

        figure = Figure(figsize=(8, 6), dpi=100)
        canvas = FigureCanvasTkAgg(figure, master=popup)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        ax = figure.add_subplot(111)
        x, y, title, xlabel, ylabel, plot_type = self.plots[self.current_plot_index]

        if plot_type == "Line":
            ax.plot(x, y, marker='o')
        elif plot_type == "Scatter":
            ax.scatter(x, y)
        elif plot_type == "Bar":
            ax.bar(x, y)
        elif plot_type == "Pie":
            ax.pie(y, labels=x, autopct='%1.1f%%')
        elif plot_type == "Histogram":
            ax.hist(y, bins=10)
        elif plot_type == "Boxplot":
            ax.boxplot(y)
        elif plot_type == "Violin":
            ax.violinplot(y)
        elif plot_type == "Hexbin":
            ax.hexbin(x, y, gridsize=20, cmap='Blues')
        elif plot_type == "Quiver":
            U = np.cos(x)
            V = np.sin(y)
            ax.quiver(x, y, U, V)
        elif plot_type == "Contour":
            X, Y = np.meshgrid(np.linspace(min(x), max(x), 30), np.linspace(min(y), max(y), 30))
            Z = np.sin(X) * np.cos(Y)
            ax.contour(X, Y, Z)
        elif plot_type == "Stem":
            ax.stem(x, y)
        elif plot_type == "Step":
            ax.step(x, y)
        elif plot_type == "Area":
            ax.fill_between(x, y, alpha=0.4)
        elif plot_type == "Bubble":
            sizes = np.abs(y) * 100
            ax.scatter(x, y, s=sizes, alpha=0.5)
        elif plot_type == "Sunburst":
            ax.pie(y, labels=x, autopct='%1.1f%%', wedgeprops=dict(width=0.3))
        elif plot_type == "Stream":
            ax.streamplot(x, y, np.cos(x), np.sin(y))
        elif plot_type == "Error Bar":
            errors = np.random.rand(len(y)) * 0.5
            ax.errorbar(x, y, yerr=errors, fmt='o')
        elif plot_type == "Polar":
            ax = self.figure.add_subplot(111, projection='polar')
            ax.plot(x, y)
        elif plot_type == "3D Surface":
            ax = self.figure.add_subplot(111, projection='3d')
            X, Y = np.meshgrid(x, y)
            Z = np.sin(X) * np.cos(Y)
            ax.plot_surface(X, Y, Z, cmap='viridis')
        elif plot_type == "Density":
            ax.hist2d(x, y, bins=30, cmap='Blues')

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        canvas.draw_idle()

    def show_data(self, parent):
        # data_window = tk.Toplevel(parent)
        # data_window.title("Data View")
        # data_window.geometry("400x300")
        #
        # text_area = scrolledtext.ScrolledText(data_window, wrap=tk.WORD, width=50, height=15)
        # text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        #
        # x, y, _, _, _, _ = self.plots[self.current_plot_index]
        # text_area.insert(tk.END, f"X Data: {x}\nY Data: {y}")

        def copy_all_data():
            """Copies all data from the Treeview to the clipboard."""
            data = []

            # Get all rows from the tree
            for item in tree.get_children():
                values = tree.item(item, "values")
                data.append("\t".join(map(str, values)))  # Tab-separated values

            clipboard_text = "\n".join(data)  # Each row on a new line
            data_window.clipboard_clear()
            data_window.clipboard_append(clipboard_text)
            data_window.update()  # Ensures clipboard data persists after window closes

        # Check if plots exist
        if not self.plots:
            return

        # Create data display window
        data_window = tk.Toplevel(parent)
        data_window.title("Data View")
        data_window.geometry("400x300")

        # Create tree view
        tree = ttk.Treeview(data_window, columns=("X", "Y"), show='headings')
        tree.heading("X", text="X Data")
        tree.heading("Y", text="Y Data")
        tree.pack(fill=tk.BOTH, expand=True)

        # Insert data into the tree view
        x, y, _, _, _, _ = self.plots[self.current_plot_index]
        for i in range(len(x)):
            tree.insert("", "end", values=(x[i], y[i]))

        # Add a "Copy All" button for copying the entire dataset
        copy_button = tk.Button(data_window, text="Copy All", command=copy_all_data)
        copy_button.pack(pady=5)

    def save_plot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("All Files", "*.*")])
        if file_path:
            self.figure.savefig(file_path)

    def update_plot_type(self, event):
        selected_type = self.plot_type_var.get()
        x, y, title, xlabel, ylabel, _ = self.plots[self.current_plot_index]
        self.plots[self.current_plot_index] = (x, y, title, xlabel, ylabel, selected_type)
        self.draw_plot(self.current_plot_index)


class BridgeManagementApp:
    def __init__(self, root):
        self.UnknownVartype = "Unknown variable type"
        self.NotValidVartype = "Not valid datatype"
        self.NotANumber = "NaN"
        self.texttol = 25   #Defined to scroll text on the entry if text number is greater than this on 2 colspanned window with 1 colspan enttry

        self.root = root
        self.root.title("Bridge Management System")
        self.root.geometry("1024x700")
        self.root.resizable(True, True)

        self.style = Style(theme="cosmo")
        self.root.protocol("WM_DELETE_WINDOW", self.secure_exit)

        # Initialize the main frame and log
        self.Macro_main_frame = None
        self.log_listbox = None
        self.empty_frame = None

        self.GUI_KeyValue = {}
        self.GUI_Inputs = {}
        self.Dtype_Frames = ["Survey data", "Design loads", "Adopted Values", "Sag Iteration", "Final Design", "Design Review"]
        self.DesignSpan = 0.00
        self.ElevationDifference = 0.00
        self.T_MCpermissible = 0.00
        self.T_HCpermissible = 0.00
        self.MetallicAreaC_All = 0.00
        self.MetallicAreaMC = 0.00
        self.MetallicAreaHC = 0.00
        self.bd_DeadLoad = 0.00
        self.bd_HoistingLoad = 0.00
        self.bd_FullLoad = 0.00


        self.ConstantFactor = 0.00
        self.shiftRightFound_Ele = False
        self.shiftRightFound_Ele = False
        self.Section1Sys = [
            'Survey_Distance',
            'FoundationShift_Right',
            'FoundationShift_Left',
            'MainCableEle_Right',
            'MainCableEle_Left',
            'WindguyEle_RightUp',
            'WindguyEle_LeftUp',
            'WindguyEle_RightDown',
            'WindguyEle_LeftDown', "HFL_Elevation"
        ]

        # self.RightbankEle = 0.00
        # self.LeftbankEle = 0.00


        self.create_menu()
        self.create_logger_frame()
        self.log_activity("Application started.")

    def secure_exit(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.log_activity("Application exited.")
            self.root.destroy()

    def log_activity(self, message, max_line_length = 140):
        def wrap_text(text, max_line_length):
            """Wrap text into lines of a specified maximum length."""
            words = text.split()
            lines = []
            current_line = ""

            for word in words:
                if len(current_line) + len(word) + 1 <= max_line_length:
                    current_line += (word + " ")
                else:
                    lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            return lines

        Text = wrap_text(message, max_line_length/3)
        Text1 = ' \n '.join(Text)
        print("here",Text1)
        """Appends a message with the current timestamp to the log listbox."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_only = datetime.now().strftime("%H:%M:%S")
        # Insert the timestamp and the message into the ScrolledText widget
        self.log_listbox.insert(tk.END, f"{time_only}~ {message}\n")

        # Auto-scroll to the latest entry
        self.log_listbox.yview(tk.END)

    def create_menu(self):
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        # File menu
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Import .xlsx", command=lambda: self.import_from_excel("Bridge_Design_Output.xlsx"))
        file_menu.add_command(label="Export .xlsx", command=lambda: self.export_to_excel("Bridge_Design_Output.xlsx"))
        file_menu.add_command(label="Save")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.secure_exit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Design Menu
        design_menu = Menu(menu_bar, tearoff=0)
        design_menu.add_command(label="Calculation Based", command=self.procedural_based_design)
        design_menu.add_separator()
        design_menu.add_command(label="Suspension Bridge (N_Type)", command=self.suspension_bridge_design)
        design_menu.add_command(label="Suspended Bridge (D_Type)", command=self.suspended_bridge_design)
        menu_bar.add_cascade(label="Design Aspects", menu=design_menu)

        # View menu
        view_menu = Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Change Theme", command=self.open_theme_window)
        menu_bar.add_cascade(label="View", menu=view_menu)

        # About menu
        about_menu = Menu(menu_bar, tearoff=0)
        about_menu.add_command(label="About", command=lambda: messagebox.showinfo("About",
                                                                                  "Bridge Management System v2.0 \n Developer: Prem Thapa Magar"))
        menu_bar.add_cascade(label="About", menu=about_menu)

    def create_logger_frame(self):
        title_frame = tk.Frame(self.root)
        title_frame.pack(side="left", fill="y")

        logger_frame = ttk.LabelFrame(title_frame, text="Activity Log", padding=5, style="info.TLabelframe")
        logger_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Content frame to hold listbox and empty frame
        content_frame = tk.Frame(logger_frame)
        content_frame.pack(fill="both", expand=True)

        # Configure grid layout for equal spacing
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)


        # Listbox (Left 50%)
        self.log_listbox = ScrolledText(content_frame, height=20, width=60, font=("Courier", 9))
        self.log_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.log_listbox.tag_configure("normal", font=("Courier", 9))
        self.log_listbox.tag_configure("comment", font=("Courier", 9 ,"italic"))
        self.log_listbox.tag_configure("bold_italic", font=("Courier", 9, "bold"))
        self.log_listbox.tag_configure("danger", font=("Courier", 9, "bold", "italic"), foreground="red")
        self.log_listbox.tag_configure("highlight", font=("Courier", 9, "bold", "italic"), foreground="blue")


        # Empty Frame (Right 50%)
        self.empty_frame = tk.Frame(content_frame, bg="lightgray", width=800, height=100)  # Fixed size
        self.empty_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Create Scrollbars
        h_scroll = tk.Scrollbar(self.empty_frame, orient="horizontal")
        v_scroll = tk.Scrollbar(self.empty_frame, orient="vertical")

        # Create Canvas with Fixed Dimensions
        canvas = tk.Canvas(self.empty_frame, width=self.empty_frame.winfo_width(), height=self.empty_frame.winfo_height(),
                           xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        canvas.place(x=0, y=0, width=self.empty_frame.winfo_width(), height=self.empty_frame.winfo_height())
        # Pack Scrollbars
        h_scroll.pack(side="bottom", fill="x")
        v_scroll.pack(side="right", fill="y")

        # Configure Scrollbars
        h_scroll.config(command=canvas.xview)
        v_scroll.config(command=canvas.yview)

        # Prevent resizing of canvas beyond original frame size
        def adjust_canvas_size(event):
            canvas.config(width=self.empty_frame.winfo_width(), height=self.empty_frame.winfo_height())

        self.empty_frame.bind("<Configure>", adjust_canvas_size)  # Keeps canvas fixed to frame size

    def calculate_line_capacity(self, text_widget):
        widget_width_chars = text_widget.cget("width")  # Get width in characters
        widget_font = tk.font.Font(font=text_widget.cget("font"))  # Get font details

        # Measure the average width of a character in pixels
        char_width = widget_font.measure("X")  # Width of a single character in pixels
        widget_pixel_width = text_widget.winfo_width()  # Get actual pixel width of widget

        # Calculate how many characters fit in one line
        if char_width > 0:
            chars_per_line = widget_pixel_width // char_width
        else:
            chars_per_line = widget_width_chars  # Fallback if measure fails

        # print(f"Character width: {char_width} pixels")
        # print(f"ScrolledText widget width: {widget_pixel_width} pixels")
        # print(f"Approx. characters per line: {chars_per_line}")
        return chars_per_line
    def insert_dict_into_table(self, dictionary, centralgap = 2, highlight='normal'):
        """Inserts the dictionary values into the ScrolledText widget in a table format."""
        chars_per_line = self.calculate_line_capacity( self.log_listbox)
        dashes_per_line = chars_per_line - 2

        # Clear the ScrolledText widget
        textspan = int(chars_per_line/2) -2
        # Insert headers
        gap0 = textspan - 3 + 2
        gap00 = 2*textspan
        self.log_listbox.insert("end", f'Key{" "*gap0}Value\n')
        self.log_listbox.insert("end", "-" * dashes_per_line + "\n")  # Separator line


        # Insert each key-value pair
        for key, value in dictionary.items():
            wrapped_value_linesKEY = self.wrap_text(str(key), textspan)
            wrapped_value_linesValue = self.wrap_text(str(value), textspan)

            lenKey, lenValue = len(wrapped_value_linesKEY), len(wrapped_value_linesValue)
            if lenKey > lenValue:
                wrapped_value_linesValue.extend([" "] * (lenKey - lenValue))
            elif lenValue > lenKey:
                wrapped_value_linesKEY.extend([" "] * (lenValue - lenKey))

            lines = []
            for index, (value1, value2) in enumerate(zip(wrapped_value_linesKEY, wrapped_value_linesValue)):
                lenV1 = len(value1)
                lenV2 = len(value2)
                gap1 = textspan - lenV1 + centralgap
                gap2 = chars_per_line -lenV1 - lenV2 - gap1
                if gap2 >2:
                    gap2 = gap2 -2

                line = f'{value1}{" "*gap1}{value2}{" "*gap2}'
                lines.append(line)
            lines = "\n".join(lines)

            self.log_listbox.insert(tk.END, lines , highlight)
            # for line in lines:
            #     if highlight:
            #         self.log_listbox.tag_configure("highlight", font=("Courier", 10, "bold"))
            #         self.log_listbox.insert("end", line)
            #     else:
            #         self.log_listbox.insert("end", line)



        # Auto-scroll to the latest entry
        self.log_listbox.yview(tk.END)
        self.log_listbox.insert("end", "\n\n")













        #
        #
        #

    def wrap_text(self, text, width=40):
        """Wraps text to fit within a specified width."""
        text = str(text)  # Ensure the input is a string
        words = text.split()
        wrapped_lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                current_line += word + " "
            else:
                wrapped_lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            wrapped_lines.append(current_line.strip())

        return wrapped_lines
    def open_theme_window(self):
        theme_window = tk.Toplevel(self.root)
        theme_window.title("Change Theme")
        theme_window.geometry("300x150")

        theme_label = ttk.Label(theme_window, text="Select Theme:", font=("Helvetica", 12))
        theme_label.pack(pady=10)

        theme_var = tk.StringVar()
        theme_dropdown = ttk.Combobox(
            theme_window,
            textvariable=theme_var,
            values=self.style.theme_names(),
            state="readonly",
            font=("Helvetica", 12)
        )
        theme_dropdown.pack(pady=5)
        theme_dropdown.current(0)

        apply_button = ttk.Button(
            theme_window,
            text="Apply Theme",
            style="info.TButton",
            command=lambda: self.change_theme(theme_var.get())
        )
        apply_button.pack(pady=10)

    def change_theme(self, theme_name):
        self.style.theme_use(theme_name)
        self.log_activity(f"Theme changed to {theme_name}.")

    def destroy_and_create_frame(self):
        """Destroys the existing Macro_main_frame (if it exists) and recreates it."""
        if self.Macro_main_frame is not None:
            self.Macro_main_frame.destroy()

        self.Macro_main_frame = ttk.Frame(self.root, padding=0)
        self.Macro_main_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def ScrollableFrameUnderFrame(self, ParentFrame):
        # Empty Frame (Right 50%)
        frame_inside_canvas = tk.Frame(ParentFrame, bg="lightgray")  # Fixed size
        frame_inside_canvas.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Create Scrollbars
        h_scroll = tk.Scrollbar(frame_inside_canvas, orient="horizontal")
        v_scroll = tk.Scrollbar(frame_inside_canvas, orient="vertical")

        # Create Canvas with Fixed Dimensions
        canvas = tk.Canvas(frame_inside_canvas, width=frame_inside_canvas.winfo_width(), height=frame_inside_canvas.winfo_height(),
                           xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        canvas.place(x=0, y=0, width=frame_inside_canvas.winfo_width(), height=frame_inside_canvas.winfo_height())

        # Pack Scrollbars
        h_scroll.pack(side="bottom", fill="x")
        v_scroll.pack(side="right", fill="y")

        # Configure Scrollbars
        h_scroll.config(command=canvas.xview)
        v_scroll.config(command=canvas.yview)

        main_frame = ttk.Frame(canvas)

        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        # Prevent resizing of canvas beyond original frame size
        def adjust_canvas_size(event):
            canvas.config(width=frame_inside_canvas.winfo_width(), height=frame_inside_canvas.winfo_height())

        frame_inside_canvas.bind("<Configure>", adjust_canvas_size)  # Keeps canvas fixed to frame size
        label = ttk.Label(frame_inside_canvas, text="Hello there ", font=("Times New Roman", 10))
        label.pack(side="right", fill="y")

        return frame_inside_canvas

    def frame_Creator(self, ParentFrame, Child1Title, Child2Titles, vertical = False):


            FrameObjects = []

            Child1Obj = ttk.LabelFrame(ParentFrame, text=Child1Title, padding=10, style="primary.TLabelframe")

            Child1Obj.pack(fill="both", expand=True, padx=5, pady=0)  # Using pack to fill entire space

            # for index, value in enumerate(Child2Titles):
            #     Cables_frame = ttk.LabelFrame(Child1Obj, text=value, padding=10,
            #                                   style="success.TLabelframe")
            #     Cables_frame.grid(row=0, column=index, padx=5, pady=0, sticky="nsew")
            #     FrameObjects.append(Cables_frame)
            #

            #
            #
            if vertical:
                for index, value in enumerate(Child2Titles):
                    Cables_frame = ttk.LabelFrame(Child1Obj, text=value, padding=10,
                                                  style="success.TLabelframe")
                    Cables_frame.grid(row=index, column=0, padx=5, pady=0, sticky="nsew")
                    FrameObjects.append(Cables_frame)

                # for index, value in enumerate(FrameObjects):
                #         value.columnconfigure(0, weight=1)

                #


                #Only handle the following for scrollbar error no ther required
                # FrameObjects[0].columnconfigure(1, weight=1)  # Input Frame
                # FrameObjects[1].columnconfigure(1, weight=1)  # Input Frame




            else:
                for index, value in enumerate(Child2Titles):
                    Cables_frame = ttk.LabelFrame(Child1Obj, text=value, padding=10,
                                                  style="success.TLabelframe")
                    Cables_frame.grid(row=0, column=index, padx=5, pady=0, sticky="nsew")
                    FrameObjects.append(Cables_frame)


                for index, value in enumerate(FrameObjects):
                    value.columnconfigure(1, weight=1)


            for index, value in enumerate(FrameObjects):
                Child1Obj.columnconfigure(index, weight=1)  # Input Frame

            for index, value in enumerate(FrameObjects):
                value.columnconfigure(1, weight=1)

            Child1Obj.columnconfigure(0, weight=1)
            Child1Obj.columnconfigure(1, weight=1)

            Child1Obj.rowconfigure(1, weight=0)


            # entry = ttk.Entry(value, font=("Times New Roman", 10), bootstyle="info")
                # entry.grid(row=index, column=1, padx=0, pady=0, sticky="ew")

            # # for index, value in enumerate(FrameObjects):
            # FrameObjects[0].columnconfigure(0, weight=1)  # Input Frame
            # FrameObjects[0].columnconfigure(1, weight=1)  # Input Frame
            # FrameObjects[1].columnconfigure(0, weight=1)  # Input Frame
            # FrameObjects[1].columnconfigure(1, weight=1)  # Input Frame

            return Child1Obj, FrameObjects

    def create_labels_and_entries(self, frame, labels, remarks,columnspan, var_types, widgets, Information = ""):
            entries = []

            # Entry box clearing function
            def on_entry_click(event, entry):
                """Clears the default text when the user clicks inside the entry box."""
                entry.get()
                entry.delete(0, tk.END)
                entry.config(foreground="black")

            # Function to check if the last entry is filled and print data
            def on_last_entry_fill(event, entries, callback):
                if entries[-1].get().strip():  # Check if the last entry is filled
                    data = {label: entry.get() for label, entry in zip(labels, entries)}
                    outputdata = []
                    Text = ""
                    for key, value in data.items():
                        Text += f"{key}: {value}"
                        outputdata.append(f"{key}: {value}")
                    self.insert_dict_into_table(data)
                    self.log_activity(Text, int(self.log_listbox.winfo_width()/5))
                    # text=wrap_text(Text, int(self.log_listbox.winfo_width()/5) )
                    # for value in text:
                    #     self.log_activity(value)


                    callback(data)  # Call the callback function

            # Create a title label
            dynrow = 0
            if not Information == "":
                # self.log_listbox = ScrolledText(content_frame, height=10, width=10, font=("Times New Roman", 8))
                # self.log_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
                    text_area = ScrolledText(frame, height=3, font=("Times New Roman", 9, "bold", "italic"))
                    text_area.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
                    text_area.insert(tk.END, Information)

                    # Auto-scroll to the latest entry
                    text_area.yview(tk.END)
                    dynrow = dynrow + 1

            def validate_numeric_input(event, var_type, entry_var, entry_widget):
                """Validate numeric input only when focus is lost."""
                try:
                    value = entry_var.get()  # Get the current value

                    if var_type == "int":
                        int(value)  # Try converting to int
                    elif var_type == "float":
                        float(value)  # Try converting to float
                    else:
                        raise ValueError(self.UnknownVartype)

                except (ValueError, tk.TclError):
                    entry_widget.delete(0, tk.END)  # Clear the invalid input
                    entry_widget.insert(0, self.NotValidVartype)  # Reset to default value

            def on_data_submit(data):
                """Handle submitted data."""
                print("Submitted Data:", data)

            def scroll_remark(entry, speed=150, texttol = 25):
                """Automatically scrolls the text in an entry widget."""
                text = entry.get()

                def scroll():
                    while True:
                        text_var = entry.get()
                        if len(text_var) > texttol:  # Only scroll if text is long enough
                            text_var = text_var[1:] + text_var[0]  # Shift left
                            entry.delete(0, "end")
                            entry.insert(0, text_var)
                        entry.update_idletasks()
                        entry.after(speed, scroll)  # Recursive call with delay
                        break  # Prevent infinite recursion in tkinter

                threading.Thread(target=scroll, daemon=True).start()  # Run in background
            for i, (text, remark, colspan,  var_type, widget_type) in enumerate(zip(labels, remarks,columnspan,  var_types, widgets)):
                if var_type == "int":
                    var = tk.IntVar(value="")
                elif var_type == "float":
                    var = tk.DoubleVar(value="")
                elif var_type == "string":
                    var = tk.StringVar(value="")
                elif var_type == "boolean":
                    var = tk.BooleanVar(value=True)
                else:
                    raise ValueError("Invalid variable type specified. Use 'int' or 'string'.")
                if colspan == 2:
                    if widget_type == "entry":

                        entry = ttk.Entry(frame, textvariable=var, font=("Times New Roman", 9, "italic"),
                                          bootstyle="info")
                        entry.grid(row=i + dynrow, column=0, columnspan=colspan, padx=0, pady=0, sticky="ew")
                        if not remark == "":
                            entry.insert(0, remark)
                            entry.original_text = remark
                            scroll_remark(entry, speed=200, texttol=35)
                        entries.append(entry)

                        # Bind the last entry to trigger data printing and callback
                        entry.bind("<FocusIn>", lambda event, e=entry: on_entry_click(event, e))

                        # Apply numeric validation only on focus out
                        if var_type in ["int", "float"]:
                            entry.bind("<FocusOut>",
                                       lambda event, v=var, w=entry, t=var_type: validate_numeric_input(event, t, v, w))

                        # if i == len(labels) - 1:
                        #     entry.bind("<FocusOut>",
                        #                lambda event, e=entries, c=on_data_submit: on_last_entry_fill(event, e, c))

                    elif widget_type == "dropdown":

                        options = remark  # Example dropdown options
                        var = tk.StringVar()

                        dropdown = ttk.Combobox(frame, textvariable=var, values=options, font=("Times New Roman", 10))
                        dropdown.grid(row=i + dynrow, column=0, columnspan=colspan, padx=0, pady=0, sticky="ew")

                        # Set the default value explicitly to the first option
                        var.set(options[0])

                        entries.append(dropdown)  # Store the dropdown variable

                    elif widget_type == "button":

                        button = ttk.Button(frame, text=text)#, command=lambda t=text: self.on_button_click(t))
                        button.grid(row=i + dynrow, column=0, columnspan=colspan, padx=5, pady=10, sticky="ew")
                        entries.append(button)  # No entry to store for buttons
                    elif widget_type == "radio":
                        radio1 = ttk.Radiobutton(self.frame, text="Option 1", variable=self.radio_value, value="1")
                        radio2 = ttk.Radiobutton(self.frame, text="Option 2", variable=self.radio_value, value="2")


                else:

                    if widget_type == "entry":
                        label = ttk.Label(frame, text=text, font=("Times New Roman", 10))
                        label.grid(row=i + dynrow, column=0, padx=10, pady=0, sticky="w")

                        entry = ttk.Entry(frame, textvariable=var, font=("Times New Roman", 9, "italic"),
                                          bootstyle="info")
                        entry.grid(row=i + dynrow, column=1, padx=0, pady=0, sticky="ew")
                        if not remark == "":
                            entry.insert(0, remark)
                            entry.original_text = remark
                            scroll_remark(entry, speed=200, texttol=35)
                        entries.append(entry)

                        # Bind the last entry to trigger data printing and callback
                        entry.bind("<FocusIn>", lambda event, e=entry: on_entry_click(event, e))

                        # Apply numeric validation only on focus out
                        if var_type in ["int", "float"]:
                            entry.bind("<FocusOut>",
                                       lambda event, v=var, w=entry, t=var_type: validate_numeric_input(event, t, v, w))

                        # if i == len(labels) - 1:
                        #     entry.bind("<FocusOut>",
                        #                lambda event, e=entries, c=on_data_submit: on_last_entry_fill(event, e, c))

                    elif widget_type == "dropdown":
                        label = ttk.Label(frame, text=text, font=("Times New Roman", 10))
                        label.grid(row=i + dynrow, column=0, padx=10, pady=0, sticky="w")

                        options = remark  # Example dropdown options
                        var = tk.StringVar()

                        dropdown = ttk.Combobox(frame, textvariable=var, values=options, font=("Times New Roman", 10))
                        dropdown.grid(row=i + dynrow, column=1, padx=0, pady=0, sticky="ew")

                        frame.after(100, lambda: dropdown.set(options[0]))
                        entries.append(dropdown)  # Store the dropdown variable

                    elif widget_type == "button":
                        button = ttk.Button(frame, text=text)
                        button.grid(row=i + dynrow, column=1, padx=0, pady=0, sticky="ew")
                        entries.append(button)  # No entry to store for buttons
                    elif widget_type == "radio":
                        radio1 = ttk.Radiobutton(self.frame, text="Option 1", variable=self.radio_value, value="1")
                        radio2 = ttk.Radiobutton(self.frame, text="Option 2", variable=self.radio_value, value="2")

                    else:
                        raise ValueError("Invalid widget type specified. Use 'entry', 'dropdown', or 'button'.")


            return entries
    def on_button_click(self, button_text):
            messagebox.showinfo("Button Clicked", f"You clicked: {button_text}")

    def floatdatatype_check(self,value):
        Valid = True
        try:
            value = float(value)
            if value in ["", self.NotValidVartype, self.UnknownVartype]:
                Valid = False
            return Valid
        except:
            return False


    def export_to_excel(self, filename="Bridge_Design_Output.xlsx"):

            print(self.GUI_KeyValue.items())
            try:
                # List to store data in structured format
                export_data = []

                # Loop through each section in GUI_KeyValue
                for section, data_dict in self.GUI_KeyValue.items():
                    for label, widget in data_dict.items():
                        try:
                            value = "N/A"  # Default value if extraction fails

                            if isinstance(widget, (tk.Entry, ttk.Combobox)):  # Text entries and Dropdowns
                                value = widget.get().strip() if widget.get() else "N/A"
                            elif isinstance(widget, tk.Text):  # Multi-line text
                                value = widget.get("1.0", tk.END).strip() if widget.get("1.0",
                                                                                        tk.END).strip() else "N/A"
                            elif isinstance(widget, ttk.Checkbutton):  # Checkbuttons
                                value = widget.variable.get() if hasattr(widget, 'variable') else "Unchecked"
                            elif isinstance(widget, ttk.Button):  # Buttons
                                value = "Button (Action)"
                            elif isinstance(widget, ttk.Label):  # Labels
                                value = widget.cget("text") if widget.cget("text") else "N/A"
                            else:
                                value = "Unsupported Widget"

                            # Append extracted data to list
                            export_data.append([section, label, value])
                        except Exception as e:
                            messagebox.showerror("Export Error", f"Error processing {label}: {e}")

                # Convert to DataFrame with columns
                df = pd.DataFrame(export_data, columns=["Section", "Label", "Value"])

                # Write to Excel
                with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
                    df.to_excel(writer, sheet_name="Design Output", index=False)

                messagebox.showinfo("Export Successful", f"Data successfully exported to {filename}")

            except Exception as e:
                messagebox.showerror("Export Error", f"An error occurred: {str(e)}")

    def import_from_excel(self, filename="Bridge_Design_Output.xlsx"):
        try:
            # Read Excel file
            df = pd.read_excel(filename, sheet_name="Design Output")

            # Loop through the DataFrame and update GUI widgets
            for _, row in df.iterrows():
                section, label, value = row["Section"], row["Label"], row["Value"]

                if section in self.GUI_KeyValue and label in self.GUI_KeyValue[section]:
                    widget = self.GUI_KeyValue[section][label]

                    try:
                        if isinstance(widget, (tk.Entry, ttk.Combobox)):
                            widget.delete(0, tk.END)
                            widget.insert(0, value)
                        elif isinstance(widget, tk.Text):
                            widget.delete("1.0", tk.END)
                            widget.insert("1.0", value)
                        elif isinstance(widget, ttk.Checkbutton):
                            if hasattr(widget, 'variable'):
                                widget.variable.set(value == "True")
                        elif isinstance(widget, ttk.Label):
                            widget.config(text=value)
                    except Exception as e:
                        messagebox.showerror("Import Error", f"Error processing {label}: {e}")

            messagebox.showinfo("Import Successful", f"Data successfully imported from {filename}")

        except Exception as e:
            messagebox.showerror("Import Error", f"An error occurred: {str(e)}")

    def set_widget_value(self, widget, value):
        """
        Function to set the value of a given widget.

        Parameters:
        - widget (tk.Widget or ttk.Widget): The widget object to be updated.
        - value (varied): The value to set for the widget.
        """
        try:
            if isinstance(widget, tk.Entry):  # If it's an Entry widget
                widget.delete(0, tk.END)  # Clear the current content
                widget.insert(0, value)  # Insert the new value

            elif isinstance(widget, tk.Text):  # If it's a Text widget
                widget.delete("1.0", tk.END)  # Clear content
                widget.insert("1.0", value)  # Insert new value

            elif isinstance(widget, tk.Radiobutton):  # If it's a Radiobutton
                # Assuming value is True/False to simulate selection/deselection
                if value:  # Simulate clicking the radiobutton
                    widget.invoke()

            elif isinstance(widget, (tk.Button, ttk.Button)):  # If it's a Button
                widget.config(text=value)  # Set button text

            elif isinstance(widget, tk.Checkbutton):  # If it's a Checkbutton
                if value:  # If value is True, check it; False will uncheck it
                    widget.select()
                else:
                    widget.deselect()

            elif isinstance(widget, ttk.Combobox):  # If it's a Combobox
                widget.set(value)  # Set the selected value

            elif isinstance(widget, tk.StringVar):  # If it's a StringVar
                widget.set(value)  # Set the variable value

        except Exception as e:
            print(f"Error setting value for widget: {e}")
    def procedural_based_design(self):
        self.destroy_and_create_frame()
        self.log_activity("Running on procedural based design.")

        #Initialize D type calculations
        D_Type = SuspendedBridge_Calculations.SuspendedBridge
        bridge_instance = D_Type()

        # Initialize plot manager if not already created
        # Initialize plot manager if not already created
        if not hasattr(self, 'plot_manager'):
            self.plot_manager = PlotManager(self.empty_frame)


        def Section1(event, LabelEntry, remarks, input_var_types):

            for index, (key, value) in enumerate(LabelEntry.items()):
                try:
                    if isinstance(value, tk.Radiobutton):  # Check if it's a Radiobutton
                        entry_value = value.cget()  # This gets the value associated with the radiobutton
                    elif isinstance(value, (tk.Button, ttk.Button)):  # Check if it's a Button
                        entry_value = value.cget("text")  # Retrieve the text displayed on the button
                    else:
                        entry_value = value.get().strip()  # Get text from Entry widgets
                except:
                    pass

                input_var_type = input_var_types[index]
                try:
                    if input_var_type == "int":
                        entry_value = int(entry_value)
                    elif input_var_type == "float":
                        entry_value = float(entry_value)
                    elif input_var_type == "boolean":
                        entry_value = bool(entry_value)
                except:
                    pass
                try:
                    original_remark = remarks[index].strip()  # Get original remark from list
                except:
                    original_remark = ""
                stored_remark = getattr(value, "original_text", "").strip()  # Get stored original remark


                # Check if the entry is empty or an invalid value

                # def sort_letters(word: str) -> str:
                #     return ''.join(sorted(word.lower()))
                # orderedRemark = sort_letters(original_remark)
                # orderedValue = sort_letters(entry_value)
                # value = False
                # if orderedValue == orderedRemark:
                #     value = True
                # print(orderedValue, orderedRemark, value)

                if entry_value in ["", self.UnknownVartype, self.NotValidVartype, self.NotANumber]:
                    """#Back feeding the adopted values from another modules to the entries"""
                    self.set_widget_value(value, getattr(bridge_instance, self.Section1Sys[index]))

                elif entry_value == original_remark or entry_value == stored_remark:
                    continue

                # elif orderedRemark == orderedValue:
                #     continue

                else:

                    if isinstance(remarks[index], list):
                        print("I am in drum")
                        if value.get() == "Drum Type":
                            bridge_instance.CableAnchorage_DrumType = True
                            bridge_instance.CableAnchorage_OpenType = False
                        if value.get() == "Open Type":
                            bridge_instance.CableAnchorage_DrumType= False
                            bridge_instance.CableAnchorage_OpenType= True
                    elif isinstance(value, (tk.Button, ttk.Button)):
                        pass
                    else:

                        # Section1Sys[index] = entry_value
                        setattr(bridge_instance, self.Section1Sys[index], entry_value)  # Dynamically set the value












            """Checking whether the data entered is the same or default"""
            for i, value in enumerate(self.Section1Sys):
                print("Final after writinhg", self.Section1Sys[i], getattr(bridge_instance, self.Section1Sys[i]))


            DesignSpan, LowestPoint_Check, hTolerance, ElevationDifference = bridge_instance.SpanHeight_Calculations()

            self.DesignSpan = float(DesignSpan)
            self.ElevationDifference = float(ElevationDifference)
            chars_per_line = self.calculate_line_capacity(self.log_listbox)
            dashes_per_line = chars_per_line - 2
            self.log_listbox.tag_configure("bold_italic", font=("Courier", 8, "bold", "italic"))
            self.log_listbox.insert("end", "=" * dashes_per_line + "\n", "bold_italic")  # Separator line

            data = {"Design Span": DesignSpan, "Elevation Difference L/R": ElevationDifference, "Span / 14" :hTolerance , "(Span / 14) > Elevation Difference L/R": LowestPoint_Check}
            if not LowestPoint_Check:
                LowestPoint_Check = "danger"
            self.insert_dict_into_table(data, highlight= LowestPoint_Check)

            Tmax_Approx, MCHC_Approx, MetallicAreaC_All, MCHCLoad_Dead , MetallicAreaMC_All,MetallicAreaHC_All = bridge_instance.preCalculation_TMCHC(DesignSpan, Basic_Scripts.ExcelTable_extractor(Basic_Scripts.StandardExcel_Path, Basic_Scripts.Sheetname1, Basic_Scripts.TableName1)[0])
            data = {"Approximate maximum cable tension": Tmax_Approx, "Metallic area provided": MetallicAreaC_All, "Cables dead load, kN/m": MCHCLoad_Dead}
            self.MetallicAreaC_All = MetallicAreaC_All
            self.MetallicAreaMC = MetallicAreaMC_All
            self.MetallicAreaHC = MetallicAreaHC_All
            self.insert_dict_into_table(data)
            self.insert_dict_into_table(MCHC_Approx)
            self.T_MCpermissible = Basic_Scripts.dictValuefromTitlekey(MCHC_Approx, "Tpermissible")

            WindGuy_Dia, Twindguy_LR, Tpermissible, Windguyload_percable = bridge_instance.WindGuy_Approximation(DesignSpan)
            totalwindguyLoad = Windguyload_percable *2
            data = {"Windguy No": 2, "Windguy diameter": WindGuy_Dia, "Approximate windguy tension (L/R)": Twindguy_LR, "Permissible cable tension": Tpermissible, "Windguy Load": totalwindguyLoad}
            self.insert_dict_into_table(data)
            self.T_HCpermissible = float(Tpermissible)

            #Updating of Hoisting load value which lies in index 1
            self.GUI_Inputs[Frame2Title][1].delete(0, tk.END)
            self.GUI_Inputs[Frame2Title][1].insert(0, float(MCHCLoad_Dead))
            self.GUI_Inputs[Frame2Title][6].delete(0, tk.END)
            self.GUI_Inputs[Frame2Title][6].insert(0, float(totalwindguyLoad))
        def LoadsAutoUpdate(event, tension_entries):
            def validate_and_sum_tension_entries(tension_entries):
                # """
                # Checks if all entries (except 'Full load') are filled.
                # If so, sums them up and sets the sum in the 'Full load' entry.
                # Updates dynamically when any entry is changed.
                # """
                dead_sum = 0.00
                total_sum = 0.00
                all_filled = True  # Flag to check if all values are filled

                for i, entry in enumerate(tension_entries[1:8]):  # Exclude last entry (Full load)
                    try:
                        value = entry.get().strip()  # Get the value
                    except:
                        value = entry.get()

                    if value in ["", self.NotValidVartype, self.UnknownVartype]:  # Check if empty
                        all_filled = False
                        break  # Stop checking further

                    try:
                        dead_sum += float(value)  # Convert to float and sum
                    except ValueError:  # Handle invalid inputs
                        all_filled = False
                        break

                        # If all values are filled, update "Full load" entry

                if all_filled:
                    tension_entries[8].delete(0, "end")  # Clear previous value
                    tension_entries[8].insert(0, float(round(dead_sum, 3)))  # Insert sum (rounded)

                    LiveLoad = 3 + float(50 / self.DesignSpan )
                    tension_entries[9].delete(0, "end")  # Clear previous value
                    tension_entries[9].insert(0, float(LiveLoad))  # Insert sum (rounded)

                    total_sum = dead_sum + float(tension_entries[9].get())

                    tension_entries[10].delete(0, "end")  # Clear previous value
                    tension_entries[10].insert(0, float(total_sum))  # Insert sum (rounded)


                if not all_filled:
                    tension_entries[8].delete(0, "end")  # Clear previous value

                    tension_entries[10].delete(0, "end")  # Clear previous value

            def bind_tension_entries(tension_entries):
                """
                Binds all entries (except 'Full load') to trigger sum calculation on modification.
                """
                for entry in tension_entries[:-1]:  # Exclude "Full load"
                    entry.bind("<FocusOut>", lambda event: validate_and_sum_tension_entries(tension_entries))
                    entry.bind("<KeyRelease>", lambda event: validate_and_sum_tension_entries(tension_entries))

                    # # tension_entries[-1].bind("<FocusOut>", self.on_last_entry_filled)

            validate_and_sum_tension_entries(tension_entries)
            bind_tension_entries(tension_entries)
        def LoadSubmit(event, tension_entries):
            beta1fmax, beta1fmin, gf, bdmax, bdmin,Tbfmax, Tbfmin, ElevationDifference, DesignSpan, gf,            Tpermissible, bfminCheck, bfmaxCheck, TpermCheck2, TpermCheck1 =                 bridge_instance.Dead_Load_Design(self.DesignSpan, self.ElevationDifference, self.T_MCpermissible,
                                                 LiveLoad=float(tension_entries[9].get()), HoistingLoad=float(tension_entries[1].get()), DeadLoad=float(tension_entries[8].get()) , FullLoad = float(tension_entries[10].get()))

            data = {"Permissible cable tension": Tpermissible, "Dead load sag, bdmax": bdmax,"β1fmax": beta1fmax,
                    "T1fmax": Tbfmax,"Tβ1fmaxCheck (Tperm > Tbfmax)": bfmaxCheck, "Dead load sag, bdmin": bdmin,"β1fmin": beta1fmin,
                    "Tbfmin": Tbfmin,"Tβ1fminCheck (Tperm > Tbfmin)": bfminCheck }

            highlight = "normal"
            if not all([bfmaxCheck, bfminCheck, TpermCheck1, TpermCheck2]):
                highlight = "danger"

            self.insert_dict_into_table(data, highlight=highlight)

            # Compute corresponding y values
            # Generate `bf` values from bdmin to bdmax
            bf_values = np.linspace(bdmin * 1.22, bdmax * 1.22, 100)

            # Calculate beta1fmax and Tmax for each `bf`
            beta1fmax_values = []
            Tmax_values = []

            for bf in bf_values:
                beta1fmax, Tmax = bridge_instance.beta_Tmax(bf, ElevationDifference, DesignSpan, gf)
                beta1fmax_values.append(beta1fmax)
                Tmax_values.append(Tmax)
        def Deadloadsag_range():
            if self.floatdatatype_check(self.GUI_Inputs[self.Dtype_Frames[2]][0].get()):
                self.ElevationDifference = float(self.GUI_Inputs[self.Dtype_Frames[2]][0].get())
                bdmax, bdmin = bridge_instance.bdmax_bdmin(self.DesignSpan, self.ElevationDifference)
                data = {"For elevation difference of": self.ElevationDifference, "Bdmax value (m)": bdmax, "Bdmin value (m)": bdmin}
                self.insert_dict_into_table(data)
        def Processing1(event, adopted_entries):
            self.ElevationDifference = float(adopted_entries[0].get())
            if adopted_entries[2].get() == "Left foundation":
                self.shiftRightFound_Ele = False
                self.shiftLeftFound_Ele = True
            else:
                self.shiftRightFound_Ele = True
                self.shiftLeftFound_Ele = False

            EleRight = getattr(bridge_instance, self.Section1Sys[self.Section1Sys.index('MainCableEle_Right')])
            EleLeft = getattr(bridge_instance, self.Section1Sys[self.Section1Sys.index('MainCableEle_Left')])

            if self.shiftRightFound_Ele:
                if EleRight > EleLeft:
                    EleRight = EleLeft + self.ElevationDifference
                else:
                    EleRight = EleLeft - self.ElevationDifference
            if self.shiftLeftFound_Ele:
                if EleRight < EleLeft:
                    EleLeft = EleRight + self.ElevationDifference
                else:
                    EleLeft = EleRight - self.ElevationDifference
            setattr(bridge_instance, self.Section1Sys[self.Section1Sys.index('MainCableEle_Right')], EleRight)
            setattr(bridge_instance, self.Section1Sys[self.Section1Sys.index('MainCableEle_Left')], EleLeft)
            TotalLoad =         float(self.GUI_Inputs[self.Dtype_Frames[1]][10].get())
            bd =  float(self.GUI_Inputs[self.Dtype_Frames[2]][1].get())
            TensionValue = bridge_instance.TensionCalc(TotalLoad, self.DesignSpan, bd, self.ElevationDifference)


            beta_1d = bridge_instance.betaCalc(bd,  self.ElevationDifference, self.DesignSpan)
            beta_2d = bridge_instance.betaCalc(bd,  -self.ElevationDifference, self.DesignSpan)

            Parabola_ed = bridge_instance.ed_Distance( self.DesignSpan, self.ElevationDifference, bd)
            Parabola_fd = bridge_instance.foundationSag(bd, self.ElevationDifference)

            max_elevation = max(EleRight, EleLeft)
            maincable_freeboard = max_elevation- Parabola_fd - getattr(bridge_instance, self.Section1Sys[self.Section1Sys.index('HFL_Elevation')])
            windguy_elevations = [getattr(bridge_instance, self.Section1Sys[self.Section1Sys.index('WindguyEle_RightUp')]),
                                  getattr(bridge_instance, self.Section1Sys[self.Section1Sys.index('WindguyEle_RightDown')]),
                                  getattr(bridge_instance, self.Section1Sys[self.Section1Sys.index('WindguyEle_LeftUp')]),
                                  getattr(bridge_instance, self.Section1Sys[self.Section1Sys.index('WindguyEle_LeftDown')])]
            windguy_freeboard = min(windguy_elevations) - getattr(bridge_instance, self.Section1Sys[self.Section1Sys.index('HFL_Elevation')])
            freeboards = [maincable_freeboard, windguy_freeboard]
            result = False
            result = all([v > 5 for v in freeboards])
            Highlight = "danger" if not result else "normal"

            CableLength = bridge_instance.CableLength( self.DesignSpan, self.ElevationDifference, bd)
            E_Modulus = float(self.GUI_Inputs[self.Dtype_Frames[1]][0].get())

            self.bd_DeadLoad = float(self.GUI_Inputs[self.Dtype_Frames[2]][1].get())
            self.ConstantFactor = bridge_instance.ConstantFactor(CableLength, E_Modulus, self.MetallicAreaC_All, self.DesignSpan)


            data = {"Cable tension under full dead load": TensionValue, "Right bank elevation": EleRight, "Left bank elevation": EleLeft,
                    "Cable inclination at saddle under dead load, For higher foundation.": beta_1d, "For lower foundation": beta_2d,
                    "Horizonatal distance of lowest point of parabola from higher foundation, ed":Parabola_ed, "Maximium sag, fd": Parabola_fd,
                    "Total cable length":CableLength, "Main cable freeboard":maincable_freeboard,
                    "Windguy cable freeboard": windguy_freeboard, "Freeboard check": result}
            self.insert_dict_into_table(data, highlight = Highlight)
        def Processing2(event, iteration_entries):
            #Tolerance correction
            tolerance = float(iteration_entries[0].get())

            bd =  float(self.GUI_Inputs[self.Dtype_Frames[2]][1].get())
            #Hoisting load sag by iteration
            delG_ = 1
            bdHoisting = bd
            MulFactor = 0.93
            HoistingLoad = float(self.GUI_Inputs[self.Dtype_Frames[1]][1].get())
            DeadLoad = float(self.GUI_Inputs[self.Dtype_Frames[1]][8].get())
            FullLoad = float(self.GUI_Inputs[self.Dtype_Frames[1]][10].get())

            CoOrdsX = []
            CoOrdsY = []
            while delG_ > tolerance:
                b_, g_,newB_,  delG_ = bridge_instance.SagIteration(bd, bdHoisting, self.ConstantFactor, DeadLoad, HoistingLoad, MulFactor)
                MulFactor = 1
                bdHoisting = newB_

                CoOrdsX.append(b_)
                CoOrdsY.append(delG_)


            # Add multiple plots
            self.plot_manager.add_plot(CoOrdsX, CoOrdsY, "Dead load sag iteration", "b *", "Error :  ΔGi = gi - g*",
                                       "Scatter")


            ######################################################################################
            #Full load sag by iteration
            delG_ = 1
            bdFull = bd
            MulFactor = 1.22

            CoOrdsX = []
            CoOrdsY = []
            while delG_ > tolerance:
                b_, g_,newB_,  delG_ = bridge_instance.SagIteration(bd, bdFull, self.ConstantFactor, DeadLoad, FullLoad, MulFactor)
                MulFactor = 1
                bdFull = newB_

                CoOrdsX.append(b_)
                CoOrdsY.append(delG_)

            self.plot_manager.add_plot(CoOrdsX, CoOrdsY, "Full load sag iteration", "b *", "Error :  ΔGi = gi - g*",
                                       "Scatter")
            data = {"Sag from hoisting load iteration": bdHoisting, "Sag from full load iteration": bdFull}

            self.bd_HoistingLoad = bdHoisting
            self.bd_FullLoad = bdFull
            self.insert_dict_into_table(data)


        # Create a container frame with grid layout
        container = ttk.Frame(self.Macro_main_frame)
        container.grid(row=0, column=0, sticky="nsew")

        # Configure resizing behavior for container and root frame
        self.Macro_main_frame.rowconfigure(0, weight=1)
        self.Macro_main_frame.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # Create canvas with a scrollbar
        canvas = tk.Canvas(container)
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Enable Mouse Scroll for Canvas
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        # Main frame inside canvas
        main_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        # Ensure main_frame resizes dynamically
        def resize_canvas(event):
            # print(container.winfo_width())
            canvas.itemconfig(canvas_window, width=int(0.9999 *container.winfo_width()))

        container.bind("<Configure>", resize_canvas)

        # main_frame = self. ScrollableFrameUnderFrame(self.Macro_main_frame)
        # ================== LEVEL 1 ==================

        Frame1Title = self.Dtype_Frames[0]
        Frame2Title =  self.Dtype_Frames[1]
        Child1Obj, FrameObjects = self.frame_Creator(main_frame, Child1Title = "Level 1", Child2Titles = [Frame1Title,Frame2Title], vertical = True)

        input_frame = FrameObjects[0]
        tension_frame = FrameObjects[1]

        # Example usage
        input_frame = FrameObjects[0]
        tension_frame = FrameObjects[1]

        # Define Input Frame Labels, Remarks, Variable Types, and Widget Types
        input_labels = ["Bridge span", "Foundation setback - Right", "Foundation setback - Left",
                        "Main cables elevation - Right",
                        "Main cables elevation - Left", "Windguy cable elevation upstream - Right",
                        "Windguy cable elevation upstream - Left",
                        "Windguy cable elevation downstream - Right", "Windguy cable elevation downstream - Left","HFL elevation",  "Anchorage Type", "Submit"]
        input_remarks = ["",
                         "",
                         "", "", "", "", "", "", "", "", ["Drum Type", "Open Type"], ""]
        input_columnspan = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2]
        input_var_types = ["float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "string", "string"]
        input_widgets = ["entry", "entry", "entry", "entry", "entry", "entry", "entry", "entry",
                         "entry", "entry", "dropdown", "button"]  # Specify widget types

        # Create labels and entries for the input frame
        input_entries = self.create_labels_and_entries(FrameObjects[0], input_labels, input_remarks,input_columnspan, input_var_types,
                                                  input_widgets, Information = "Provide information in 'm' unit")
        self.GUI_Inputs[Frame1Title] = [obj for obj in input_entries]
        input_data = {label: entry for label, entry in zip(input_labels, input_entries)}

        input_entries[-1].bind("<Button-1>", lambda event:  Section1(event, input_data, input_remarks, input_var_types))
        self.GUI_KeyValue[Frame1Title] = input_data





        # # You can similarly create labels and entries for the tension frame
        tension_labels = ["Modulus of elasticity (kN/mm²)","Hoisting loads", "Walkway deck (steel)", "Walkway support (incl hangers)", "Fixation cables", "Wiremesh netting","Windguy cables load", "Windties (average)", "Total dead load","Live load", "Full load", "Refresh Calculation", "Submit load"]
        tension_remarks = [110, "", 0.370, 0.220, 0.010 , 0.060, "", 0.03, "", "","", "", ""]
        tension_columnspan = [1, 1, 1, 1, 1, 1, 1, 1, 1,1,1,1, 2]
        tension_var_types = ["float", "float" , "float" , "float" , "float", "float", "float", "float", "float", "float","float","string", "string"]
        tension_widgets = ["entry","entry", "entry","entry","entry","entry","entry","entry","entry","entry","entry","button", "button"]  # Specify widget types
        tension_entries = self.create_labels_and_entries(FrameObjects[1], tension_labels, tension_remarks,tension_columnspan, tension_var_types,
                                                    tension_widgets, "Tension Parameters")
        self.GUI_Inputs[Frame2Title] = [obj for obj in tension_entries]
        data = {label: entry for label, entry in zip(tension_labels, tension_entries)}
        self.GUI_KeyValue[Frame2Title] = data

        tension_entries[-2].bind("<Button-1>", lambda event: LoadsAutoUpdate(event, tension_entries))

        tension_entries[-1].bind("<Button-1>", lambda event: LoadSubmit(event, tension_entries))





        # # ================== LEVEL 2 ==================
        Child1Obj, FrameObjects = self.frame_Creator(main_frame, Child1Title = "Processing", Child2Titles = [self.Dtype_Frames[2], self.Dtype_Frames[3]], vertical = True)


        adopted_labels = ["Elevation difference (L/R)", "Dead load sag (bd)", "Shift foundation elevation of", "Check"]
        adopted_remarks = ["","",  ["Left foundation", "Right Foundation"], ""]
        adopted_columnspan = [1, 1,1,  2]
        adopted_var_types = ["float","float",  "string" , "string" ]
        adopted_widgets = ["entry","entry", "dropdown", "button"]  # Specify widget types
        adopted_entries = self.create_labels_and_entries(FrameObjects[0], adopted_labels, adopted_remarks,adopted_columnspan, adopted_var_types,
                                                    adopted_widgets, "Elevation difference is selected so as to have safe and economic span. Specify which foundation would you like to change based on adopted elevation difference and dead load sag.")
        self.GUI_Inputs[self.Dtype_Frames[2]] = [obj for obj in adopted_entries]
        data = {label: entry for label, entry in zip(adopted_labels, adopted_entries)}
        self.GUI_KeyValue[self.Dtype_Frames[2]] = data

        self.GUI_Inputs[self.Dtype_Frames[2]][0].bind("<FocusOut>", lambda event: Deadloadsag_range())
        adopted_entries[-1].bind("<Button-1>", lambda event: Processing1(event, self.GUI_Inputs[self.Dtype_Frames[2]]))



        sagiteration_labels = ["Error tolerance", "Check hoisting load and full load sag"]
        sagiteration_remarks = ["0.0001", ""]
        sagiteration_columnspan = [1, 2]
        sagiteration_var_types = ["float",  "string" ]
        sagiteration_widgets = ["entry", "button"]  # Specify widget types
        sagiteration_entries = self.create_labels_and_entries(FrameObjects[1], sagiteration_labels, sagiteration_remarks,sagiteration_columnspan, sagiteration_var_types,
                                                    sagiteration_widgets, "Sag iteration will be performed and values are presented based on the tolerance of 0.0001")
        self.GUI_Inputs[self.Dtype_Frames[3]] = [obj for obj in sagiteration_entries]
        data = {label: entry for label, entry in zip(sagiteration_labels, sagiteration_entries)}
        self.GUI_KeyValue[self.Dtype_Frames[3]] = data

        sagiteration_entries[-1].bind("<Button-1>", lambda event: Processing2(event,  self.GUI_Inputs[self.Dtype_Frames[3]]))


        # # ================== LEVEL 3 ==================
        Child1Obj, FrameObjects = self.frame_Creator(main_frame, Child1Title = "Final Design", Child2Titles = [self.Dtype_Frames[4], self.Dtype_Frames[5]], vertical = True)
        finalDesign_labels = ["Final Design"]
        finalDesign_remarks = [""]
        finalDesign_columnspan = [2]
        finalDesign_var_types = [ "string" ]
        finalDesign_widgets = [ "button"]  # Specify widget types
        finalDesign_entries = self.create_labels_and_entries(FrameObjects[1], finalDesign_labels, finalDesign_remarks,finalDesign_columnspan, finalDesign_var_types,
                                                    finalDesign_widgets, "Click on final design to review the complete design data.")
        self.GUI_Inputs[self.Dtype_Frames[4]] = [obj for obj in finalDesign_entries]
        data = {label: entry for label, entry in zip(finalDesign_labels, finalDesign_entries)}
        self.GUI_KeyValue[self.Dtype_Frames[4]] = data

        def FinalDesign(event):
            ele_Diff = float(self.GUI_Inputs[self.Dtype_Frames[2]][0].get())
            MC_area = self.MetallicAreaMC
            HC_area = self.MetallicAreaHC
            Total_CArea = self.MetallicAreaC_All
            hoistLoad = float(self.GUI_Inputs[self.Dtype_Frames[1]][1].get())
            deadLoad = float(self.GUI_Inputs[self.Dtype_Frames[1]][8].get())
            fullLoad = float(self.GUI_Inputs[self.Dtype_Frames[1]][10].get())
            Loads = [hoistLoad, deadLoad, fullLoad]
            Sags = [self.bd_HoistingLoad, self.bd_DeadLoad, self.bd_FullLoad]
            titles = ["Hoisting load", "Dead load", "Full load"]



            Inputs_data = {"Design span (m)": self.DesignSpan, "Foundation elevation difference (m)": ele_Diff, "Main cables metallic area (mm2)": MC_area,
                    "Handrail cables metallic area (mm2)":HC_area, "Total metallic area (mm2)":Total_CArea, "Total hoisting load (kN/m)": hoistLoad,
            "Total dead load (kN/m)": deadLoad, "Full load (kN/m)":fullLoad, "Sag due to hoisting load (m)":self.bd_HoistingLoad, "Sag due to dead load (m)": self.bd_DeadLoad,
                    "Sag due to full load (m)": self.bd_FullLoad}
            self.insert_dict_into_table(Inputs_data)

            #Output data
            Outputs_data = {}
            for index, (load, sag, title) in enumerate(zip(Loads, Sags, titles)):
                beta1 = bridge_instance.betaCalc ( sag, ele_Diff, self.DesignSpan)
                beta2 = bridge_instance.betaCalc ( sag, -ele_Diff, self.DesignSpan)

                ed = bridge_instance.ed_Distance( self.DesignSpan, ele_Diff, sag)
                f = bridge_instance.foundationSag( sag, ele_Diff)
                L = bridge_instance.CableLength( self.DesignSpan, ele_Diff, sag)

                H = bridge_instance.TotalHorizontal_T(self.DesignSpan, load, sag)

                Tmax =bridge_instance.T_Max(H, beta1)
                Tm_Max =bridge_instance.Tm_Max(Tmax, self.MetallicAreaMC, self.MetallicAreaC_All)
                Tm =bridge_instance.Tm(H, beta2, self.MetallicAreaMC, self.MetallicAreaC_All)
                Th_Max =bridge_instance.Th_Max(Tmax, self.MetallicAreaHC, self.MetallicAreaC_All)
                Th =bridge_instance.Th(H, beta2, self.MetallicAreaHC, self.MetallicAreaC_All)

                valuesTitles = [
                f"{title} beta1 (deg)",
                f"{title} beta2 (deg)",
                f"{title} ed (m)",
                f"{title} f (m)",
                f"{title} L (m)",
                f"{title} H (kN)",
                f"{title} Tmax (kN)",
                f"{title} Tm_Max (kN)",
                f"{title} Tm (kN)",
                f"{title} Th_Max (kN)",
                f"{title} Th  (kN)"]
                values = [beta1,
beta2,
ed,
f,
L,
H,
Tmax,
Tm_Max,
Tm,
Th_Max,
Th ]
                for (key, value) in zip(valuesTitles, values):
                    Outputs_data[key] = value
            self.insert_dict_into_table(Outputs_data)

            self.export_to_excel( filename="Bridge_Design_Output.xlsx")



        finalDesign_entries[-1].bind("<Button-1>", lambda event: FinalDesign(event))





        # Implementation details same as procedural_based_design

    def suspension_bridge_design(self):
        pass
    def suspended_bridge_design(self):
        self.destroy_and_create_frame()
        self.log_activity("Running on Suspended bridge design (D Type).")
        # Implementation details same as procedural_based_design


# Initialize the main application window
root = tk.Tk()
app = BridgeManagementApp(root)
root.mainloop()
