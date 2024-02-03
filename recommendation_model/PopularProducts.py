import pandas as pd

class PopularProducts():
    '''
    The dataset has ratings and rating_counts, but the popularity cannot be defined solely on the basis of ratings only.
    
    I have defined the popular products as the products with good ratings by a large number of people.
    So, weighted_rating = rating * rating_count
    '''

    def __init__(self, data) -> None:
        self.data = data
    
    def productIds(self):
        self.data['weighted_ratings'] = pd.DataFrame(self.data['rating'] * self.data['rating_count'])
        x = self.data.sort_values(by='weighted_ratings', ascending=False) # sorted by the 'weighted_ratings'
        return x['product_id'].head(20).tolist()