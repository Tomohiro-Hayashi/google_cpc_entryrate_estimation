import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegressionCV
import numpy as np
import ipdb
from sklearn.model_selection import train_test_split
from sklearn import metrics
import matplotlib.pyplot as plt
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE
import sys

#インプット
args = sys.argv
if args[1] == 'normal':
    data = pd.read_csv('preprocess/preprocess.csv')
    explain = [

        'detail_trajectory',
        'edit_hope_trajectory',
        'edit_resume_trajectory',
        'edit_scout_trajectory',
        # 'else_trajectory',
        # 'entry_trajectory',
        'login_trajectory',
        'mypage_consider_trajectory',
        'mypage_index_trajectory',
        'mypage_scout_trajectory',
        'register_trajectory',
        'search_city_trajectory',
        'search_hello_trajectory',
        'search_multi_trajectory',
        'search_other_trajectory',
        'search_pref_trajectory',
        'search_user_trajectory',
        'voice_compa_trajectory',

        'detail_hit',
        'edit_hope_hit',
        'edit_resume_hit',
        'edit_scout_hit',
        # 'else_hit',
        # 'entry_hit',
        'login_hit',
        'mypage_consider_hit',
        'mypage_index_hit',
        'mypage_scout_hit',
        'register_hit',
        'search_city_hit',
        'search_hello_hit',
        'search_multi_hit',
        'search_other_hit',
        'search_pref_hit',
        'search_user_hit',
        'voice_compa_hit',

        'detail_stay',
        'edit_hope_stay',
        'edit_resume_stay',
        'edit_scout_stay',
        # 'else_stay',
        # 'entry_stay',
        'login_stay',
        'mypage_consider_stay',
        'mypage_index_stay',
        'mypage_scout_stay',
        'register_stay',
        'search_city_stay',
        'search_hello_stay',
        'search_multi_stay',
        'search_other_stay',
        'search_pref_stay',
        'search_user_stay',
        'voice_compa_stay',

        'landing_page_type_encode',
        'pref_id_encode',
        'occupation_id_encode',
        'os_encode',
        'mail_domain_type_encode',
        'age_encode',
    ]
elif args[1] == 'pca':
    data = pd.read_csv("preprocess/preprocess_pca.csv")
    explain = [
        '0', '1', '2', '3', '4',
        '5', '6', '7', '8', '9',
        '10', '11', '12', '13', '14',
        '15', '16', '17', '18', '19',
        # '20', '21', '22', '23', '24',
        # '25', '26', '27', '28', '29',
        # '30', '31', '32', '33', '34',
        # '35', '36', '37', '38', '39',
        # '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50',
        # '51', '52', '53', '54',
    ]
object = 'entry_flg'

X_train, X_test = train_test_split(
    data,
    test_size = 0.20
)
sampler = RandomUnderSampler()
# sampler = SMOTE()
X_resampled, y_resampled = sampler.fit_resample(X_train[explain], X_train[object])

# X_resampled, y_resampled = X_train[explain], X_train[object]

#統計モデルの選択
model = LogisticRegressionCV(
    penalty = 'l2', solver = 'lbfgs',
    # penalty = 'l1', solver = 'saga',
    Cs = np.logspace(-10, 10, 100),
    fit_intercept = True,
    cv = 100,##交差検証の回数
    # scoring = 'average_precision',
    scoring = 'roc_auc',
    n_jobs = -1##使用コア数
)

#推定の実行(グリッドサーチ)
model.fit(X_resampled, y_resampled)
print('score', model.score(X_test[explain], X_test[object]))
Y_pred = model.predict(X_test[explain])
Y_actual = X_test[object]
Y_prob = model.predict_proba(X_test[explain])[:,1]

fig = plt.figure()
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(2, 1, 2)
#ROC曲線
fpr, tpr, thresholds_roc = metrics.roc_curve(X_test[object], Y_prob)
auc_roc = metrics.auc(fpr, tpr)
ax1.plot(fpr, tpr, label='Logistic Regression (AUC_ROC = %.2f)'%auc_roc)
ax1.grid(True)
ax1.legend()
##PR曲線
precision, recall, thresholds_pr = metrics.precision_recall_curve(X_test[object], Y_prob)
auc_pr = metrics.auc(recall, precision)
ax2.plot(recall, precision, label='Logistic Regression (AUC_PR = %.2f)'%auc_pr)
ax2.legend()
ax2.grid(True)
plt.show()

##score表示
print('AUC_ROC', auc_roc)
print('AUC_PR', auc_pr)
print('recall', metrics.recall_score(Y_actual, Y_pred))
print('accuracy', metrics.accuracy_score(Y_actual, Y_pred))
print('precision', metrics.precision_score(Y_actual, Y_pred))
print('confusion matrix')
print(metrics.confusion_matrix(Y_actual,Y_pred))
print('logloss', metrics.log_loss(Y_actual,Y_pred))
print('C',model.C_)
print('-------coef-------')
coef = dict(zip(explain, model.coef_.tolist()[0]))
for key in coef:
    print(key, ':', coef[key])
print('------------------')

X_test['Y_prob'] = Y_prob
X_test.to_csv("prediction/試験データ_検証.csv")

##ターゲットユーザーへスコアを書き込む
if args[1] == 'normal':
    target = pd.read_csv("preprocess/preprocess_scoring.csv")
elif args[1] == 'pca':
    target = pd.read_csv("preprocess/preprocess_scoring_pca.csv")
prob = model.predict_proba(target[explain])
target['Y_prob'] = prob[:,1]
target = target.sort_values(by = 'Y_prob', ascending = False)
target.to_csv("prediction/scored_target.csv")

ipdb.set_trace()
