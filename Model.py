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
        dataset = pd.read_csv('website_classification.csv')
        print(dataset.shape)
        df = dataset[['website_url', 'cleaned_website_text', 'Category']].copy()
        df['category_id'] = df['Category'].factorize()[0]

        tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5,
                             ngram_range=(1, 2),
                             stop_words='english')

        # We transform each cleaned_text into a vector
        features = tfidf.fit_transform(df.cleaned_website_text).toarray()

        labels = df.category_id

        X = df['cleaned_website_text']  # Collection of text

        X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(features,labels,
                                                                                      df.index, test_size=0.25,
                                                                                      random_state=1)
        model = LinearSVC()
        model.fit(X_train, y_train)
        calibrated_svc = CalibratedClassifierCV(estimator=model, cv="prefit")

        calibrated_svc.fit(X_train, y_train)

        model.fit(features, labels)

        X_train, X_test, y_train, y_test = train_test_split(X, df['category_id'], test_size=0.25, random_state=0)

        tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, ngram_range=(1, 2), stop_words='english')

        fitted_vectorizer = tfidf.fit(X_train)
        tfidf_vectorizer_vectors = fitted_vectorizer.transform(X_train)

        m = LinearSVC().fit(tfidf_vectorizer_vectors, y_train)
        m1 = CalibratedClassifierCV(estimator=m, cv="prefit").fit(tfidf_vectorizer_vectors, y_train)

        filename = 'model'
        filename_vector = 'vect'

        pickle.dump(m1, open(filename, 'wb'))
        pickle.dump(fitted_vectorizer, open(filename_vector, 'wb'))

    def execute_model(self, website):
        """
        Использование модели для классфикации ссылок
        """
        filename = 'model'
        filename_vect = 'vect'
        m1 = pickle.load(open(filename, 'rb'))
        fitted_vectorizer = pickle.load(open(filename_vect, 'rb'))

        parser = Parser.Parser()

        web = dict(parser.visit_url(website))
        text = (parser.clean_text(web['website_text']))
        t = fitted_vectorizer.transform([text])
        data = pd.DataFrame(m1.predict_proba(t) * 100,
                            columns=['Travel', 'Social Networking and Messaging', 'News', 'Streaming Services',
                                     'Sports', 'Photography', 'Law and Government', 'Health and Fitness', 'Games',
                                     'E-Commerce', 'Food', 'Education', 'Computers and Technology',
                                     'Business/Corporate'])
        data = data.T
        data.columns = ['Probability']
        data.index.name = 'Category'
        a = data.sort_values(['Probability'], ascending=False)
        a['Probability'] = a['Probability'].apply(lambda x: round(x, 2))

        # Update history with class prediction
        class_pred = a.index[0]

        return class_pred

