import os
import json
import pickle
from flask import Flask, request, render_template

from model import Recommendation
from recommendation_model.PopularProducts import PopularProducts
from recommendation_model.Search import Search

app = Flask(__name__)

with open('recommendation_model.pkl', 'rb') as file:
    recommendation_model = pickle.load(file)

with open('search.pkl', 'rb') as file:
    search_model = pickle.load(file)

with open('popular_products.pkl', 'rb') as file:
    popular_model = pickle.load(file)

# saves recommendations in the JSON file named 'recommendations.json'
def save_recommendations(user_input, operation_type, recommendations):
    result = {}
    if operation_type == 'recommendation':
        result = {
            'product_id': user_input,
            'type': operation_type,
            'recommendations': recommendations
        }
    elif operation_type == 'search result':
        result = {
            'product_name': user_input,
            'type': operation_type,
            'recommendations': recommendations
        }
    elif operation_type == 'popular products':
        result = {
            'type': operation_type,
            'recommendations': recommendations
        }

    file_path = 'recommendations.json'

    existing_data = []
    if os.path.exists(file_path): # if the json file already exists, new recommendations will be stored in it
        with open(file_path, 'r') as json_file:
            existing_data = json.load(json_file)
        
        existing_data.append(result)

        with open(file_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=2)
    
    else: # else create a new json file and add the recommendations there
        with open(file_path, 'w') as json_file:
            json.dump([result], json_file, indent=2)
    
    return

# home page
@app.route('/')
def home():
    popular_products = popular_model.productIds()
    save_recommendations(user_input='', operation_type='popular products', recommendations=popular_products)
    return render_template('index.html', popular_products=popular_products)

# result page
@app.route('/recommend', methods=['POST'])
def recommend():
    productId = request.form.get('productId')
    search_input = request.form.get('search_input')
    action = request.form.get('action')

    if action == 'recommendations' and productId:
        recommendations = recommendation_model.combinedRecommendations(productId)
        save_recommendations(user_input=productId, operation_type='recommendation', recommendations=recommendations)
        return render_template('result.html', user_input=productId, recommendations=recommendations, type='Recommendations')
    
    elif action == 'search' and search_input:
        search_result = search_model.productIds(search_input)
        save_recommendations(user_input=search_input, operation_type='search result', recommendations=search_result)
        return render_template('result.html', user_input=search_input, recommendations=search_result, type='Search Results')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)