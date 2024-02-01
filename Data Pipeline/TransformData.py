import pandas as pd
from datetime import date

file_path = f"extracted_data_{date.today()}.csv"

data = pd.read_csv(file_path)

'''Extract BrandName'''
# Extracting brand name (first word) from the product title
data['BrandName'] = data['product_name'].str.split().str[0]



'''Extract Product Tags'''
# Extract all the category tags:
#   1. Strip all the tags and put them in a single columns
#   2. find what is the maximum number of tags any product has --> (7)
#   3. put every tag in these column if there is no tag at the required column put NaN

category = pd.DataFrame()
data['CategoryTags'] = data['category'].str.split('|')

# Creating separate columns for each tag
max_tags = data['CategoryTags'].apply(len).max()
for i in range(max_tags):
    data[f'CategoryTag_{i+1}'] = data['CategoryTags'].str[i] if i < max_tags else None

data = data.drop(columns=['CategoryTags'])



'''Clean the numerical data'''
cat_data = ['discounted_price', 'actual_price', 'discount_percentage', 'rating_count']
replace_dict = {'₹': '', ',': '', '%': ''}

data[cat_data] = data[cat_data].replace(replace_dict, regex=True)

data['rating_count'] = data['rating_count'].astype(float)
data['rating_count'] = pd.DataFrame(data['rating_count'].fillna(data['rating_count'].median()))
data['rating'] = pd.DataFrame(data['rating'].fillna(data['rating'].median()))


'''
Some products reviews are duplicated in the dataset, but have reviews by different people,
saving the product which has higher rating
'''
data = data.sort_values('rating', ascending=False)
data = data.drop_duplicates('product_id', keep='first')


'''Store Data in different Tables'''
# Create all the tables:
MetaData = pd.DataFrame(data[['product_id', 'BrandName', 'product_name', 'img_link', 'product_link']])
Tags = pd.DataFrame(data[['CategoryTag_1', 'CategoryTag_2', 'CategoryTag_3', 'CategoryTag_4', 'CategoryTag_5', 'CategoryTag_6', 'CategoryTag_7']])
PriceAndRating = pd.DataFrame(data[['discounted_price', 'actual_price', 'discount_percentage', 'rating', 'rating_count']])
UserDetail = pd.DataFrame(data[['user_id', 'user_name']])
Reviews = pd.DataFrame(data[['review_id', 'review_title', 'review_content', 'about_product']])

# store in csv format
MetaData.to_csv('MetaData.csv',index=False)
print('Saved meta data to MetaData.csv')

Tags.to_csv('Tags.csv',index=False)
print('Saved category tags to Tags.csv')

PriceAndRating.to_csv('PriceAndRating.csv',index=False)
print('Saved ratings to PriceAndRating.csv')

UserDetail.to_csv('UserDetail.csv',index=False)
print('Saved user info to UserDetails.csv')

Reviews.to_csv('Reviews.csv',index=False)
print('Saved reviews to Reviews.csv')
