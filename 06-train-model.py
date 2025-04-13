import joblib
import sys
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

def train_svm_classifier(X_train, y_train, X_test, y_test):
    model = make_pipeline(
        StandardScaler(),
        SVC(C=1.0, gamma='scale', kernel='rbf', class_weight='balanced', probability=True)
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    return ['svm', accuracy_score(y_test, y_pred), model]

def train_naive_bayes_classifier(X_train, y_train, X_test, y_test):
    model = make_pipeline(
        StandardScaler(),
        GaussianNB()
    )
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    return ['nb', accuracy_score(y_test, y_pred), model]

def train_random_forest_classifier(X_train, y_train, X_test, y_test):
    model = make_pipeline(
        StandardScaler(),
        RandomForestClassifier(
            n_estimators=50, max_depth=10, min_samples_split=2, min_samples_leaf=1, 
            class_weight='balanced'
        )
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    return ['forest', accuracy_score(y_test, y_pred), model]

def main(fights, model_results, num_runs):
    fight_df = pd.read_csv(fights)

    # remove draws
    fight_df = fight_df[fight_df['red_result'] != 0.5]

    # drop columns that can't be used to train on
    drop_cols = [
        'red_result', 'date', 'red', 'blue', 'red_rating', 'blue_rating', 'blue_rd', 'red_rd', 
        'new_red_rating', 'new_blue_rating'
    ]

    X = fight_df.drop(columns=drop_cols)
    y = fight_df['red_result']

    models = [train_svm_classifier, train_naive_bayes_classifier, train_random_forest_classifier]

    results = []
    for model in models:
        for _ in range(0, int(num_runs)):
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

            results.append(model(X_train, y_train, X_test, y_test))

    # store results in dataframe 
    model_df = pd.DataFrame(results, columns=['name', 'accuracy', 'model'])
    model_df.drop('model', axis=1).to_csv(model_results, index=False)   

    # get best models
    best_model_df = model_df.loc[model_df.groupby('name')['accuracy'].idxmax()]
    best_model_df = best_model_df.reset_index().drop('index', axis=1)

    print("**Best Models**")
    print(best_model_df.drop('model', axis=1))

    # save models
    for _, model in best_model_df.iterrows():
        name = model['name']

        joblib.dump(model['model'], f'{name}.pkl')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])