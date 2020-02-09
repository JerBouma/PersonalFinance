from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk
from PIL import Image
import threading
from dataprocessor import *
from excelwriter import *
import time

button_color = '#334d3e'
report_button_color = "#ee7b4a"
button_text_colour = 'white'
background = 'lightgrey'


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        def get_file_path(variable, button):
            filename = filedialog.askopenfilename()
            variable.set(filename)
            button.config(textvariable=variable)

        def get_folder_path(variable, button):
            filename = filedialog.askdirectory()
            variable.set(filename)
            button.config(textvariable=variable)

        self.master.title("Personal Finance")
        self.pack(fill=BOTH, expand=1)

        image = ImageTk.PhotoImage(Image.open(resource_path("images\\PersonalFinancePNG.png")))
        panel = Label(self, image=image, bg=background)
        panel.image = image
        panel.grid(row=1,column=1, columnspan=3,sticky=W+E+N+S)

        self.bank_data_entry = StringVar()
        bank_data_button = Button(self, text="Browse Bank file (.csv)",
                                  command=lambda:get_file_path(self.bank_data_entry, bank_data_button),
                                  bg=button_color, fg=button_text_colour)
        bank_data_button.grid(row=2, column=1, columnspan=3, sticky=W+E+N+S, padx=10, pady=5)

        self.input_entry = StringVar()
        input_button = Button(self, text="Browse Input file (.xlsx)",
                              command=lambda:get_file_path(self.input_entry, input_button),
                              bg=button_color, fg=button_text_colour)
        input_button.grid(row=3, column=1, columnspan=3, sticky=W+E+N+S, padx=10, pady=5)

        self.output_entry = StringVar()
        output_button = Button(self, text="Output location",
                               command=lambda:get_folder_path(self.output_entry, output_button),
                               bg=button_color, fg=button_text_colour)
        output_button.grid(row=4, column=1, columnspan=3, sticky=W+E+N+S, padx=10, pady=5)

        excel_report_button = Button(self, text="Create Report", command=self.run_program,
                                     bg=report_button_color, fg=button_text_colour)
        excel_report_button.grid(row=5, column=1, columnspan=3, sticky=W+E+N+S,padx=10, pady=10)

    def generate_report(self):
        try:
            progress = Label(self, text="Collecting data..", bg=report_button_color, fg=button_text_colour)
            progress.grid(row=5, column=1, columnspan=3, sticky=W + E + N + S, padx=10, pady=10)
            input = load_personal_input(self.input_entry.get())
            bank_data = data_processor(self.bank_data_entry.get())
            bank_data = category_selector(input, bank_data)
            output_location = self.output_entry.get()

            progress = Label(self, text="Creating Category sheet..", bg=report_button_color, fg=button_text_colour)
            progress.grid(row=5, column=1, columnspan=3, sticky=W + E + N + S, padx=10, pady=10)
            excel_categories(input, output_location, bank_data)

            progress = Label(self, text="Creating Yearly sheets..", bg=report_button_color, fg=button_text_colour)
            progress.grid(row=5, column=1, columnspan=3, sticky=W + E + N + S, padx=10, pady=10)
            excel_bank_data_years(output_location, bank_data)

            progress = Label(self, text="Creating Total Overview sheet..", bg=report_button_color, fg=button_text_colour)
            progress.grid(row=5, column=1, columnspan=3, sticky=W + E + N + S, padx=10, pady=10)
            excel_report(input, output_location, bank_data)

            progress = Label(self, text="Done!", bg="#e2b940", fg=button_text_colour)
            progress.grid(row=5, column=1, columnspan=3, sticky=W + E + N + S, padx=10, pady=10)
            time.sleep(3)

        except Exception as error:
            messagebox.showerror('Error', "The program has crashed with the following error: \n\n"
            + str(error) + "\n\n If the problem persists, please create an Issue with the error "
            "message on the project's GitHub page: https://github.com/JerBouma/PersonalFinance/issues. \n\n"
            + "You can copy this entire message with CTRL + C.")

        excel_report_button = Button(self, text="Create Report", command=self.run_program,
                                     bg=report_button_color, fg=button_text_colour)
        excel_report_button.grid(row=5, column=1, columnspan=3, sticky=W + E + N + S, padx=10, pady=10)

    def run_program(self):
        threading.Thread(target=self.generate_report).start()


root = Tk()
app = Window(root)
app.configure(background=background)
root.iconbitmap("images/PersonalFinanceICO.ico")
root.resizable(False, False)
root.mainloop() 
