import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Load dataset
df = pd.read_csv("C:/Users/Prasad Patil/Downloads/e_waste_prices.csv")

# One-hot encoding categorical columns
encoder = OneHotEncoder(drop="first", sparse_output=False)
categorical_cols = ['Device Type', 'Condition', 'Brand', 'Market Demand']
categoricals = encoder.fit_transform(df[categorical_cols])
categorical_df = pd.DataFrame(categoricals, columns=encoder.get_feature_names_out())

# Combine with numerical features
X = pd.concat([categorical_df, df[['Weight (kg)']]], axis=1)
y = df['Price (₹)']

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the trained model properly
joblib.dump(model, "ewaste_price_model.pkl")

joblib.dump(X_train.columns, "model_columns.pkl")  # Save column names for later use


print("✅ Model trained and saved successfully!")
