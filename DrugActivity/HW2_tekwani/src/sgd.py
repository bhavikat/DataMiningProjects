from sklearn.feature_selection import VarianceThreshold
import numpy as np
from time import time
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

df_train = pd.read_csv('../data/train.csv', sep='\t', index_col=False, header=None,
                       names=['Active', 'Structure'])


df_test = pd.read_csv('../data/test.csv', sep='\t', index_col=False, header=None,
                       names=['Structure'])


vec = CountVectorizer(binary=True, vocabulary=[str(i) for i in range(100000)])
X_train = vec.fit_transform(df_train['Structure'])
y_train = df_train['Active'].values


X_test = vec.fit_transform(df_test['Structure'])

featurespace_dense_X_train = X_train.toarray()
featurespace_dense_X_test = X_test.toarray()

selector = VarianceThreshold()
vt = selector.fit_transform(X_train)

v = selector.fit(X_train)

start = time()

variance_thresh = 0.04

#feature numbers for the ones that are left

idx = np.where(v.variances_ > variance_thresh)[0]

df_reduced_train = pd.DataFrame(np.nan, index=range(800), columns=idx)
df_reduced_test = pd.DataFrame(np.nan, index=range(350), columns=idx)


def get_value_featurespace(row, column, test_train):
    if test_train == "test":
        return featurespace_dense_X_test[row, column]
    else:
        return featurespace_dense_X_train[row, column]


def populate_df_reduced(row, col, test_train):
    if test_train == "train":
        df_reduced_train.xs(row)[col] = get_value_featurespace(row, col, "train")
    else:
        df_reduced_test.xs(row) [col] = get_value_featurespace(row, col, "test")


def create_new_featurespace():
    for i in range(800):
        for j in idx:
            populate_df_reduced(i, j, "train")
    for i in range(350):
        for j in idx:
            populate_df_reduced(i, j, "test")


#Building the new, reduced featurespace
create_new_featurespace()


clf = SGDClassifier(n_iter=10000, loss='modified_huber', penalty='elasticnet', shuffle=True,
                    class_weight={0:0.1}, alpha=0.07)

clf.fit(df_reduced_train.values, y_train)


y_pred = clf.predict(df_reduced_test.values)
print "Predicted values" , y_pred

np.savetxt('../predictions/sgd_predictions_8', y_pred, fmt='%i')

print ("Finished classifying 350 drugs in: ", (time() - start))


#
# print "Reduced features_ train: ", df_reduced_train
# print "Reduced features test: ", df_reduced_test


# print "X_train: ", X_train
#
# print "X_test: ", X_test
#
# print "Shape of X_train", X_train.shape
#
# print "Shape of X_test", X_test.shape