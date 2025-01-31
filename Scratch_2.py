import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

class App:
    def __init__(self, root):
        self.root = root
        self.frame = ttk.Frame(root)
        self.frame.pack()

        # Create a ScrolledText widget for logging
        self.log_listbox = ScrolledText(self.frame, width=100, height=20, font=("Courier", 10))
        self.log_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Example dictionary to insert into the table
        example_dict = {
            "Anchorage type": "Drum",
            "Main Cables Number": "4",
            "Main Cables Diameter(mm)": "40",
            "Handrail Cables Diameter (mm)": "26",
            "Tbreak (kN)": "4428",
            "Tpermissible (kN)": "1476"
        }

        # Insert the dictionary into the ScrolledText widget
        self.insert_dict_into_table(example_dict, textspan=12, highlight=False)

    def insert_dict_into_table(self, dictionary, textspan=20, centralgap = 2, highlight=False):
        """Inserts the dictionary values into the ScrolledText widget in a table format."""
        # Clear the ScrolledText widget
        self.log_listbox.delete("1.0", tk.END)

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
                gap2 = textspan - lenV2

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

        # Handle cases where the value is very short (e.g., "Drum")
        if not wrapped_lines:
            wrapped_lines.append(text)

        return wrapped_lines


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
