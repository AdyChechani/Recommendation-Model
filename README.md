# Recommendation-Model
This repository contains a recommendation model developed as part of my internship project. This powerful system is designed to enhance user experience by providing personalized product suggestions based on various factors, including product rating, product category, and product description.

### Prerequisites
- MongoDB
- Python
- Pipenv 

### Installation
1. **Clone this repository to your local machine**
   ```
   git clone https://github.com/AdyChechani/Recommendation-Model.git
   ```
2. **Set and run the environment** <br>
   The following command will automatically install the required libraries for the model, and make a Piplock file
   ```
   pipenv install
   ```
   
   To run the environment run the following command
   ```
   pipenv shell
   ```
3. **Set up the database** <br>
   Open MongoDB compass, and create a new database named ```Source``` and import the ```data.csv``` file under a collection name ```Data```
4. **Run the Data Pipeline** <br>
   Run all the ```.py``` files Data Pipeline directory in the following order:
      ```
      python ExtractData.py
      ```
      ```
      python TransformData.py
      ```
      ```
      python LoadData.py
      ```

   This will clean and load the data into the data warehouse in MonogoDB named ```Warehouse```
6. **Train the model**
  Run the ```model.py``` file. It will train and store the models in Pickle files
   ```
   python model.py
   ```
8. Now run the Flask app, It will start a web page on port ```5000```, then got to ```http://127.0.0.1:5000```
   ```
   python app.py
   ```


### Usage
To integrate this recommendation model into your application, follow these steps:
1. Run the model.py file to create the Pickle files
2. You can use the import the pickled version of the models
   ```
   import pickle

   with open('recommendation_model.pkl', 'rb') as file:
     recommendation_model = pickle.load(file)

   # get the recommendations
   productId = '' # input the product id of the product you want to get recommendations for
   recommendations = recommendation_model.combinedRecommendations(productId) # returns a list of top 20 recommended products
   ```
