import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os
import Model

class Main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Классификатор")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (500 // 2)  # 500 is the width of the window
        y = (screen_height // 2) - (300 // 2)  # 300 is the height of the window
        self.geometry("500x300+{}+{}".format(x, y))

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
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (500 // 2)  # 500 is the width of the window
        y = (screen_height // 2) - (300 // 2)  # 300 is the height of the window
        self.geometry("500x300+{}+{}".format(x, y))
        self.model = Model.Model("model", "vect")

        self.label1 = tk.Label(self, text='Введите URL для классификации', font=('Arial', 12))
        self.label1.place(x=125, y=30)

        self.url_entry = tk.Entry(self, width=20, font=('Arial', 12))
        self.url_entry.place(x=150, y=80)

        self.button1 = tk.Button(self, text='Классифицировать', command=self.classify_url, font=('Arial', 12))
        self.button1.place(x=165, y=130)

        self.button2 = tk.Button(self, text='Классифицировать ссылки из CSV файла', command=self.classify_urls_from_csv,
                                 font=('Arial', 12))
        self.button2.place(x=90, y=180)

        self.button3 = tk.Button(self, text='Назад', command=self.back, font=('Arial', 12))
        self.button3.place(x=210, y=230)

    def classify_url(self):
        url = self.url_entry.get()
        category = self.model.predict_class(url)
        probability = self.model.predict_probability(url)
        probability = (probability * 100)

        # Сохранение URL и категорию в файл CSV
        df = pd.DataFrame({'URL': [url], 'Category': [category], 'Probability': [probability]})
        df.to_csv('classified_urls.csv', mode='a', header=not os.path.exists('classified_urls.csv'), index=False)

        self.url_entry.delete(0, tk.END)

        # Обновление таблицы с классифицированными URL-адресами
        classified_urls = pd.read_csv('classified_urls.csv')
        tk.messagebox.showinfo(title="Классификация URL", message="Класс этой ссылки: " + " " + category + " " + "с точностью" + " " + str(probability) + "%")

    def classify_urls_from_csv(self):
        csv_file_path = filedialog.askopenfilename(title="Select CSV file")
        if csv_file_path:
            classified_urls = pd.read_csv(csv_file_path)
            data = []
            for row in classified_urls.itertuples(index=False):
                url = row[0]
                category = self.model.predict_class(url)
                probability = self.model.predict_probability(url)
                probability = (probability * 100)
                data.append((url, category, probability))

            # Сохранение URL и категорию в файл CSV
            df = pd.DataFrame(data, columns=['URL', 'Category', 'Probability'])
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
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width // 2) - (500 // 2)  # 500 is the width of the window
            y = (screen_height // 2) - (300 // 2)  # 300 is the height of the window
            self.geometry("500x300+{}+{}".format(x, y))
            self.model = Model.Model("model", "vect")

            # создание таблицы для отображения классифицированных URL-адресов
            self.table_frame = tk.Frame(self, bg='#F0F0F0', bd=1, relief=tk.GROOVE)
            self.table_frame.pack(pady=(1, 1))

            self.table_label = tk.Label(self.table_frame, text="История классифицированных ссылок", bg='#F0F0F0', fg='#333333',
                                        font=('Arial', 12, 'bold'))
            self.table_label.pack()

            self.table_scrollbar = tk.Scrollbar(self.table_frame)
            self.table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.table = tk.Text(self.table_frame, bg='#F0F0F0', fg='#333333', font=('Arial', 12), wrap=tk.WORD, yscrollcommand=self.table_scrollbar.set, height=7)
            self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.table.configure(state=tk.NORMAL)
            self.table.insert(tk.END, self.classified_urls.to_string(index=False, max_colwidth=30))
            self.table.configure(state=tk.DISABLED)

            self.table_scrollbar.config(command=self.table.yview)

            # Установка выравнивания текста в столбцах
            self.table.tag_configure('col1', justify='left')
            self.table.tag_configure('col2', justify='center')
            self.table.tag_configure('col3', justify='right')

            # Вставка содержимого таблицы в виде строк
            for row in self.classified_urls.to_numpy():
                self.table.insert(tk.END, '{:<30} {:^30} {:>30}\n'.format(*row), ('col1', 'col2', 'col3'))

            # Создание кнопки "Clear history"
            self.clear_button = tk.Button(self, text="Очистить историю", command=self.clear_history, font=('Arial', 12))
            self.clear_button.place(x=170, y=180)

            # Создание кнопки "Назад"
            self.button3 = tk.Button(self, text='Назад', command=self.back, font=('Arial', 12))
            self.button3.place(x=210, y=230)
        else:
            tk.messagebox.showerror(title="Error", message="Файл пустой")
            app = Main()
            app.grab_set()

    def clear_history(self):
        # Очистка истории классифицированных URL- адресов
        try:
            os.remove('classified_urls.csv')
            self.table.configure(state=tk.NORMAL)
            self.table.delete('1.0', tk.END)
            self.table.configure(state=tk.DISABLED)
        except OSError:
            tk.messagebox.showerror(title="Error", message="Файл и так пустой")

    def back(self):
        self.destroy()
        app = Main()
        app.grab_set()



if __name__ == "__main__":
     app = Main()
     app.mainloop()

