from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Recommender():
    '''
    It takes product name as input, and returns product_id of top 20 similar product

    It uses cosine similarity to find most similar product names
    '''
    def __init__(self, data) -> None:
        self.data = data

    def productIds(self, productName):
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(self.data['product_name'])
        string_vector = vectorizer.transform([productName])
        
        cosine_sim = cosine_similarity(string_vector, vectors)
        cos = []
        for i in range(len(self.data['product_name'])):
            cos.append(cosine_sim[0][i])
        
        cosine_data = self.data
        cosine_data['cosine_similarity'] = cos
        cosine_data = cosine_data.sort_values(by=['cosine_similarity'], ascending=False)
        return(cosine_data['product_id'].head(20).tolist())