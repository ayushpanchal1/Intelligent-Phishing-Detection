import pandas as pd
from sklearn.model_selection import train_test_split
import joblib
import os
from datetime import datetime

model = joblib.load('/home/tase/Project-Based-Learning/Static/XGB-GSCV-OG.pkl')


dataset = pd.read_csv("/home/tase/Project-Based-Learning/Static/feedback-features.csv")

dataset = dataset.drop(['Domain'], axis = 1)

# print(dataset.info())

X_train = dataset.drop('Label',axis=1)
y_train = dataset['Label']

best_params = {'gamma': 0, 'learning_rate': 0.05, 'max_depth': 8, 'min_child_weight': 1, 'n_estimators': 300}

model.fit(X_train, y_train, xgb_model=model)

source_file = "/home/tase/Project-Based-Learning/Static/XGB-GSCV.joblib"
destination_folder = "/home/tase//Project-Based-Learning/Static"
def move_and_rename_file(source_file, destination_folder):
  current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  filename, extension = os.path.splitext(os.path.basename(source_file))
  new_filename = f"{current_datetime}-{filename}{extension}"
  destination_path = os.path.join(destination_folder, new_filename)
  try:
    os.rename(source_file, destination_path)
    print(f"File moved and renamed to: {destination_path}")
  except OSError as e:
    print(f"Error moving file: {e}")
move_and_rename_file(source_file, destination_folder)

joblib.dump(model, '/home/tase/Project-Based-Learning/Static/XGB-GSCV.joblib')

def clear_csv_content():
  with open('/home/tase/Project-Based-Learning/Static/feedback.csv', 'w') as csvfile:
    pass  # Empty the file by writing nothing
clear_csv_content()