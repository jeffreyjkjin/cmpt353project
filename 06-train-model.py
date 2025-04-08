import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
import joblib

# TODO: implement functions for training each model
#       save weights for model and as well training/validation set scores

def stance_to_num(stance):
    if (stance == 'Orthodox'):
        return 0
    return 1

def train_svm(X_train, y_train, X_test, y_test):
    # Scale Data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)  # Fit and transform on training data
    X_test_scaled = scaler.transform(X_test)  # Only transform the test data

    # Prefound best parameters
    best_params = {
        'C': 0.1,
        'gamma': 'scale',
        'kernel': 'rbf'
    }

    svr = SVR(C=best_params['C'], gamma=best_params['gamma'], kernel=best_params['kernel'])
    svr.fit(X_train_scaled, y_train)
    y_pred_svr = svr.predict(X_test_scaled)

    # Calculate the Mean Squared Error
    mse_svr = mean_squared_error(y_test, y_pred_svr)
    print(f"Support Vector Machine (SVM) Mean Squared Error (tuned): {mse_svr}")

    # Calculate the R² score
    r2_svr = r2_score(y_test, y_pred_svr)
    print(f"Support Vector Machine (SVM) R² (tuned): {r2_svr}")

    return mse_svr, r2_svr, svr  # Return the trained model


def main(fights, fighters, model, num_runs):
    # TODO: write a selector to pick which model to train
    #       train the model num_runs times


    fight_df = pd.read_csv(fights)

    fight_df['red_stance'] = fight_df['red_stance'].apply(stance_to_num)
    fight_df['blue_stance'] = fight_df['blue_stance'].apply(stance_to_num)

    X = fight_df.drop(columns=['red_result', 'date','red','blue'])
    y = fight_df['red_result']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    mse_svm, r2_svm, svr = train_svm(X_train, y_train, X_test, y_test)

    joblib.dump(svr, model)




if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])