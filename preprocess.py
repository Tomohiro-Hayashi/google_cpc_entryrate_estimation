# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import ipdb
import random
import scipy.special as sp
import sys
from statistics import mean, median, variance, stdev
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pickle

#訓練データ,ユーザー抽出データ、どちらを前処理するのか選ぶ
args = sys.argv
if args[1] == 'train':
    df = pd.read_csv("train/train_1.csv")
    element_df = pd.read_csv("train/train_2.csv")
    hit_data = pd.pivot_table(df, values="hit", index="member_id", columns="page_type").add_suffix('_hit')
    stay_data = pd.pivot_table(df, values="stay", index="member_id", columns="page_type").add_suffix('_stay')
    trajectory_data = pd.pivot_table(df, values="trajectory", index="member_id", columns="page_type").add_suffix('_trajectory')
    data = pd.merge(trajectory_data, hit_data, on = 'member_id')
    data = pd.merge(data, stay_data, on = 'member_id')
    data = pd.merge(data, element_df, on = 'member_id')
    data.to_csv('train/train.csv')
elif args[1] == 'scoring':
    df = pd.read_csv("scoring/scoring_1.csv")
    element_df = pd.read_csv("scoring/scoring_2.csv")
    hit_data = pd.pivot_table(df, values="hit", index="member_id", columns="page_type").add_suffix('_hit')
    stay_data = pd.pivot_table(df, values="stay", index="member_id", columns="page_type").add_suffix('_stay')
    trajectory_data = pd.pivot_table(df, values="trajectory", index="member_id", columns="page_type").add_suffix('_trajectory')
    data = pd.merge(trajectory_data, hit_data, on = 'member_id')
    data = pd.merge(data, stay_data, on = 'member_id')
    data = pd.merge(data, element_df, on = 'member_id')
    data.to_csv('scoring/scoring.csv')
data = data.fillna(0)

##例外処理
data['age'] = data['age'] // 5 *5

##型変換
type_float = [
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
]
type_str = [
    'landing_page_type',
    'pref_id',
    'occupation_id',
    'os',
    'mail_domain_type',
    'age',
]
data[type_float] = data[type_float].astype(float)
data[type_str] = data[type_str].astype(str)

##エンコーディング
object = 'entry_flg'
if args[1] == 'train':
    for name in type_str:
        new_col = name + str('_encode')
        data[new_col] = data.groupby(name)[object].transform('mean')
        table = data[[name, new_col]].drop_duplicates()
        table.to_csv('preprocess/' + new_col + '.csv')
elif args[1] == 'scoring':
    for name in type_str:
        new_col = name + str('_encode')
        table = pd.read_csv('preprocess/' + new_col + '.csv')
        table[name] = table[name].astype(str)
        data[name] = data[name].astype(str)
        data = pd.merge(data, table[[name, new_col]], on = name)

##対数化
for name in type_float:
    data[name] = np.log(data[name] + 1)

##統計量の算出
explain = type_float + [
    'landing_page_type_encode',
    'pref_id_encode',
    'occupation_id_encode',
    'os_encode',
    'mail_domain_type_encode',
    'age_encode',
]

if args[1] == 'train':
    pd.DataFrame({key: max(data[key]) for key in explain},index=[0,]).to_csv('preprocess/max_values.csv')
    pd.DataFrame({key: min(data[key]) for key in explain},index=[0,]).to_csv('preprocess/min_values.csv')
max_values = pd.read_csv('preprocess/max_values.csv')
min_values = pd.read_csv('preprocess/min_values.csv')

##正規化
for name in explain:
    data[name] = ( data[name] - min_values[name][0]) *1.0 /(max_values[name][0]- min_values[name][0])

#データを出力する
if args[1] == 'train':
    explain.append('entry_flg')
    data[explain].to_csv("preprocess/preprocess.csv")
    explain.remove('entry_flg')
    object = 'entry_flg'
    pca = PCA(n_components=20)
    feature = pca.fit(data[explain])
    feature = pca.transform(data[explain])
    feature = pd.DataFrame(feature)
    feature = feature.assign(entry_flg = data[object].tolist())
    plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    plt.plot([0] + list( np.cumsum(pca.explained_variance_ratio_)), "-o")
    plt.xlabel("Number of principal components")
    plt.ylabel("Cumulative contribution rate")
    plt.grid()
    plt.show()
    feature.to_csv("preprocess/preprocess_pca.csv")
    pickle.dump(pca, open('preprocess/pca_model.sav', 'wb'))
    ipdb.set_trace()
elif args[1] == 'scoring':
    data[explain].to_csv("preprocess/preprocess_scoring.csv")
    pca = pickle.load(open('preprocess/pca_model.sav', 'rb'))
    feature = pca.transform(data[explain])
    feature = pd.DataFrame(feature)
    feature.to_csv("preprocess/preprocess_scoring_pca.csv")
