import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
import Parser

class Model:

    def __init__(self, model_filename, vector_filename):
        self.model_filename = model_filename
        self.vector_filename = vector_filename
        try:
            self.model = pickle.load(open(self.model_filename, 'rb'))
            self.fitted_vector = pickle.load(open(self.vector_filename, 'rb'))
        except:
            self.create_model()
            self.model = pickle.load(open(self.model_filename, 'rb'))
            self.fitted_vector = pickle.load(open(self.vector_filename, 'rb'))


    def create_model(self):
        """
        Создание модели
        """
        dataset = pd.read_csv('website_classification.csv')
        dataset['category_id'] = dataset['Category'].factorize()[0]

        tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5,ngram_range=(1, 2),stop_words='english')

        # We transform each cleaned_text into a vector
        features = tfidf.fit_transform(dataset.cleaned_website_text).toarray()
        labels = dataset.category_id
        X = dataset['cleaned_website_text']  # Collection of text
        X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(features,labels,
                                                                                      dataset.index, test_size=0.25,
                                                                                      random_state=1)
        model = LinearSVC()
        model.fit(X_train, y_train)
        calibrated_svc = CalibratedClassifierCV(estimator=model, cv="prefit")

        calibrated_svc.fit(X_train, y_train)

        model.fit(features, labels)

        X_train, X_test, y_train, y_test = train_test_split(X, dataset['category_id'], test_size=0.25, random_state=0)

        fitted_vectorizer = tfidf.fit(X_train)
        tfidf_vectorizer_vectors = fitted_vectorizer.transform(X_train)

        m = LinearSVC().fit(tfidf_vectorizer_vectors, y_train)
        m1 = CalibratedClassifierCV(estimator=m, cv="prefit").fit(tfidf_vectorizer_vectors, y_train)

        pickle.dump(m1, open(self.model_filename, 'wb'))
        pickle.dump(fitted_vectorizer, open(self.vector_filename, 'wb'))

    def predict_class(self, website):
        """
        Использование модели для классификации ссылок и возврат предсказанного класса
        """
        # Использование модели для классификации ссылок
        model = pickle.load(open(self.model_filename, 'rb'))
        fitted_vector = pickle.load(open(self.vector_filename, 'rb'))

        parser = Parser.Parser()

        web = dict(parser.visit_url(website))
        text = (parser.clean_text(web['website_text']))
        t = fitted_vector.transform([text])
        # Получаем вероятности для каждого класса
        proba = model.predict_proba(t)[0]
        # Составляем DataFrame с вероятностями для каждого класса
        data = pd.DataFrame({
            'Category': ['Путешествия', 'Социальные сети', 'Новости', 'Стриминговые сервисы',
                         'Спорт', 'Фотографии', 'Закон и правительство', 'Здоровье и фитнесс', 'Игры',
                         'Электронная коммерция', 'Еда', 'Образование', 'Компьютер и технологии',
                         'Бизнес'],
            'Probability': proba
        })
        # Сортируем по убыванию вероятности
        data = data.sort_values(['Probability'], ascending=False)
        # Округляем вероятности до 2 знаков после запятой
        data['Probability'] = data['Probability'].apply(lambda x: round(x, 2))

        # Обновляем историю с предсказанием класса и его точностью
        class_pred = data.iloc[0]['Category']

        return class_pred

    def predict_probability(self, website):
        """
        Использование модели для классификации ссылок и возврат вероятности предсказанного класса
        """
        # Использование модели для классификации ссылок
        model = pickle.load(open(self.model_filename, 'rb'))
        fitted_vector = pickle.load(open(self.vector_filename, 'rb'))

        parser = Parser.Parser()

        web = dict(parser.visit_url(website))
        text = (parser.clean_text(web['website_text']))
        t = fitted_vector.transform([text])
        # Получаем вероятности для каждого класса
        proba = model.predict_proba(t)[0]
        # Составляем DataFrame с вероятностями для каждого класса
        data = pd.DataFrame({
            'Category': ['Путешествия', 'Социальные сети', 'Новости', 'Стриминговые сервисы',
                         'Спорт', 'Фотографии', 'Закон и правительство', 'Здоровье и фитнесс', 'Игры',
                         'Электронная коммерция', 'Еда', 'Образование', 'Компьютер и технологии',
                         'Бизнес'],
            'Probability': proba})
        # Сортируем по убыванию вероятности
        data = data.sort_values(['Probability'], ascending=False)
        # Округляем вероятности до 2 знаков после запятой
        data['Probability'] = data['Probability'].apply(lambda x: round(x, 2))
        # Обновляем историю с предсказанием класса и его точностью
        class_prob = data.iloc[0]['Probability']

        return class_prob

