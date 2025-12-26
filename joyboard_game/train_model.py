import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import os

LOG_FILE = "game_log.csv"
MODEL_FILE = "dda_model.pkl"

if not os.path.exists(LOG_FILE):
    print(f"No log found: {LOG_FILE}. Play the game to generate data first.")
    exit(1)

df = pd.read_csv(LOG_FILE)  # header: level,time_taken,health_ratio
df = df.dropna()

if len(df) < 5:
    print("Warning: only", len(df), "rows found. Training may be unstable but will run.")

# higher = better
df['score'] = (df['health_ratio'] * 1000) / (df['time_taken'] + 1)

# Calculate the average score for each level (Expected Performance)
level_performance = df.groupby('level')['score'].median()

# Create the DDA target: Performance Delta
# This is how much better (positive) or worse (negative) the player did
df['expected_score'] = df['level'].apply(lambda x: level_performance.get(x, df['score'].median()))
df['performance_delta'] = df['score'] - df['expected_score']

# Model predicts the DELTA
X = df[['level', 'time_taken', 'health_ratio']]
y = df['performance_delta'] 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

preds = model.predict(X_test)
mse = mean_squared_error(y_test, preds)
print(f"Trained LinearRegression. Test MSE: {mse:.4f}")

joblib.dump(model, MODEL_FILE)
print("Saved model to", MODEL_FILE)