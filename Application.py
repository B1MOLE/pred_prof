import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os
import Model

class Main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Классификатор")
        self.geometry("500x300")

        self.label = tk.Label(self, text="Классификатор интернет ресурсов", bg='#F0F0F0', fg='#333333',
                              font=('Arial', 18, 'bold'))
        self.label.pack(pady=(20, 10))

        self.button = tk.Button(self, text="Классификатор", command=self.open_classificator, font=('Arial', 12))
        self.button.pack(pady=10)

        self.button1 = tk.Button(self, text="Классифицированные ссылки", command=self.open_classified_urls,
                                 font=('Arial', 12))
        self.button1.pack(pady=10)

        self.button2 = tk.Button(self, text="Выход", command=self.destroy, font=('Arial', 12))
        self.button2.pack(pady=10)

    def open_classificator(self):
        self.withdraw()
        Classificator(self)

    def open_classified_urls(self):
        self.withdraw()
        Classified_urls(self)


class Classificator(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.title("Классификатор")
        self.geometry("600x150")
        self.model = Model.Model("model", "vect")

        self.label1 = tk.Label(self, text='Введите URL для классификации', font=('Arial', 12))
        self.label1.grid(row=0, column=0, padx=10, pady=10)

        self.url_entry = tk.Entry(self, width=20, font=('Arial', 12))
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        self.button1 = tk.Button(self, text='Классифицировать', command=self.classify_url, font=('Arial', 12))
        self.button1.grid(row=1, column=1, padx=10, pady=10)

        self.button2 = tk.Button(self, text='Классифицировать ссылки из CSV файла', command=self.classify_urls_from_csv,
                                 font=('Arial', 12))
        self.button2.grid(row=1, column=0, padx=10, pady=10)

        self.button3 = tk.Button(self, text='Назад', command=self.back, font=('Arial', 12))
        self.button3.place(x=300, y=100)

    def classify_url(self):
        url = self.url_entry.get()
        category = self.model.execute_model(url)

        # Сохранение URL и категорию в файл CSV
        df = pd.DataFrame({'URL': [url], 'Category': [category]})
        df.to_csv('classified_urls.csv', mode='a', header=not os.path.exists('classified_urls.csv'), index=False)

        self.url_entry.delete(0, tk.END)

        # Обновление таблицы с классифицированными URL-адресами
        classified_urls = pd.read_csv('classified_urls.csv')
        tk.messagebox.showinfo(title="Классификация URL", message="Класс этой ссылки: " + " " + category)

    def classify_urls_from_csv(self):
        csv_file_path = filedialog.askopenfilename(title="Select CSV file")
        if csv_file_path:
            classified_urls = pd.read_csv(csv_file_path)
            data = []
            for row in classified_urls.itertuples(index=False):
                url = row[0]
                category = self.model.execute_model(url)
                data.append({'URL': url, 'Category': category})

            # Сохранение URL и категорию в файл CSV
            df = pd.DataFrame(data)
            df.to_csv('classified_urls.csv', header=not os.path.exists('classified_urls.csv'), mode='a', index=False)

            # Обновление таблицы с классифицированными URL-адресами
            classified_urls = pd.read_csv('classified_urls.csv')
            tk.messagebox.showinfo(title="Классификация URL", message="Ссылки успешно определены")

    def back(self):
        self.destroy()
        app = Main()
        app.grab_set()

class Classified_urls(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        if os.path.exists("classified_urls.csv"):
            tk.Toplevel.__init__(self, *args, **kwargs)
            self.classified_urls = pd.read_csv('classified_urls.csv')
            self.title("Классифицированные ссылки")
            self.geometry("500x400")
            self.model = Model.Model("model", "vect")

            # создание таблицы для отображения классифицированных URL-адресов
            self.table_frame = tk.Frame(self, bg='#F0F0F0', bd=2, relief=tk.GROOVE)
            self.table_frame.pack(pady=(10, 20))

            self.table_label = tk.Label(self.table_frame, text="История классифицированных ссылок", bg='#F0F0F0', fg='#333333',
                                        font=('Arial', 12, 'bold'))
            self.table_label.pack()

            self.table = tk.Label(self.table_frame, text="", bg='#F0F0F0', fg='#333333', font=('Arial', 12), justify='left')
            self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.table.configure(text=self.classified_urls.to_string(index=False, max_colwidth=30))

            # Создание кнопки "Clear history"
            self.clear_button = tk.Button(self, text="Очистить историю", command=self.clear_history, bg='white',activebackground='#8FC2E5', fg='#333333', activeforeground='#333333',font=('Arial', 12, 'bold'))
            self.clear_button.place(x=160, y=250)

            # Создание кнопки "Назад"
            self.back_button = tk.Button(self, text="Назад", command=self.back, bg='white',activebackground='#8FC2E5', fg='#333333', activeforeground='#333333',font=('Arial', 12, 'bold'))
            self.back_button.place(x=210, y=300)
        else:
            tk.messagebox.showerror(title="Error", message="Файл пустой")
            app = Main()
            app.grab_set()

    def clear_history(self):
        # Очистка истории классифицированных URL- адресов
        try:
            os.remove('classified_urls.csv')
            self.table.configure(text="")
        except OSError:
            tk.messagebox.showerror(title="Error", message="Файл и так пустой.")

    def back(self):
        self.destroy()
        app = Main()
        app.grab_set()



if __name__ == "__main__":
     app = Main()
     app.mainloop()

