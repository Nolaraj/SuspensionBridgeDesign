import tkinter as tk
from tkinter import ttk, Menu, messagebox
from ttkbootstrap import Style
from datetime import datetime
from tkinter.scrolledtext import ScrolledText
import threading
import SuspendedBridge_Calculations
import Basic_Scripts
import textwrap


class BridgeManagementApp:
    def __init__(self, root):
        self.UnknownVartype = "Unknown variable type"
        self.NotValidVartype = "Not valid datatype"
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
        file_menu.add_command(label="Import .xlsx")
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
        title_frame.pack(side="top", fill="x")

        logger_frame = ttk.LabelFrame(title_frame, text="Activity Log", padding=5, style="info.TLabelframe")
        logger_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Content frame to hold listbox and empty frame
        content_frame = tk.Frame(logger_frame)
        content_frame.pack(fill="both", expand=True)

        # Configure grid layout for equal spacing
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Listbox (Left 50%)
        self.log_listbox = ScrolledText(content_frame, height=10, width=10, font=("Courier", 8))
        self.log_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)


        # Empty Frame (Right 50%)
        empty_frame = tk.Frame(content_frame, bg="lightgray", width=800, height=100)  # Fixed size
        empty_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Create Scrollbars
        h_scroll = tk.Scrollbar(empty_frame, orient="horizontal")
        v_scroll = tk.Scrollbar(empty_frame, orient="vertical")

        # Create Canvas with Fixed Dimensions
        canvas = tk.Canvas(empty_frame, width=empty_frame.winfo_width(), height=empty_frame.winfo_height(),
                           xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        canvas.place(x=0, y=0, width=empty_frame.winfo_width(), height=empty_frame.winfo_height())
        # Pack Scrollbars
        h_scroll.pack(side="bottom", fill="x")
        v_scroll.pack(side="right", fill="y")

        # Configure Scrollbars
        h_scroll.config(command=canvas.xview)
        v_scroll.config(command=canvas.yview)

        # Prevent resizing of canvas beyond original frame size
        def adjust_canvas_size(event):
            canvas.config(width=empty_frame.winfo_width(), height=empty_frame.winfo_height())

        empty_frame.bind("<Configure>", adjust_canvas_size)  # Keeps canvas fixed to frame size

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

        print(f"Character width: {char_width} pixels")
        print(f"ScrolledText widget width: {widget_pixel_width} pixels")
        print(f"Approx. characters per line: {chars_per_line}")
        return chars_per_line
    def insert_dict_into_table(self, dictionary, textspan=20, centralgap = 2, highlight=False):
        """Inserts the dictionary values into the ScrolledText widget in a table format."""
        chars_per_line = self.calculate_line_capacity( self.log_listbox)
        # Clear the ScrolledText widget

        # Insert headers
        gap0 = textspan - 3 + 2
        gap00 = 2*textspan + 2
        self.log_listbox.insert("end", f'Key{" "*gap0}Value\n')
        self.log_listbox.insert("end", "-" * gap00 + "\n")  # Separator line

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

                line = f'{value1}{" "*gap1}{value2}{" "*gap2}'
                lines.append(line)
            for line in lines:
                if highlight:
                    self.log_listbox.tag_configure("highlight", font=("Courier", 10, "bold"))
                    self.log_listbox.insert("end", line)
                else:
                    self.log_listbox.insert("end", line)



            # Auto-scroll to the latest entry
            self.log_listbox.yview(tk.END)
            self.log_listbox.insert("end", "\n")













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

    def frame_Creator(self, ParentFrame, Child1Title, Child2Titles):
            FrameObjects = []
            Child1Obj = ttk.LabelFrame(ParentFrame, text=Child1Title, padding=10, style="primary.TLabelframe")
            Child1Obj.pack(fill="both", expand=True, padx=5, pady=0)  # Using pack to fill entire space

            for index, value in enumerate(Child2Titles):
                Cables_frame = ttk.LabelFrame(Child1Obj, text=value, padding=10,
                                              style="success.TLabelframe")
                Cables_frame.grid(row=0, column=index, padx=5, pady=0, sticky="nsew")
                FrameObjects.append(Cables_frame)

            for index, value in enumerate(FrameObjects):
                Child1Obj.columnconfigure(index, weight=1)  # Input Frame

            for index, value in enumerate(FrameObjects):
                value.columnconfigure(1, weight=1)

                # entry = ttk.Entry(value, font=("Times New Roman", 10), bootstyle="info")
                # entry.grid(row=index, column=1, padx=0, pady=0, sticky="ew")
            return Child1Obj, FrameObjects

    def create_labels_and_entries(self, frame, labels, remarks, var_types, widgets, Information = ""):
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
            for i, (text, remark, var_type, widget_type) in enumerate(zip(labels, remarks, var_types, widgets)):
                label = ttk.Label(frame, text=text, font=("Times New Roman", 10))
                label.grid(row=i + dynrow, column=0, padx=10, pady=0, sticky="w")
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
                if widget_type == "entry":


                    entry = ttk.Entry(frame, textvariable=var, font=("Times New Roman", 9, "italic"), bootstyle="info")
                    entry.grid(row= i + dynrow, column=1, padx=0, pady=0, sticky="ew")
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
                    var = tk.StringVar(value=options[0])

                    dropdown = ttk.Combobox(frame, textvariable=var, values=options, font=("Times New Roman", 10))
                    dropdown.grid(row=i + dynrow, column=1, padx=10, pady=0, sticky="ew")

                    entries.append(dropdown)  # Store the dropdown variable

                elif widget_type == "button":
                    button = ttk.Button(frame, text=text, command=lambda t=text: self.on_button_click(t))
                    button.grid(row=i + dynrow, column=1, padx=10, pady=0, sticky="ew")
                    entries.append(None)  # No entry to store for buttons
                elif widget_type == "radio":
                    radio1 = ttk.Radiobutton(self.frame, text="Option 1", variable=self.radio_value, value="1")
                    radio2 = ttk.Radiobutton(self.frame, text="Option 2", variable=self.radio_value, value="2")

                else:
                    raise ValueError("Invalid widget type specified. Use 'entry', 'dropdown', or 'button'.")

            return entries
    def on_button_click(self, button_text):
            messagebox.showinfo("Button Clicked", f"You clicked: {button_text}")


    def procedural_based_design(self):
        self.destroy_and_create_frame()
        self.log_activity("Running on procedural based design.")

        #Initialize D type calculations
        D_Type = SuspendedBridge_Calculations.SuspendedBridge
        bridge_instance = D_Type()

        def Section1(event, LabelEntry, remarks, input_var_types):
            Section1Sys = [
                'Survey_Distance',
                'FoundationShift_Right',
                'FoundationShift_Left',
                'MainCableEle_Right',
                'MainCableEle_Left',
                'WindguyEle_RightUp',
                'WindguyEle_LeftUp',
                'WindguyEle_RightDown',
                'WindguyEle_LeftDown'
            ]

            for index, (key, value) in enumerate(LabelEntry.items()):

                if isinstance(value, tk.Radiobutton):  # Check if it's a Radiobutton
                    entry_value = value.cget()  # This gets the value associated with the radiobutton
                else:
                    entry_value = value.get().strip()  # Get text from Entry widgets
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
                if entry_value in ["", self.UnknownVartype, self.NotValidVartype]:
                    continue  # Skip processing
                elif entry_value == original_remark or entry_value == stored_remark:
                    continue
                else:
                    if isinstance(remarks[index], list):
                        if value.get() == "Drum Type":
                            bridge_instance.CableAnchorage_DrumType = True
                            bridge_instance.CableAnchorage_OpenType = False
                        if value.get() == "Open Type":
                            bridge_instance.CableAnchorage_DrumType= False
                            bridge_instance.CableAnchorage_OpenType= True
                    else:
                        # Section1Sys[index] = entry_value
                        setattr(bridge_instance, Section1Sys[index], entry_value)  # Dynamically set the value
                        print(Section1Sys[index], getattr(bridge_instance, Section1Sys[index]))

                    # print(f"Processed Entry: {entry_value}, Is Tkinter Widget: {isinstance(value, tk.Widget)}")

            DesignSpan, LowestPoint_Check, hTolerance, ElevationDifference = bridge_instance.SpanHeight_Calculations()

            data = {"Design Span": DesignSpan, "Elevation Difference L/R": ElevationDifference, "Span / 14" :hTolerance , "(Span / 14) > Elevation Difference L/R": LowestPoint_Check}
            self.insert_dict_into_table(data,textspan= 33, highlight= not LowestPoint_Check)

            Tmax_Approx, MCHC_Approx, MetallicAreaC_All, MCHCLoad_Dead = bridge_instance.preCalculation_TMCHC(DesignSpan, Basic_Scripts.ExcelTable_extractor(Basic_Scripts.StandardExcel_Path, Basic_Scripts.Sheetname1, Basic_Scripts.TableName1)[0])

            data = {"Approximate maximum cable tension": Tmax_Approx, "Metallic area provided": MetallicAreaC_All, "Cables dead load, kN/m": MCHCLoad_Dead}
            self.insert_dict_into_table(data, textspan= 33)
            self.insert_dict_into_table(MCHC_Approx, textspan= 33)



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

        Child1Obj, FrameObjects = self.frame_Creator(main_frame, Child1Title = "Level 1", Child2Titles = ["Survey data", "Tension Design"])

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
                        "Windguy cable elevation downstream - Right", "Windguy cable elevation downstream - Left", "Anchorage Type"]
        input_remarks = ["Horizontal component of bridge span proposed during survey. ",
                         "Foundation shift from proposed position. ",
                         "Foundation shift from proposed position. ", "", "", "", "", "", "", ["Drum Type", "Open Type"]]
        input_var_types = ["float", "float", "float", "float", "float", "float", "float", "float", "float", "string"]
        input_widgets = ["entry", "entry", "entry", "entry", "entry", "entry", "entry", "entry",
                         "entry", "dropdown"]  # Specify widget types

        # Create labels and entries for the input frame
        input_entries = self.create_labels_and_entries(FrameObjects[0], input_labels, input_remarks, input_var_types,
                                                  input_widgets, Information = "Provide information in 'm' unit")
        data = {label: entry for label, entry in zip(input_labels, input_entries)}

        last_entry = input_entries[-1]
        last_entry.bind("<FocusOut>", lambda event: Section1(event, data, input_remarks, input_var_types))














        # You can similarly create labels and entries for the tension frame
        tension_labels = ["Tension value 1", "Tension value 2", "Tension value 3"]
        tension_remarks = ["Enter tension value 1", "Enter tension value 2", "Enter tension value 3"]
        tension_var_types = ["int", "int", "int"]
        tension_widgets = ["entry", "button", "entry"]  # Specify widget types

        tension_entries = self.create_labels_and_entries(FrameObjects[1], tension_labels, tension_remarks, tension_var_types,
                                                    tension_widgets, "Tension Parameters")
        # tension_entries[-1].bind("<FocusOut>", self.on_last_entry_filled)

        # Define Tension Design Frame Labels and Entries
        tension_labels = ["Cable Tension (kN):", "Factor of Safety:", "Material Strength (MPa):", "Design Load (kN):"]
        tension_entries = []

        for i, text in enumerate(tension_labels):
            label = ttk.Label(tension_frame, text=text, font=("Times New Roman", 10))
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            entry = ttk.Entry(tension_frame, font=("Times New Roman", 10), bootstyle="info")
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entry.insert(0, "Enter value...")
            tension_entries.append(entry)
            # entry.bind("<FocusIn>", lambda event, e=entry: on_entry_click(event, e))

        # ================== LEVEL 2 ==================
        Child1Obj, FrameObjects = self.frame_Creator(main_frame, Child1Title = "Level 2", Child2Titles = ["Cable Design", "WindGuy Design"])
        Cables_frame  = FrameObjects[0]
        Windguy_frame = FrameObjects[1]

        # Define Level 2 Labels and Entries
        level_2_labels = ["Deck Thickness (cm):", "Wind Load Factor:", "Seismic Load Factor:", "Expansion Joint Type:"]
        level_2_entries = []

        for i, text in enumerate(level_2_labels):
            label = ttk.Label(Cables_frame, text=text, font=("Times New Roman", 10))
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            # if i < 3:  # Text entry fields
            entry = ttk.Entry(Cables_frame, font=("Times New Roman", 10), bootstyle="info")
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entry.insert(0, "Enter value...")
            level_2_entries.append(entry)
            # entry.bind("<FocusIn>", lambda event, e=entry: on_entry_click(event, e))
            # else:  # Dropdown for expansion joint type
            #     joint_types = ["Modular", "Finger Joint", "Elastomeric"]
            #     dropdown = ttk.Combobox(Cables_frame, values=joint_types, state="readonly", font=("Helvetica", 12))
            #     dropdown.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            #     level_2_entries.append(dropdown)


        Child1Obj, FrameObjects = self.frame_Creator(main_frame, Child1Title = "Level 2", Child2Titles = ["Cable Design", "WindGuy Design"])




    def suspension_bridge_design(self):
        self.destroy_and_create_frame()
        self.log_activity("Running on Suspension bridge design (N Type).")
        # Implementation details same as procedural_based_design

    def suspended_bridge_design(self):
        self.destroy_and_create_frame()
        self.log_activity("Running on Suspended bridge design (D Type).")
        # Implementation details same as procedural_based_design


# Initialize the main application window
root = tk.Tk()
app = BridgeManagementApp(root)
root.mainloop()
