import tkinter as tk
from tkinter import ttk, Menu
from tkinter import messagebox
from ttkbootstrap import Style
from datetime import datetime


def secure_exit():
    if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
        log_activity("Application exited.")
        root.destroy()
def change_theme(theme_name):
    style.theme_use(theme_name)
    log_activity(f"Theme changed to {theme_name}.")
def open_theme_window():
    theme_window = tk.Toplevel(root)
    theme_window.title("Change Theme")
    theme_window.geometry("300x150")

    theme_label = ttk.Label(theme_window, text="Select Theme:", font=("Helvetica", 12))
    theme_label.pack(pady=10)

    theme_var = tk.StringVar()
    theme_dropdown = ttk.Combobox(
        theme_window,
        textvariable=theme_var,
        values=style.theme_names(),
        state="readonly",
        font=("Helvetica", 12)
    )
    theme_dropdown.pack(pady=5)
    theme_dropdown.current(0)

    apply_button = ttk.Button(
        theme_window,
        text="Apply Theme",
        style="info.TButton",
        command=lambda: change_theme(theme_var.get())
    )
    apply_button.pack(pady=10)
def ProceduralBased_Design():
    destroy_and_create_frame()
    log_activity("Running on procedural based design.")

    canvas = tk.Canvas(Macro_main_frame)
    canvas.pack(side="bottom", fill="both", expand=True)

    # Add a vertical scrollbar to the canvas
    scrollbar = ttk.Scrollbar(canvas, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    # Configure the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Bind mouse scroll operation
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # macOS Scroll Up
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # macOS Scroll Down

    # Create a frame inside the canvas
    main_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=main_frame, anchor="nw")


    # Content Frame
    content_frame = ttk.Frame(main_frame, padding=0)
    content_frame.pack(fill="both", expand=True, padx=0, pady=0)

    content_frame.grid_columnconfigure(0, weight=2)

    # Input Section
    input_frame = ttk.LabelFrame(
        content_frame,
        text="Input Parameters",
        padding=0,
        style="success.TLabelframe"
    )
    input_frame.grid(row=0, column=0, padx=10, pady=0, sticky="nsew")

    input_labels = ["Bridge Span (m):", "Bridge Width (m):", "Max Load (tons):", "Suspension Cable Type:"]
    input_entries = []

    def on_entry_click(event, entry):
            """Clears the default text when the user clicks inside the entry box."""
            entry.delete(0, tk.END)
            entry.config(foreground="black")  # Change text color to normal

    for i, text in enumerate(input_labels):
        label = ttk.Label(input_frame, text=text, font=("Times New Roman", 10))
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        if i < 3:
            entry = ttk.Entry(input_frame, font=("Times New Roman", 10), bootstyle="info")
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, "Enter valuedfgsgsgfsgdfgfg...")
            input_entries.append(entry)
            entry.bind("<FocusIn>", lambda event, e=entry: on_entry_click(event, e))  # Bind focus event

        else:
            cable_types = ["Steel", "Aluminum", "Carbon Fiber"]
            dropdown = ttk.Combobox(input_frame, values=cable_types, state="readonly", font=("Helvetica", 12))
            dropdown.grid(row=i, column=1, padx=10, pady=5)
            input_entries.append(dropdown)

    # Design Aspects Frame
    design_frame = ttk.LabelFrame(content_frame, text="Design Aspects", padding=15, style="primary.TLabelframe")
    design_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    design_label = ttk.Label(design_frame, text="Aspect Description:", font=("Helvetica", 12))
    design_label.pack(anchor="w", padx=10, pady=5)

    design_text = tk.Text(design_frame, height=5, font=("Helvetica", 12), wrap="word")
    design_text.pack(fill="both", padx=10, pady=5)

    # Considerations Frame
    consider_frame = ttk.LabelFrame(content_frame, text="Considerations", padding=15, style="primary.TLabelframe")
    consider_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    consider_label = ttk.Label(consider_frame, text="Key Considerations:", font=("Helvetica", 12))
    consider_label.pack(anchor="w", padx=10, pady=5)

    consider_text = tk.Text(consider_frame, height=5, font=("Helvetica", 12), wrap="word")
    consider_text.pack(fill="both", padx=10, pady=5)

    # Environmental Factors Frame
    environment_frame = ttk.LabelFrame(content_frame, text="Environmental Factors", padding=15,
                                       style="primary.TLabelframe")
    environment_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    environment_label = ttk.Label(environment_frame, text="Factors Description:", font=("Helvetica", 12))
    environment_label.pack(anchor="w", padx=10, pady=5)

    environment_text = tk.Text(environment_frame, height=5, font=("Helvetica", 12), wrap="word")
    environment_text.pack(fill="both", padx=10, pady=5)

    # Buttons Section
    button_frame = ttk.Frame(main_frame, padding=10)
    button_frame.pack(fill="x", padx=20, pady=10)

    submit_button = ttk.Button(
        button_frame,
        text="Submit",
        width=15,
        style="success.TButton",
        command=lambda: [
            messagebox.showinfo("Submit", "Data Submitted Successfully!"),
            log_activity("Data submitted successfully.")
        ]
    )
    submit_button.pack(side="left", padx=10)

    clear_button = ttk.Button(
        button_frame,
        text="Clear",
        width=15,
        style="warning.TButton",
        command=lambda: [
            [entry.delete(0, tk.END) for entry in input_entries[:-1]],
            log_activity("Form cleared.")
        ]
    )
    clear_button.pack(side="left", padx=10)

    exit_button = ttk.Button(
        button_frame,
        text="Exit",
        width=15,
        style="danger.TButton",
        command=secure_exit
    )
    exit_button.pack(side="right", padx=10)
