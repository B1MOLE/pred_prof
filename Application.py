import tkinter.messagebox as messagebox
import tkinter as tk
from tkinter import Menu, filedialog
import pandas as pd
import os
import Model


class Application:
    def __init__(self, master):
        self.master = master
        self.master.title("URL Classifier")             # Название окна
        self.master.configure(background='#F0F0F0')     # Цвет фона

        self.model = Model.Model("model", "vect")

        # Создание меню
        menu_bar = Menu(self.master)
        self.master.config(menu=menu_bar)

        # Создание подменю "File"
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Classify URL", command=self.classify_url)
        file_menu.add_command(label="Clear History", command=self.clear_history)
        file_menu.add_command(label="Classify URLs from CSV", command=self.classify_urls_from_csv)
        file_menu.add_command(label="Exit", command=self.master.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Создание заголовка приложения
        self.title_label = tk.Label(self.master, text="URL Classifier", bg='#F0F0F0', fg='#333333',
                                    font=('Arial', 24, 'bold'))
        self.title_label.pack(pady=(20, 10))

        # Создание фрейма для UI-элементов
        self.frame = tk.Frame(master, bg='#F0F0F0', pady=20, padx=20)
        self.frame.pack()

        # Создание метки для ввода URL
        self.url_label = tk.Label(self.frame, text="Enter a URL:", bg='#F0F0F0', fg='#333333',
                                  font=('Arial', 16))
        self.url_label.pack(pady=(10, 5))

        # Создание поля для ввода URL
        self.url_entry = tk.Entry(self.frame, width=40, font=('Arial', 16))
        self.url_entry.pack()

        # Создание кнопки "Classify URL"
        self.classify_button = tk.Button(self.frame, text="Classify URL", command=self.classify_url, bg='#B7D1E2',
                                         activebackground='#8FC2E5', fg='#333333', activeforeground='#333333',
                                         font=('Arial', 16, 'bold'))
        self.classify_button.pack(pady=(20, 10))

        # Создание кнопки "Classify URLs from CSV"
        self.classify_button_csv = tk.Button(self.frame, text="Classify URLs from CSV", command=self.classify_urls_from_csv, bg='#B7D1E2',
                                         activebackground='#8FC2E5', fg='#333333', activeforeground='#333333',
                                         font=('Arial', 16, 'bold'))
        self.classify_button_csv.pack(pady=(5, 10))

        # создание таблицу для отображения классифицированных URL-адресов
        self.table_frame = tk.Frame(self.frame, bg='#F0F0F0', bd=2, relief=tk.GROOVE)
        self.table_frame.pack(pady=(0, 20))

        self.table_label = tk.Label(self.table_frame, text="History of Classified URLs", bg='#F0F0F0', fg='#333333',
                                    font=('Arial', 12, 'bold'))
        self.table_label.pack()

        self.table = tk.Label(self.table_frame, text="", bg='#F0F0F0', fg='#333333', font=('Arial', 12), justify='left')
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Создание кнопки "Clear history"
        self.clear_button = tk.Button(self.frame, text="Clear History", command=self.clear_history, bg='#B7D1E2',
                                      activebackground='#8FC2E5', fg='#333333', activeforeground='#333333',
                                      font=('Arial', 12, 'bold'))
        self.clear_button.pack(pady=(20, 0))

    def classify_url(self):
        url = self.url_entry.get()
        category = self.model.execute_model(url)

        # Сохранение URL и категорию в файл CSV
        df = pd.DataFrame({'URL': [url], 'Category': [category]})
        df.to_csv('classified_urls.csv', mode='a', header=not os.path.exists('classified_urls.csv'), index=False)

        self.url_entry.delete(0, tk.END)

        # Обновление таблицы с классифицированными URL-адресами
        classified_urls = pd.read_csv('classified_urls.csv')
        self.table.configure(text=classified_urls.to_string(index=False))

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
            self.table.configure(text=classified_urls.to_string(index=False))

    def clear_history(self):
        # Очистка истории классифицированных URL- адресов
        try:
            os.remove('classified_urls.csv')
            self.table.configure(text="")
        except OSError:
            tk.messagebox.showerror(title="Error", message="An error occurred while attempting to clear the history.")


if __name__ == '__main__':
    # Создание окна
    root = tk.Tk()
    app = Application(root)
    root.mainloop()


