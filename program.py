from tkinter import *
from tkinter import messagebox
from PIL import ImageTk
from PIL import Image
import threading
from dataprocessor import *
from excelwriter import *
import time

button_color = '#ff6633'
button_text_colour = 'white'
background = 'white'


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        self.master.title("Personal Finance")
        self.pack(fill=BOTH, expand=1)

        image = ImageTk.PhotoImage(Image.open(resource_path("images\\PersonalFinancePNG.png")))
        panel = Label(self, image=image, bg=background)
        panel.image = image
        panel.grid(row=1,column=1, columnspan=2,sticky=W+E+N+S)

        bank_data_label = Label(self, text="Bank file (.csv)", bg=background)
        bank_data_label.grid(row=2, column=1, sticky=E)

        self.bank_data_entry = StringVar()
        bank_data_entry = Entry(self, textvariable=self.bank_data_entry, width=100)
        bank_data_entry.grid(row=2, column=2, sticky=W, pady=10, padx=10)

        input_label = Label(self, text="Input file (.xlsx)", bg=background)
        input_label.grid(row=3, column=1, sticky=E)

        self.input_entry = StringVar()
        input_entry = Entry(self, textvariable=self.input_entry, width=100)
        input_entry.grid(row=3, column=2, sticky=W, pady=10, padx=10)

        output_label = Label(self, text="Output location", bg=background)
        output_label.grid(row=4, column=1, sticky=E)

        self.output_entry = StringVar()
        output_entry = Entry(self, textvariable=self.output_entry, width=100)
        output_entry.grid(row=4, column=2, sticky=W, pady=10, padx=10)

        excel_report_button = Button(self, text="Create Report", command=self.run_program,
                                     bg=button_color, fg=button_text_colour)
        excel_report_button.grid(row=5, column=1, columnspan=3, sticky=W+E+N+S,padx=10, pady=10)

    def generate_report(self):
        try:
            progress = Label(self, text="Collecting data..", bg=button_color, fg=button_text_colour)
            progress.grid(row=5, column=1, columnspan=2, sticky=W + E + N + S, padx=10, pady=10)
            input = load_personal_input(self.input_entry.get())
            bank_data = data_processor(self.bank_data_entry.get())
            bank_data = category_selector(input, bank_data)
            output_location = self.output_entry.get()

            progress = Label(self, text="Creating Category sheet..", bg=button_color, fg=button_text_colour)
            progress.grid(row=5, column=1, columnspan=2, sticky=W + E + N + S, padx=10, pady=10)
            excel_categories(input, output_location, bank_data)

            progress = Label(self, text="Creating Yearly sheets..", bg=button_color, fg=button_text_colour)
            progress.grid(row=5, column=1, columnspan=2, sticky=W + E + N + S, padx=10, pady=10)
            excel_bank_data_years(output_location, bank_data)

            progress = Label(self, text="Creating Total Overview sheet..", bg=button_color, fg=button_text_colour)
            progress.grid(row=5, column=1, columnspan=2, sticky=W + E + N + S, padx=10, pady=10)
            excel_report(input, output_location, bank_data)

            progress = Label(self, text="Done!", bg="Green", fg=button_text_colour)
            progress.grid(row=5, column=1, columnspan=2, sticky=W + E + N + S, padx=10, pady=10)
            time.sleep(3)

        except Exception as error:
            messagebox.showerror('Error', "The program has crashed with the following error: \n\n"
            + str(error) + "\n\n If the problem persists, please create an Issue with the error "
            "message on the project's GitHub page: https://github.com/JerBouma/PersonalFinance/issues. \n\n"
            + "You can copy this entire message with CTRL + C.")

        excel_report_button = Button(self, text="Create Report", command=self.run_program,
                                     bg=button_color, fg=button_text_colour)
        excel_report_button.grid(row=5, column=1, columnspan=3, sticky=W + E + N + S, padx=10, pady=10)

    def run_program(self):
        threading.Thread(target=self.generate_report).start()


root = Tk()
app = Window(root)
app.configure(background=background)
root.geometry('725x475')
root.iconbitmap("images/PersonalFinanceICO.ico")
root.resizable(False, False)
root.mainloop() 
