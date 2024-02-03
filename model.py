import pandas as pd
from pymongo import MongoClient
import pickle

from recommendation_model.Search import Search
from recommendation_model.PopularProducts import PopularProducts
from recommendation_model.CategoryBased import CategoryBasedRecommendation
from recommendation_model.DescriptionModel import DescriptionBasedRecommendation

class Recommendation(): # combined both Category and Description based model
    '''
    The ultimate recommendation model which combines the recommendations given by the category and description based models.

    The combination is based on a weighted sum of the positions of the products where they are located in the recommendation list:
    Combined Score = (Category Score * category_weight) + (Desciption Score * description_weight)

    for example, our dataset contains product_id = [1,2,3,4,5,6]
    and category based recommendations = [4,5,2], and description model = [3,2,5]
    
    calulating the combined score for every recommended product in both the lists:
    for product 2 -> at position 3 in category based -> and at position 2 in description based:
        combined score = (3 * 0.7) + (2 * 0.3) = 2.7
    
    then return top 20 combined scores
    '''
    def __init__(self, data, category_weight=0.5, description_weight=0.5, top_n=20):
        self.category_weight = category_weight
        self.description_weight = description_weight
        self.top_n = top_n

        self.category_model = CategoryBasedRecommendation(data)
        self.description_model = DescriptionBasedRecommendation(data)

    def combinedRecommendations(self, productId):
        category_recommendations = self.category_model.productIds(productId)
        description_recommendations = self.description_model.productIds(productId, top_n=self.top_n)

        # Combine recommendations with weights
        combined_recommendations = {}
        for product_id in set(category_recommendations + description_recommendations):
            category_score = category_recommendations.index(product_id) + 1 if product_id in category_recommendations else self.top_n + 1
            description_score = description_recommendations.index(product_id) + 1 if product_id in description_recommendations else self.top_n + 1
            combined_score = self.category_weight * category_score + self.description_weight * description_score
            combined_recommendations[product_id] = combined_score

        # Sorting the combined recommendations by combined scores
        sorted_combined_recommendations = sorted(combined_recommendations.items(), key=lambda x: x[1])

        top_combined_recommendations = [product_id for product_id, _ in sorted_combined_recommendations[:self.top_n]]

        return top_combined_recommendations

#####################

def database_extraction():
    mongo_uri = 'mongodb://localhost:27017/Warehouse' # connection string
    collections = ['Tags', 'UserDetail', 'Reviews', 'MetaData', 'PriceAndRating'] # importing all these collections
    client = MongoClient(mongo_uri)

    data_dict = {}
    for collection_name in collections:
        collection = client['Warehouse'][collection_name]
        data_list = list(collection.find())
        data_dict[collection_name] = data_list
    client.close()
    dfs = {key: pd.DataFrame(value) for key, value in data_dict.items()}
    combined_df = pd.concat(dfs.values(), axis=1)
    combined_df = combined_df.drop(['_id'], axis=1)
    columns_to_keep = ['product_id', 'user_id', 'user_name', 'review_id', 'review_title', 
                       'review_content','BrandName', 'product_name', 'img_link', 'product_link',
                       'discounted_price', 'actual_price', 'discount_percentage', 'rating',
                       'rating_count', 'CategoryTag_1', 'CategoryTag_2', 'CategoryTag_3', 
                       'CategoryTag_4', 'CategoryTag_5', 'CategoryTag_6', 'CategoryTag_7', 'about_product']
    data = combined_df[columns_to_keep]
    category_columns = ['CategoryTag_1', 'CategoryTag_2', 'CategoryTag_3', 'CategoryTag_4', 'CategoryTag_5', 'CategoryTag_6', 'CategoryTag_7']
    data['category'] = data[category_columns].apply(lambda row: '|'.join(row.dropna().astype(str)), axis=1)
    data = data.drop(category_columns, axis=1)
    return data

#####################

data = database_extraction()

recommendation_model = Recommendation(data=data,
                                      category_weight=0.8, 
                                      description_weight=0.4, top_n=20)
with open('recommendation_model.pkl', 'wb') as file:
    pickle.dump(recommendation_model, file)


search = Search(data=data)
with open('search.pkl', 'wb') as file:
    pickle.dump(search, file)

popular = PopularProducts(data=data)
with open('popular_products.pkl', 'wb') as file:
    pickle.dump(popular, file)