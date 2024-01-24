import findspark
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as cs


findspark.init()

class Recommender():
    def __init__(self, model_data, data_collect, DF_pandas, TDF, RDF):
        self.model_data = model_data
        self.data_collect = data_collect
        self.DF_pandas = DF_pandas
        self.TDF = TDF
        self.RDF = RDF

    def cosine_similarityy(self, X, Y):
        denom = X.norm(2) * Y.norm(2)
        if denom == 0.0:
            return -1.0
        else:
            return X.dot(Y) / float(denom)
    
    def search(self, string):
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(self.DF_pandas['product_name'])
        string_vector = vectorizer.transform([string])
        cosine_sim = cs(string_vector, vectors)
        cos=[]
        for i in range(len(self.DF_pandas['product_name'])):
            cos.append(cosine_sim[0][i])
        self.DF_pandas['cosine_sim'] = cos
        self.DF_pandas = self.DF_pandas.sort_values(by=["cosine_sim"], ascending=False)
        return(self.DF_pandas.head(20))
    
    def Sort(self, sub_li):
        l = len(sub_li)
        for i in range(0, l):
            for j in range(0, l-i-1):
                if (sub_li[j][1] < sub_li[j + 1][1]):
                    tempo = sub_li[j]
                    sub_li[j]= sub_li[j + 1]
                    sub_li[j + 1]= tempo
        return sub_li
    
    def product_name_recommendation(self, x):
        gProd1 = self.model_data.filter(self.model_data['product_id'] == x).collect()[0]
        l = []
        for row in self.data_collect:
            c = self.cosine_similarityy(row['product_nameIDF'], gProd1['product_nameIDF'])
            i = row['product_id']
            l+=[c]
        tit = []
        for i in range(len(self.TDF['product_name'])):
            tit.append(l[i])
        self.TDF['titlesim'] = tit
        TDF1= self.TDF.sort_values(by=["titlesim"], ascending=False)
        TDF1 = TDF1.iloc[1:,:]
        return(TDF1)
    
    def toprated(self, productId): # these are top rated but no the similar products --> make changes here
        return(self.description_recommendation(productId).sort_values(by=["rating"], ascending=False))
    
    def description_recommendation(self, x):
        gProd1 = self.model_data.filter(self.model_data['product_id'] == x).collect()[0]
        l = []
        for row in self.data_collect:
            c = self.cosine_similarityy(row['about_productIDF'], gProd1['about_productIDF'])
            i = row['product_id']
            l+=[(c)]
        rec=[]
        for i in range(len(self.RDF['product_name'])):
            rec.append(l[i])
        self.RDF['sim'] = rec
        RDF1 = self.RDF.sort_values(by=["sim"], ascending=False)
        RDF1=RDF1.iloc[1:,:]
        return(RDF1)
    
    def category_recommendation(self, x):
        gProd1 = self.model_data.filter(self.model_data['product_id'] == x).collect()[0]
        l=[]
        for row in self.data_collect:
            c = self.cosine_similarityy(row['categoryIDF'], gProd1['categoryIDF'])
            i=row['product_id']
            l+=[(c)]
        rec=[]  
        for i in range(len(self.RDF['product_name'])):
            rec.append(l[i])
        self.RDF['sim']=rec
        RDF1 = self.RDF.sort_values(by=["sim"], ascending=False)
        RDF1=RDF1.iloc[1:,:]
        return(RDF1.head(50))