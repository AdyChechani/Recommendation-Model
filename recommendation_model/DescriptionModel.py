import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Recommender():
    def __init__(self, data) -> None:
        self.data = data
    
    def similarities(self):
        data = self.data
        corpus = [text.lower() for text in data['about_product']]

        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(corpus)

        # cosine similarity
        cosine_similarities = cosine_similarity(tfidf_matrix, tfidf_matrix)

        return cosine_similarities

    def productIds(self, productId, top_n=20): # top_n: how many top product_ids to return
        data = self.data
        idx = data[data['product_id'] == productId].index[0]
        
        cosine_similarities = self.similarities()

        sim_scores = list(enumerate(cosine_similarities[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:(top_n + 1)]
        similar_products = [data['product_id'][i[0]] for i in sim_scores]
        return similar_products