def SuspensionBridge_Design():
    destroy_and_create_frame()
    log_activity("Running on Suspension bridge design (N Type).")

    canvas = tk.Canvas(Macro_main_frame)
    canvas.pack(side="bottom", fill="both", expand=True)

    # Add a vertical scrollbar to the canvas
    scrollbar = ttk.Scrollbar(canvas, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    # Configure the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Bind mouse scroll operation
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # macOS Scroll Up
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # macOS Scroll Down

    # Create a frame inside the canvas
    main_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=main_frame, anchor="nw")


    # Content Frame
    content_frame = ttk.Frame(main_frame, padding=0)
    content_frame.pack(fill="both", expand=True, padx=0, pady=0)

    content_frame.grid_columnconfigure(0, weight=2)

    # Input Section
    input_frame = ttk.LabelFrame(
        content_frame,
        text="Input Parameters",
        padding=15,
        style="success.TLabelframe"
    )
    input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    input_labels = ["Bridge Length (m):", "Bridge Width (m):", "Max Load (tons):", "Suspension Cable Type:"]
    input_entries = []

    for i, text in enumerate(input_labels):
        label = ttk.Label(input_frame, text=text, font=("Helvetica", 12))
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        if i < 3:
            entry = ttk.Entry(input_frame, font=("Helvetica", 12), bootstyle="info")
            entry.grid(row=i, column=1, padx=10, pady=5)
            input_entries.append(entry)
        else:
            cable_types = ["Steel", "Aluminum", "Carbon Fiber"]
            dropdown = ttk.Combobox(input_frame, values=cable_types, state="readonly", font=("Helvetica", 12))
            dropdown.grid(row=i, column=1, padx=10, pady=5)
            input_entries.append(dropdown)

    # Design Aspects Frame
    # design_frame = ttk.LabelFrame(content_frame, text="Design Aspects", padding=15, style="primary.TLabelframe")
    # design_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    #
    # design_label = ttk.Label(design_frame, text="Aspect Description:", font=("Helvetica", 12))
    # design_label.pack(anchor="w", padx=10, pady=5)
    #
    # design_text = tk.Text(design_frame, height=5, font=("Helvetica", 12), wrap="word")
    # design_text.pack(fill="both", padx=10, pady=5)

    # Considerations Frame
    consider_frame = ttk.LabelFrame(content_frame, text="Considerations", padding=15, style="primary.TLabelframe")
    consider_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    consider_label = ttk.Label(consider_frame, text="Key Considerations:", font=("Helvetica", 12))
    consider_label.pack(anchor="w", padx=10, pady=5)

    consider_text = tk.Text(consider_frame, height=5, font=("Helvetica", 12), wrap="word")
    consider_text.pack(fill="both", padx=10, pady=5)

    # Environmental Factors Frame
    environment_frame = ttk.LabelFrame(content_frame, text="Environmental Factors", padding=15,
                                       style="primary.TLabelframe")
    environment_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    environment_label = ttk.Label(environment_frame, text="Factors Description:", font=("Helvetica", 12))
    environment_label.pack(anchor="w", padx=10, pady=5)

    environment_text = tk.Text(environment_frame, height=5, font=("Helvetica", 12), wrap="word")
    environment_text.pack(fill="both", padx=10, pady=5)

    # Buttons Section
    button_frame = ttk.Frame(main_frame, padding=10)
    button_frame.pack(fill="x", padx=20, pady=10)

    submit_button = ttk.Button(
        button_frame,
        text="Submit",
        width=15,
        style="success.TButton",
        command=lambda: [
            messagebox.showinfo("Submit", "Data Submitted Successfully!"),
            log_activity("Data submitted successfully.")
        ]
    )
    submit_button.pack(side="left", padx=10)

    clear_button = ttk.Button(
        button_frame,
        text="Clear",
        width=15,
        style="warning.TButton",
        command=lambda: [
            [entry.delete(0, tk.END) for entry in input_entries[:-1]],
            log_activity("Form cleared.")
        ]
    )
    clear_button.pack(side="left", padx=10)

    exit_button = ttk.Button(
        button_frame,
        text="Exit",
        width=15,
        style="danger.TButton",
        command=secure_exit
    )
    exit_button.pack(side="right", padx=10)
