import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import joblib

def train_svm_classifier(X_train, y_train, X_test, y_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)
    svc = SVC(C=1.0, gamma='scale', kernel='rbf', class_weight='balanced', probability=True)
    svc.fit(X_train_scaled, y_train)
    y_pred = svc.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"SVC Accuracy: {accuracy:.4f}")
    print(classification_report(y_test, y_pred, zero_division=0))
    return accuracy, svc, scaler

def train_decision_tree_classifier(X_train, y_train, X_test, y_test):
    clf = DecisionTreeClassifier(max_depth=10, min_samples_split=2, min_samples_leaf=1)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"DecisionTreeClassifier Accuracy: {accuracy:.4f}")
    print(classification_report(y_test, y_pred, zero_division=0))
    return accuracy, clf

def train_random_forest_classifier(X_train, y_train, X_test, y_test):
    clf = RandomForestClassifier(
        n_estimators=50, max_depth=10, min_samples_split=2, min_samples_leaf=1, class_weight='balanced'
    )
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"RandomForestClassifier Accuracy: {accuracy:.4f}")
    print(classification_report(y_test, y_pred, zero_division=0))
    return accuracy, clf


def main(fights, model_path):
    fight_df = pd.read_csv(fights)

    no_draws_df = fight_df[fight_df['red_result'] != 0.5].copy()
    no_draws_df['red_result'] = no_draws_df['red_result'].astype(int)

    X = no_draws_df.drop(columns=['red_result', 'date', 'red', 'blue', 'red_rating', 'blue_rating', 'exp_red_outcome', 'blue_rd', 'red_rd', 'new_red_rating', 'new_blue_rating'])
    y_reg = no_draws_df['red_result']

    print("\n========== CLASSIFICATION (WITHOUT DRAWS) ==========")
    X_train, X_test, y_train, y_test = train_test_split(X, y_reg, test_size=0.2)

    acc_svc, svc, scaler = train_svm_classifier(X_train, y_train, X_test, y_test)
    acc_dtc, dtc = train_decision_tree_classifier(X_train, y_train, X_test, y_test)
    acc_rfc, rfc = train_random_forest_classifier(X_train, y_train, X_test, y_test)

    # Compare and save best classification model
    classifier_results = {
        'svc': (acc_svc, svc, scaler),
        'decision_tree': (acc_dtc, dtc, None),
        'random_forest': (acc_rfc, rfc, None)
    }
    best_name, (best_acc, best_model, best_scaler) = max(classifier_results.items(), key=lambda x: x[1][0])
    print(f"\n Best classifier: {best_name} with accuracy: {best_acc:.4f}")
    joblib.dump((best_model, best_scaler, X.columns.tolist()), f"{model_path}_best_classifier.pkl")


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])