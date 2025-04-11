import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR, SVC
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import joblib


def to_int(red_result):
    return int(red_result * 2)


def train_svm(X_train, y_train, X_test, y_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    svr = SVR(C=0.1, gamma='scale', kernel='rbf')
    svr.fit(X_train_scaled, y_train)
    y_pred = svr.predict(X_test_scaled)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"SVR MSE: {mse:.4f}, R²: {r2:.4f}")
    return mse, r2, svr


def train_svm_classifier(X_train, y_train, X_test, y_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    svc = SVC(C=1.0, gamma='scale', kernel='rbf', class_weight='balanced')
    svc.fit(X_train_scaled, y_train)
    y_pred = svc.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"SVC Accuracy: {accuracy:.4f}")
    print(classification_report(y_test, y_pred, zero_division=0))
    return accuracy, svc

    fight_df = pd.read_csv(fights)
    # print("Tie count:", (fight_df['red_result'] == 0.5).sum())

    X = fight_df.drop(columns=['red_result', 'date','red','blue', 'exp_red_outcome'])
    y = fight_df['red_result']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    print("\n========== CLASSIFICATION (WITH DRAWS) ==========")
    y_clf = y_reg.apply(to_int)
    X_train, X_test, y_train, y_test = train_test_split(X, y_clf, test_size=0.2, random_state=42)
    train_svm_classifier(X_train, y_train, X_test, y_test)
    train_decision_tree_classifier(X_train, y_train, X_test, y_test)
    train_random_forest_classifier(X_train, y_train, X_test, y_test)


    # Models Without draws
    print("\n========== REGRESSION (WITHOUT DRAWS) ==========")
    no_draws_df = fight_df[fight_df['red_result'] != 0.5].copy()
    no_draws_df['red_result'] = no_draws_df['red_result'].astype(int)

    X = no_draws_df.drop(columns=['red_result', 'date', 'red', 'blue'])
    y_reg = no_draws_df['red_result']
    X_train, X_test, y_train, y_test = train_test_split(X, y_reg, test_size=0.2, random_state=42)
    train_svm(X_train, y_train, X_test, y_test)
    train_decision_tree_regressor(X_train, y_train, X_test, y_test)
    train_random_forest_regressor(X_train, y_train, X_test, y_test)

    print("\n========== CLASSIFICATION (WITHOUT DRAWS) ==========")
    y_clf = y_reg.apply(to_int)
    X_train, X_test, y_train, y_test = train_test_split(X, y_clf, test_size=0.2, random_state=42)

    acc_svc, svc = train_svm_classifier(X_train, y_train, X_test, y_test)
    acc_dtc, dtc = train_decision_tree_classifier(X_train, y_train, X_test, y_test)
    acc_rfc, rfc = train_random_forest_classifier(X_train, y_train, X_test, y_test)

    # Compare and save best classification model
    classifier_results = {
        'svc': (acc_svc, svc),
        'decision_tree': (acc_dtc, dtc),
        'random_forest': (acc_rfc, rfc)
    }
    best_name, (best_acc, best_model) = max(classifier_results.items(), key=lambda x: x[1][0])
    print(f"\n Best classifier: {best_name} with accuracy: {best_acc:.4f}")
    joblib.dump(best_model, f"{model_path}_best_classifier.pkl")


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
