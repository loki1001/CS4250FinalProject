# search_engine.py
import time
from text_transformer import TextTransformer
from sklearn.metrics.pairwise import cosine_similarity
from bson.objectid import ObjectId

class SearchEngine:
    def __init__(self, db):
        self.db = db
        self.terms_col = db['terms']
        self.docs_col = db['documents']
        self.pages_col = db['pages']
        self.text_transformer = TextTransformer()
        self.page_size = 5
        self.snippet_size = 100

    def preprocess_query(self, query):
        return self.text_transformer.transform_text(query)

    def get_matching_terms(self, query_terms):
        return list(self.terms_col.find({"term": {"$in": query_terms}}))

    def build_query_vector(self, query_terms, term_info):
        query_vector = []
        doc_ids = set()

        for term in term_info:
            tf = query_terms.count(term['term']) / len(query_terms)
            idf = float(term['idf'])
            query_vector.append(tf * idf)
            doc_ids.update([ObjectId(doc_id) for doc_id in term['docs']])

        return query_vector, doc_ids

    def build_doc_vectors(self, docs, term_info):
        return [[doc['tfidf'][term['pos']] for term in term_info] for doc in docs]

    def find_snippet(self, content, query_terms):
        content_lower = content.lower()

        best_pos = -1
        for term in query_terms:
            pos = content_lower.find(term.lower())
            if pos != -1 and (best_pos == -1 or pos < best_pos):
                best_pos = pos

        if best_pos == -1:
            return content[:200] + "..."

        start = max(0, best_pos - self.snippet_size)
        end = min(len(content), best_pos + self.snippet_size)

        snippet = content[start:end]

        snippet_lower = snippet.lower()
        highlighted_snippet = snippet
        offset = 0

        for term in query_terms:
            term_lower = term.lower()
            pos = 0
            while True:
                pos = snippet_lower.find(term_lower, pos)
                if pos == -1:
                    break

                original_term = snippet[pos:pos + len(term)]
                highlighted_snippet = (highlighted_snippet[:pos + offset] + "**" + original_term + "**" + highlighted_snippet[pos + len(term) + offset:])
                offset += 4
                pos += len(term)

        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(content) else ""

        return prefix + highlighted_snippet + suffix

    def format_results(self, docs, similarities, query_terms):
        results = []
        for doc, score in zip(docs, similarities):
            if score > 0:
                page = self.pages_col.find_one({"_id": doc["_id"]})
                if page:
                    snippet = self.find_snippet(doc['content'], query_terms)
                    results.append({
                        'url': doc['url'],
                        'name': page['parsed_data']['name'],
                        'email': page['parsed_data']['email'],
                        'snippet': snippet,
                        'score': round(score * 100, 2)
                    })
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def search(self, query):
        start_time = time.time()

        query_terms = self.preprocess_query(query)
        if not query_terms:
            return []

        term_info = self.get_matching_terms(query_terms)
        if not term_info:
            return []

        query_vector, doc_ids = self.build_query_vector(query_terms, term_info)
        docs = list(self.docs_col.find({"_id": {"$in": list(doc_ids)}}))
        if not docs:
            return []

        doc_vectors = self.build_doc_vectors(docs, term_info)
        similarities = cosine_similarity([query_vector], doc_vectors)[0]

        results = self.format_results(docs, similarities, query_terms)
        search_time = round(time.time() - start_time, 2)

        return results, search_time

    def display_results(self, results, query, search_time):
        total_results = len(results)
        print(f"\nFound {total_results} results for '{query}' in {search_time}s")

        page = 1
        while True:
            start_idx = (page - 1) * self.page_size
            end_idx = start_idx + self.page_size
            page_results = results[start_idx:end_idx]

            if not page_results:
                break

            print(f"\n--- Page {page} ---")
            for i, result in enumerate(page_results, 1):
                print(f"\n{i + start_idx}. {result['name']} - {result['email']} ({result['score']}% match)")
                print(f"URL: {result['url']}")
                print(f"Summary: {result['snippet']}")

            if len(results) <= end_idx:
                break

            next_page = input("\nPress 'n' for next page, any other key for new search: ")
            if next_page.lower() != 'n':
                break
            page += 1