def SuspendedBridge_Design():
    destroy_and_create_frame()
    log_activity("Running on Suspended bridge design.  (D Type)")

    canvas = tk.Canvas(Macro_main_frame)
    canvas.pack(side="bottom", fill="both", expand=True)

    # Add a vertical scrollbar to the canvas
    scrollbar = ttk.Scrollbar(canvas, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    # Configure the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Bind mouse scroll operation
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # macOS Scroll Up
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # macOS Scroll Down





# Initialize the main application window
style = Style(theme="cosmo")
root = style.master
root.title("Bridge Management System")
root.geometry("1024x700")
root.resizable(False, True)
root.protocol("WM_DELETE_WINDOW", secure_exit)

# Add a canvas for scrolling
title_frame = tk.Frame(root)
title_frame.pack(side="top", fill="x")


# Create the menu bar
menu_bar = Menu(root)
root.config(menu=menu_bar)

# File menu
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New")
file_menu.add_command(label="Open")
file_menu.add_command(label="Import .xlsx")
file_menu.add_command(label="Save")
file_menu.add_separator()
file_menu.add_command(label="Exit", command=secure_exit)
menu_bar.add_cascade(label="File", menu=file_menu)

#Design Menu
design_menu = Menu(menu_bar, tearoff=0)
design_menu.add_command(label="Calculation Based", command= ProceduralBased_Design)
design_menu.add_separator()
design_menu.add_command(label="Suspension Bridge (N_Type)", command= SuspensionBridge_Design)
design_menu.add_command(label="Suspended Bridge (D_Type)", command= SuspendedBridge_Design)
menu_bar.add_cascade(label="Design Aspects", menu=design_menu)

# View menu
view_menu = Menu(menu_bar, tearoff=0)
view_menu.add_command(label="Change Theme", command=open_theme_window)
menu_bar.add_cascade(label="View", menu=view_menu)

# About menu
about_menu = Menu(menu_bar, tearoff=0)
about_menu.add_command(label="About",
                       command=lambda: messagebox.showinfo("About", "Bridge Management System v2.0 \n Developer: Prem Thapa Magar"))
menu_bar.add_cascade(label="About", menu=about_menu)

# Header Frame with Log Information
# Logger Frame
def log_activity(message):
    """Appends a message with the current timestamp to the log listbox."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_listbox.insert(tk.END, f"[{current_time}] {message}")
    log_listbox.yview_moveto(1)  # Auto-scroll to the latest entry

logger_frame = ttk.LabelFrame(
    title_frame,
    text="Activity Log",
    padding=15,
    style="info.TLabelframe"
)
logger_frame.pack(fill="x", padx=10, pady=10)

log_listbox = tk.Listbox(logger_frame, height=4, font=("Times New Roman", 8))
log_listbox.pack(fill="both", expand=True, padx=0, pady=0)

# Update Log for Any Activity
log_activity("Application started.")





# Initialize Macro_main_frame as None to handle it later
Macro_main_frame = None
def destroy_and_create_frame():
    """Destroys the existing Macro_main_frame (if it exists) and recreates it."""
    global Macro_main_frame

    # Destroy existing Macro_main_frame if it exists
    if Macro_main_frame is not None:
        Macro_main_frame.destroy()

    # Recreate the Macro_main_frame
    Macro_main_frame = ttk.Frame(root, padding=0)
    Macro_main_frame.pack(fill="both", expand=True, padx=0, pady=0)
















# # Footer Section
# footer_frame = ttk.Frame(Macro_main_frame, padding=10, style="secondary.TFrame")
# footer_frame.pack(fill="x", pady=10)
#
# version_label = ttk.Label(
#     footer_frame,
#     text=f"Current Version: v2.0",
#     font=("Helvetica", 12)
# )
# version_label.pack(side="left", padx=10)
#
# time_label = ttk.Label(
#     footer_frame,
#     text=f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
#     font=("Helvetica", 12)
# )
# time_label.pack(side="right", padx=10)

# Run the application
root.mainloop()
