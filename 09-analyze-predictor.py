"""
Performs model comparison using accuracy results.
- Generates histograms of model accuracy distributions
- Tests normality and runs one-way ANOVA
- Conducts Tukey's post-hoc test for pairwise model comparison
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn
import sys

from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

seaborn.set_theme()

def main(predictor_results):
    df = pd.read_csv(predictor_results)

    # Separate Models (SVM, Decision Tree, Random Forest)
    svm = df[df['name'] == 'svm']['accuracy']
    tree = df[df['name'] == 'tree']['accuracy']
    forest = df[df['name'] == 'forest']['accuracy']

    # Plot histogram of model accuracies
    plt.figure()
    plt.hist(svm, color='r', alpha=0.5)
    plt.hist(tree, color='g', alpha=0.5)
    plt.hist(forest, color='b', alpha=0.5)
    plt.legend(['SVM', 'Tree', 'Forest'])
    plt.xlabel('Accuracy')
    plt.ylabel('Frequency')
    plt.title('Frequency of Model Accuracies')
    plt.savefig('09-model-accuracy.png')

    # Test for normality of accuracy distributions
    print(f'Normal test on SVM Accuracy: {stats.normaltest(svm).pvalue}')
    print(f'Normal test on Tree Accuracy: {stats.normaltest(tree).pvalue}')
    print(f'Normal test on Forest Accuracy: {stats.normaltest(forest).pvalue}')
    print('')

    # Run one-way ANOVA to test if model accuracies differ significantly
    anova = stats.f_oneway(svm, tree, forest)
    print(f'ANOVA p-value: {anova.pvalue}\n')

    # Run Tukey's post-hoc test to identify pairwise differences
    df_melt = pd.melt(pd.DataFrame(
        {'svm': svm.to_list(), 
         'tree': tree.to_list(), 
         'forest': forest.to_list()}
    ))
    posthoc = pairwise_tukeyhsd(df_melt['value'], df_melt['variable'], alpha=0.05)
    print(posthoc)

if __name__ == '__main__':
    main(sys.argv[1])