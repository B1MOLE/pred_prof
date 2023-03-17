from bs4 import BeautifulSoup
import bs4 as bs4
from urllib.parse import urlparse
import requests
import pandas as pd
import spacy as sp


class Parser:
    def visit_url(self, website_url):
        '''
        Посещает URL-адрес. Загрузка контента. Инициализация объекта BeautifulSoup. Методы разбора вызовов. Возврат объекта серии.
        '''
        self.history = []
        content = requests.get(website_url, timeout=20).content

        # lxml is apparently faster than other settings.
        soup = BeautifulSoup(content, features="html.parser")
        result = {
            "website_url": website_url,
            "website_name": self.get_website_name(website_url),
            "website_text": self.get_html_title_tag(soup) + self.get_html_meta_tags(soup) + self.get_html_heading_tags(
                soup) + self.get_text_content(soup)
        }

        # Append to history
        self.history.append({"website_url": website_url, "class": ""})

        # Convert to Series object and return
        return pd.Series(result)

    def get_website_name(self, website_url):
        '''
        Возвращает название страницы"
        '''
        try:
            return "".join(urlparse(website_url).netloc.split(".")[-2])
        except:
            return ""
    def get_html_title_tag(self, soup):
        '''Возвращает текстовое содержимое тега <title> с веб-страницы'''
        try:
            return '. '.join(soup.title.contents)
        except:
            return ""

    def get_html_meta_tags(self, soup):
        '''Возвращает текстовое содержимое тегов <meta>, связанных с ключевыми словами и описанием с веб-страницы.'''
        try:
            tags = soup.find_all(lambda tag: (tag.name == "meta") & (tag.has_attr('name') & (tag.has_attr('content'))))
            content = [str(tag["content"]) for tag in tags if tag["name"] in ['keywords', 'description']]
            return ' '.join(content)
        except:
            return ""
    def get_html_heading_tags(self, soup):
        '''возвращает текстовое содержимое тегов заголовков. Предполагается, что заголовки могут содержать относительно важный текст.'''
        try:
            tags = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            content = [" ".join(tag.stripped_strings) for tag in tags]
            return ' '.join(content)
        except:
            return ""

    def get_text_content(self, soup):
        '''возвращает текстовое содержимое всей страницы с некоторыми исключениями для тегов'''
        tags_to_ignore = ['style', 'script', 'head', 'title', 'meta', '[document]', "h1", "h2", "h3", "h4", "h5", "h6",
                          "noscript"]
        tags = soup.find_all(text=True)
        result = []
        for tag in tags:
            stripped_tag = tag.strip()
            if tag.parent.name not in tags_to_ignore \
                    and isinstance(tag, bs4.element.Comment) == False \
                    and not stripped_tag.isnumeric() \
                    and len(stripped_tag) > 0:
                result.append(stripped_tag)
        return ' '.join(result)


    def clean_text(self, doc):
        '''
        Очистка документа. Удаление местоимения, стоп-слов, лемматизировать слова и сделать их строчными
        '''
        nlp = sp.load("en")
        # output_dir = r"C:\Users\Alexey\PycharmProjects\ml_prof\dist\App"
        # nlp.to_disk(output_dir)
        doc = nlp(doc)
        tokens = []
        exclusion_list = ["nan"]
        for token in doc:
            if token.is_stop or token.is_punct or token.text.isnumeric() or (
                    token.text.isalnum() == False) or token.text in exclusion_list:
                continue
            token = str(token.lemma_.lower().strip())
            tokens.append(token)
        return " ".join(tokens)





