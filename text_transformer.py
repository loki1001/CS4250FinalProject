# text_transformer.py
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import string


class TextTransformer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def transform_text(self, text):
        regex = re.compile('[%s“”]' % re.escape(string.punctuation))
        text = regex.sub('', text.lower())
        tokens = word_tokenize(text)

        tokens = [token for token in tokens
                  if token not in string.punctuation
                  and token not in self.stop_words]

        return [self.lemmatizer.lemmatize(token) for token in tokens]

    def __call__(self, text):
        return self.transform_text(text)

    def create_vectorizer(self, ngram_range=(1, 3)):
        return TfidfVectorizer(
            analyzer='word',
            stop_words='english',
            ngram_range=ngram_range,
            tokenizer=self
        )