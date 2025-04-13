import matplotlib.pyplot as plt
import pandas as pd
import seaborn
import sys

from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

seaborn.set_theme()

def main(predictor_results):
    df = pd.read_csv(predictor_results)

    # separate models
    svm = df[df['name'] == 'svm']['accuracy']
    nb = df[df['name'] == 'nb']['accuracy']
    forest = df[df['name'] == 'forest']['accuracy']

    # create histogram of model accuracies
    plt.figure()
    plt.hist(svm, color='r', alpha=0.5)
    plt.hist(nb, color='g', alpha=0.5)
    plt.hist(forest, color='b', alpha=0.5)
    plt.legend(['SVM', 'NB', 'Forest'])
    plt.xlabel('Accuracy')
    plt.ylabel('Frequency')
    plt.title('Frequency of Model Accuracies')
    plt.savefig('09-model-accuracy.png')

    # normal test on classifier accuracy
    print(f'Normal test on SVM Accuracy: {stats.normaltest(svm).pvalue}')
    print(f'Normal test on NB Accuracy: {stats.normaltest(nb).pvalue}')
    print(f'Normal test on Forest Accuracy: {stats.normaltest(forest).pvalue}')
    print('')

    anova = stats.f_oneway(svm, nb, forest)
    print(f'ANOVA p-value: {anova.pvalue}\n')

    # tukey posthoc analysis
    df_melt = pd.melt(pd.DataFrame(
        {'svm': svm.to_list(), 
         'nb': nb.to_list(), 
         'forest': forest.to_list()}
    ))
    posthoc = pairwise_tukeyhsd(df_melt['value'], df_melt['variable'], alpha=0.05)
    print(posthoc)

if __name__ == '__main__':
    main(sys.argv[1])