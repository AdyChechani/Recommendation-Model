import os
import pandas as pd
from pymongo import MongoClient
import json
import pickle

import SearchSimilar
import DescriptionModel
import PopularProducts
import CategoryBased


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

#########################

data = database_extraction()

popular = PopularProducts.Recommender(data)
search = SearchSimilar.Recommender(data)
description_model = DescriptionModel.Recommender(data)
category_based = CategoryBased.Recommender(data)

#########################

def get_recommendations(choice):
    if choice == 'POPULAR':
        recommendations = {
            'type': 'popular products',
            'result': popular.productIds()
        }

        return recommendations
    

    elif choice == 'SEARCH':
        what = input('what do you want to search? ')

        recommendations = {
            'type': 'searched products',
            'product_name': what,
            'result': search.productIds(what)
        }

        return recommendations
    

    elif choice == 'SUMMARY BASED':
        productId = input('Input the product ID: ')

        recommendations = {
            'type': 'summary based recommendations',
            'product_id': productId,
            'result': description_model.productIds(productId)
        }

        return recommendations
    

    elif choice == 'CATEGORY BASED':
        productId = input('Input the product ID: ')

        recommendations = {
            'type': 'summary based recommendations',
            'product_id': productId,
            'result': category_based.productIds(productId)
        }

        return recommendations
    

    else:
        print('Sorry, we dont provide this operation yet.')
        return None

#########################

def model():
    os.system('cls')
    print('We provide these operations: ')
    print('1. Search --> Type: search')
    print('2. Product Summary Based Recommendation --> Type: Summary based')
    print('3. Most Popular Products --> Type: Popular')
    print('4. Category Based Recommendation --> Type: Category Based')
    print()
    print('type "exit" to exit the program')
    print()

    while True:
        choice = input('Type the operation name you want to perform: ').upper()

        if choice == 'EXIT':
            break
        
        result = get_recommendations(choice)

        if result == None:
            continue

        file_path = 'recommendations.json'

        existing_data = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                existing_data = json.load(json_file)

            existing_data.append(result)
            
            with open(file_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=2)

        else:
            with open(file_path, 'w') as json_file:
                json.dump([result], json_file, indent=2)
        
        print('Recommendations appended to recommendations.json\n\n')
    return

if __name__ == '__main__':
    model()