import json
import recommendation_model as RecMod

import os
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import monotonically_increasing_id, lit
from pymongo import MongoClient
from pyspark.ml.feature import RegexTokenizer, StopWordsRemover, CountVectorizer, IDF
from pyspark.ml import Pipeline


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
    combined_df.head()
    x = combined_df['product_id']
    combined_df = combined_df.drop(['product_id'], axis=1)
    combined_df['product_id'] = x.iloc[:, 0]
    combined_df.columns
    columns_to_keep = ['product_id', 'user_id', 'user_name', 'review_id', 'review_title', 
                       'review_content','BrandName', 'product_name', 'img_link', 'product_link',
                       'discounted_price', 'actual_price', 'discount_percentage', 'rating',
                       'rating_count', 'CategoryTag_1', 'CategoryTag_2', 'CategoryTag_3', 
                       'CategoryTag_4', 'CategoryTag_5', 'CategoryTag_6', 'CategoryTag_7', 'about_product']
    data = combined_df[columns_to_keep]
    category_columns = ['CategoryTag_1', 'CategoryTag_2', 'CategoryTag_3', 'CategoryTag_4', 'CategoryTag_5', 'CategoryTag_6', 'CategoryTag_7']
    data['category'] = data[category_columns].apply(lambda row: '|'.join(row.dropna().astype(str)), axis=1)
    data = data.drop(category_columns, axis=1)
    data.to_csv("data.csv")
    return data

def model_pipeline_transformation(df):
    columns = ['product_name', 'about_product', 'category']
    minDFs = {'product_name':2.0, 'about_product':4.0, 'category':4.0}
    preProcStages = []
    for col in columns:
        regexTokenizer = RegexTokenizer(gaps=False, pattern='\w+', inputCol=col, outputCol=col+'Token')
        stopWordsRemover = StopWordsRemover(inputCol=col+'Token', outputCol=col+'SWRemoved')
        countVectorizer = CountVectorizer(minDF=minDFs[col], inputCol=col+'SWRemoved', outputCol=col+'TF')
        idf = IDF(inputCol=col+'TF', outputCol=col+'IDF') 
        preProcStages += [regexTokenizer, stopWordsRemover, countVectorizer, idf]
    pipeline = Pipeline(stages=preProcStages)
    model = pipeline.fit(df)
    data = model.transform(df)
    data = data.select('product_id', 'product_nameIDF', 'about_productIDF','categoryIDF')
    return data

############

spark = SparkSession.builder.master("local[1]").appName("SparkByExamples.com").getOrCreate()
data = database_extraction()
# data = spark.read.csv('Amazon_Kaggle_Dataset.csv',header=True, inferSchema=True )
data = spark.createDataFrame(data).withColumn("index", lit(1) + monotonically_increasing_id())
modeldata = model_pipeline_transformation(data)
DF_pandas = data.toPandas()
TDF = data.toPandas()
RDF = data.toPandas()
data_collect = modeldata.collect()
recommendor = RecMod.Recommender(model_data=modeldata, data_collect=data_collect,
                                DF_pandas=DF_pandas, TDF=TDF, RDF=RDF)

#############

def search(what):
    result = recommendor.search(what)
    products = result['product_id'].tolist()
    search = {
        'type': 'search results',
        'product_name': what,
        'result': products
    }

    return search

def product_based_recommendation(productId):
    result = recommendor.product_name_recommendation(productId)
    products = result['product_id'].tolist()
    recommendations = {
        'type': 'product based recommendations',
        'product_id': productId,
        'result': products[0:20]
    }
    return recommendations

def summary_based_recommendation(productId):
    result = recommendor.description_recommendation(productId)
    products = result['product_id'].tolist()
    recommendations = {
        'type': 'summary based recommendations',
        'product_id': productId,
        'result': products[0:20]
    }
    return recommendations

def rating_based_recommendation(productId):
    result = recommendor.toprated(productId)
    products = result['product_id'].tolist()
    recommendations = {
        'type': 'rating based recommendation',
        'product_id': productId,
        'result': products[0:20]
    }
    return recommendations

def category_based_recommendation(productId):
    result = recommendor.category_recommendation(productId)
    products = result['product_id'].tolist()
    recommendations = {
        'type': 'category based recommendation',
        'product_id' : productId,
        'result': products[0:20]
    }
    return recommendations



def get_recommendations(choice):
    if choice == 'SEARCH':
        what = input('what do you want to search? ')
        return search(what)
    elif choice == 'PRODUCT BASED':
        productId = input('Input the product ID: ')
        return product_based_recommendation(productId)
    elif choice == 'SUMMARY BASED':
        productId = input('Input the product ID: ')
        return summary_based_recommendation(productId)
    elif choice == 'RATING BASED':
        productId = input('Input the product ID: ')
        return rating_based_recommendation(productId)
    elif choice == 'CATEGORY BASED':
        productId = input('Input the product ID: ')
        return rating_based_recommendation(productId)
    else:
        print('Sorry, we dont provide this operation yet.')
        return None
    

###################

os.system('cls')
print('We provide these operations: ')
print('1. Search --> Type: search')
print('2. Product Based Recommendation --> Type: product based')
print('3. Product Summary Based Recommendation --> Type: Summary based')
print('4. Rating Based Recommendations --> Type: Rating Based')
print('5. Category Based Recommendation --> Type: Category Based')
print()

while True:
    choice = input('Type the operation name you want to perform: ').upper()
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