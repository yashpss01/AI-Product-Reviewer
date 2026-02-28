import numpy as np
import pandas as pd

df=pd.read_csv("data/Reviews.csv")

df.drop_duplicates(inplace=True) #if any

df=df.sample(n=15000,random_state=42) #random sampling to reduce dataset size

# removing unwanted fields
df.drop(columns=['HelpfulnessNumerator','HelpfulnessDenominator', 'UserId', 'ProfileName'],inplace=True)

#renaming columns
df.rename(columns={'Score': 'Rating'}, inplace=True)

#creating a sentiment column rating>=4 -> Positive, rating<=2 -> Negative, else Neutral
conditions = [
    (df['Rating'] >= 4),
    (df['Rating'] <= 2)
]
choices = ['Positive', 'Negative']

df['Sentiment'] = np.select(conditions, choices, default='Neutral')


print(df.columns)
print(df.shape)
print(df.head())


df.to_csv('data/cleaned_reviews.csv')
