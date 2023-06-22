import pandas as pd
#import matplotlib.pyplot as plt
#from sklearn import datasets
#from sklearn.model_selection import train_test_split
#from mlxtend.plotting import plot_decision_regions
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier

#
# Load IRIS data set
#
# iris = datasets.load_iris()
# X = iris.data[:, 2:]
# y = iris.target
data = pd.read_csv("merged_data.csv")#,  usecols = ['acc_x_autoregyw_1', 'acc_y_autoregyw_1', 'acc_y_entropy', 'acc_x_entropy', 'acc_z_autoregyw_1', 'acc_z_entropy', 'acc_z_skewness_t', 'acc_y_corecoef', 'acc_x_corecoef', 'acc_x_skewness_t', 'acc_y_skewness_t', 'acc_y_autoregburg_4', 'acc_x_top3', 'acc_x_kurtosis_t', 'acc_y_kurtosis_t', 'acc_z_corecoef', 'acc_z_crossco', 'acc_x_autoregburg_4', 'acc_z_autoregburg_4', 'acc_y_top3', 'acc_x_crossco', 'acc_z_mean', 'acc_y_mean', 'acc_x_autoregburg_1', 'acc_y_one_quarter', 'acc_y_mpf1', 'acc_y_stdev', 'acc_z_stdev', 'acc_y_enwacto_5', 'acc_x_mpf1', 'acc_y_enwacto_6', 'acc_x_enwacto_5', 'acc_y_enwacto_7', 'acc_z_enwacto_6', 'acc_y_enwacto_4', 'acc_z_enwacto_5', 'acc_y_enwacto_2', 'acc_x_stdev', 'acc_z_enwacto_7', 'acc_x_enwacto_6', 'name','activity'])
#data = pd.read_csv("merged_data.csv")
# dla 679 jest ok, od 680 liczy w nieskończoność
#data = data1.loc[1:679]
result = data[data["name"].str.contains("kuba")].copy()

result_train = data[data["name"].str.contains("kuba") == False].copy()

result_train.drop('name', axis=1, inplace=True)
result.drop('name', axis=1, inplace=True)

from sklearn.preprocessing import LabelBinarizer
encoder = LabelBinarizer()
encoder.fit(data['activity'].values)

X_train = result_train.iloc[:, :-1].values
y_train = result_train.iloc[:, -1].values


X_test = result.iloc[:, :-1].values
y_test = result.iloc[:, -1].values

#
# Create training/ test data split
#
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1, stratify=y)

#
# Create an instance of Random Forest Classifier
#
forest = RandomForestClassifier(criterion='gini',
                                n_estimators=90,
                                # max_depth=12,
                                random_state=1,
                                n_jobs=6)
#
# Fit the model
#
forest.fit(X_train, y_train)

#
# Measure model performance
#
y_pred = forest.predict(X_test)
print('Accuracy: %.3f' % accuracy_score(y_test, y_pred))
for i in range(5):
    print(f"ma byc: {y_test[i]}, a jest: {y_pred[i]}")

from sklearn.metrics import accuracy_score, confusion_matrix
# import seaborn as sns
import matplotlib.pyplot as plt
print('-'*10)
score = forest.score(X_test, y_test)
y_eval = forest.predict(X_test)
print('Accuracy', score)
confusion_mat = confusion_matrix(y_test, y_eval)
plt.imshow( confusion_mat , cmap = 'autumn' , interpolation = 'nearest' )
# sns.heatmap(confusion_mat, annot=True, cmap="Blues")
plt.xlabel("Predicted Labels")
plt.ylabel("True Labels")
plt.show()