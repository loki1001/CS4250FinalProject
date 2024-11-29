from sklearn.feature_extraction.text import TfidfVectorizer
import string, re
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://localhost:27017/')
db = client['FinalProject']

pagesCol = db['pages']
docsCol = db['documents']
termsCol = db['terms']

# Fetch target pages
targets = pagesCol.find({ "target": True })

# Define array to store merged document content
docs = []
docIds = []

# Squash content into document strings
for target in list(targets):
    content = ""
    for key, value in target['parsed_data']['sections'].items():
        content += key + " "
        for v in value:
            content += v + " "
    docs.append(content)
    docIds.append(target["_id"])

# Convert to lowercase and strip punctuation
regex = re.compile('[%s]' % re.escape(string.punctuation))
docs = [regex.sub('', doc.lower()) for doc in docs]

# Define vectorizer 
vectorizer  = TfidfVectorizer(analyzer='word', stop_words='english', ngram_range=(1, 3)) # Generate unigrams, bigrams and trigrams
vectorizer.fit(docs)

# Transform documents into tf-idf vectors
docsV = vectorizer.transform(docs).toarray()

# Store IDF values
idf = vectorizer.idf_.tolist()

# Push docs to MongoDB
index = 0
for doc in docs:
    docsCol.insert_one({
        "_id": ObjectId(docIds[index]),
        "content": doc,
        "tfidf": docsV[index].tolist()
    })
    index+=1

# Push terms to MongoDB
for term, idx in vectorizer.vocabulary_.items():
    docList = []
    index = 0
    for doc in docs:
        if term in doc:
            docList.append(docIds[index])
        index+=1
    termsCol.update_one({"term": term}, { "$set": {
        "term": term,
        "pos": idx,
        "idf": idf[idx],
        "docs": docList
    }}, upsert=True)