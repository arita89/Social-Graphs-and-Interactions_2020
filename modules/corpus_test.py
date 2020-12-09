from nltk import FreqDist
from nltk.corpus import stopwords
from pprint import pprint

from ..modules.own.corpus import corpus

if False:
    import nltk
    nltk.download('stopwords')
    nltk.download('punkt')


# Get song
words = corpus.words('835323.txt')

# Lowercase words
words = [token.lower() for token in words]
# Remove stopwords
words = [w for w in words if not w in stopwords.words()]


print(words)

fc_dc = FreqDist(words)

pprint(dict(fc_dc))
