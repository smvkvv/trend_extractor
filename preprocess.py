from pymystem3 import Mystem
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords

tokenizer = TweetTokenizer()
m = Mystem()


def preprocess(text):
    def tokeniz(text):
        return ' '.join(tokenizer.tokenize(text.lower()))

    stop_words = set(stopwords.words('russian'))

    def delete_stop_words(text):

        filtered_tokens = []
        for token in text.split():
            if token not in stop_words:
                filtered_tokens.append(token)

        return ' '.join(filtered_tokens)

    def lemmatize_sentence(text):
        lemmas = m.lemmatize(text)
        return "".join(lemmas).strip()

    def symbol_deleting(text):
        alphabet = 'abcdefghijklmnopqrstuvwxyzабвгдежзийклмнопрстуфхцчшщъыьэюя0123456789 '

        text = text.replace("ё", "е")
        words = ''.join([[" ", i][i in alphabet] for i in text]).split()
        return ' '.join(words)

    text = tokeniz(text)
    text = delete_stop_words(text)
    text = symbol_deleting(text)
    text = lemmatize_sentence(text)

    return text


def fill_na(row):
    if isinstance(row['processed'], float):
        return preprocess(row['title'])
    else:
        return row['processed']
