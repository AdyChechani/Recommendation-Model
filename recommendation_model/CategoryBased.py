import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


class Recommender():
    '''
    This model recommends products based on their categories. 
    Users can input a product and receive recommendations that share similar categories.
    '''
    def __init__(self, data) -> None:
        self.data = data

    def productIds(self, productId):
        df = self.data
        # TF-IDF Vectorization
        tfidf_vectorizer = TfidfVectorizer(stop_words='english', tokenizer=lambda x: x.split('|'))
        tfidf_matrix = tfidf_vectorizer.fit_transform(df['category'])

        top_n = 21 # top 20 products (-1 for removing the product itself)

        # Fit the KNN model
        knn_model = NearestNeighbors(n_neighbors=top_n, metric='cosine')
        knn_model.fit(tfidf_matrix)

        idx = df[df['product_id'] == productId].index[0]
        tfidf_vector = tfidf_vectorizer.transform([df['category'].iloc[idx]])
        _, indices = knn_model.kneighbors(tfidf_vector)
        indices = indices.flatten()[1:]  # Exclude the input product_id
        return df['product_id'].iloc[indices].tolist()