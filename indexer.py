# indexer.py
from text_transformer import TextTransformer
from bson import ObjectId

class Indexer:
    def __init__(self, db):
        self.db = db
        self.pages_col = db['pages']
        self.docs_col = db['documents']
        self.terms_col = db['terms']
        self.text_transformer = TextTransformer()

    def get_documents(self):
        targets = self.pages_col.find({"target": True})

        docs = []
        doc_ids = []
        doc_urls = []

        for target in list(targets):
            if 'parsed_data' in target and 'content' in target['parsed_data']:
                docs.append(target['parsed_data']['content'])
                doc_ids.append(target["_id"])
                doc_urls.append(target["url"])

        return docs, doc_ids, doc_urls

    def create_vectorizer(self):
        return self.text_transformer.create_vectorizer()

    def store_documents(self, doc_ids, docs, urls, tfidf_array):
        for idx, doc in enumerate(docs):
            self.docs_col.update_one(
                {"_id": ObjectId(doc_ids[idx])},
                {
                    "$set": {
                        "content": doc,
                        "tfidf": tfidf_array[idx].tolist(),
                        "url": urls[idx]
                    }
                },
                upsert=True
            )

    def store_terms(self, vectorizer, tfidf_array, doc_ids):
        for term, term_idx in vectorizer.vocabulary_.items():
            doc_list = [
                str(doc_ids[doc_idx])
                for doc_idx, doc in enumerate(tfidf_array)
                if doc[term_idx] > 0
            ]

            self.terms_col.update_one(
                {"term": term},
                {
                    "$set": {
                        "term": term,
                        "pos": term_idx,
                        "idf": float(vectorizer.idf_[term_idx]),
                        "docs": doc_list
                    }
                },
                upsert=True
            )

    def create_index(self):
        docs, doc_ids, doc_urls = self.get_documents()

        if not docs:
            print("No documents found to index")
            return

        vectorizer = self.create_vectorizer()
        tfidf_matrix = vectorizer.fit_transform(docs)
        tfidf_array = tfidf_matrix.toarray()

        self.store_documents(doc_ids, docs, doc_urls, tfidf_array)
        self.store_terms(vectorizer, tfidf_array, doc_ids)

        print(f"Indexed {len(docs)} documents with {len(vectorizer.vocabulary_)} unique terms")