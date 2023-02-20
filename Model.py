import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
import Parser


class Model:
    def create_model(self):
        """
        Создание модели
        """
        dataset = pd.read_csv('website_classification.csv')   # чтение данных из CSV файла с помощью Pandas
        df = dataset[['website_url', 'cleaned_website_text', 'Category']].copy()   # создание DataFrame с нужными столбцами
        df['category_id'] = df['Category'].factorize()[0]   # создание нового столбца с идентификаторами категорий

        tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, ngram_range=(1, 2), stop_words='english')   # создание объекта TfidfVectorizer

        # Преобразуем каждый очищенный текст в вектор
        features = tfidf.fit_transform(df.cleaned_website_text).toarray()   # преобразование текста в векторы признаков
        labels = df.category_id   # определение меток классов

        X = df['cleaned_website_text']   # тексты для обучения
        X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(features, labels, df.index, test_size=0.25, random_state=1)   # разбиение на тренировочную и тестовую выборки

        model = LinearSVC()   # инициализация модели машины опорных векторов
        model.fit(X_train, y_train)   # обучение модели
        calibrated_svc = CalibratedClassifierCV(estimator=model, cv="prefit")   # создание объекта CalibratedClassifierCV для калибровки модели
        calibrated_svc.fit(X_train, y_train)   # обучение модели

        model.fit(features, labels)   # обучение модели на всей выборке

        X_train, X_test, y_train, y_test = train_test_split(X, df['category_id'], test_size=0.25, random_state=0)   # разбиение на тренировочную и тестовую выборки

        tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, ngram_range=(1, 2), stop_words='english')   # создание нового объекта TfidfVectorizer

        # обучение векторайзера на тренировочной выборке
        fitted_vectorizer = tfidf.fit(X_train)
        tfidf_vectorizer_vectors = fitted_vectorizer.transform(X_train)

        # Обучение модели LinearSVC на векторизованных функциях
        m = LinearSVC().fit(tfidf_vectorizer_vectors, y_train)

        # Калибровка модели
        m1 = CalibratedClassifierCV(estimator=m, cv="prefit").fit(tfidf_vectorizer_vectors, y_train)

        # Сохранение модели и векторизатора на диск
        filename = 'model'
        filename_vector = 'vect'
        pickle.dump(m1, open(filename, 'wb'))
        pickle.dump(fitted_vectorizer, open(filename_vector, 'wb'))

    def execute_model(self, website):
        """
        Использование модели для классфикации ссылок
        """
        # Название файлов с сохраненной моделью и векторайзером
        filename = 'model'
        filename_vect = 'vect'
        # Загрузка модели и векторайзера из файлов
        m1 = pickle.load(open(filename, 'rb'))
        fitted_vectorizer = pickle.load(open(filename_vect, 'rb'))

        # Создание экземпляра класса Parser
        parser = Parser.Parser()

        # Получение словаря с данными о веб-странице
        web = dict(parser.visit_url(website))
        # Очистка текста веб-страницы
        text = (parser.clean_text(web['website_text']))
        # Векторизация очищенного текста с помощью векторайзера
        t = fitted_vectorizer.transform([text])
        # Получение вероятности принадлежности к каждому классу с помощью модели
        data = pd.DataFrame(m1.predict_proba(t) * 100,
                            columns=['Travel', 'Social Networking and Messaging', 'News', 'Streaming Services',
                                     'Sports', 'Photography', 'Law and Government', 'Health and Fitness', 'Games',
                                     'E-Commerce', 'Food', 'Education', 'Computers and Technology',
                                     'Business/Corporate'])
        # Транспонирование таблицы с вероятностями и изменение названий столбцов и индекса
        data = data.T
        data.columns = ['Probability']
        data.index.name = 'Category'
        # Сортировка по вероятности в порядке убывания
        a = data.sort_values(['Probability'], ascending=False)
        # Округление вероятностей до 2 знаков после запятой
        a['Probability'] = a['Probability'].apply(lambda x: round(x, 2))

        # Update history with class prediction
        # Получение категории с наибольшей вероятностью принадлежности
        class_pred = a.index[0]

        # Возврат предсказанной категории
        return class_pred

