# -*- coding: utf-8 -*-
"""pa3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xdpfz8G_9MvLJpzkEv7HSgMweE3GfaS2
"""

# Google Colaboratory環境沒有內建keras_bert，需先安裝
!pip install keras_bert

# Commented out IPython magic to ensure Python compatibility.
# 切割train data和test data的套件
from sklearn.model_selection import train_test_split
# Support Vector Classification套件
from sklearn.svm import SVC
# 計算precision, recall, F1-score的套件
from sklearn import metrics
# 將list轉化成numpy array較便於計算
import numpy as np
# 轉成csv用套件
import pandas as pd
# 該套件可借用BERT model parameters架出網路架構執行input
from keras_bert import extract_embeddings
# 讀取自己的Google Drive
from google.colab import drive
drive.mount('/content/drive')
# %cd /content/drive/MyDrive/

# 先建一個空的list: "all_news"
all_news = []

# 對每篇新聞跑迴圈，iterator variable名稱為"txt"，因為有1095篇文件，迴圈跑1095次
for txt in range(1095):
  # "string_news"是用來裝新聞文件用的string，每個迴圈的開始先把"string_news"清空
  string_news = ''
  # 讀取每篇新聞，每篇新聞皆裝在資料夾"PA1-data"，以唯讀方式打開，每篇檔案裝進"doc"變數
  with open(f'PA1-data/{txt+1}.txt', 'r') as doc:
    # 每篇新聞原始檔案皆有"\n"分段(不是以句點分段)，"line"這個iterator variable會讀取每一段
    for line in doc:
      # 把每一段的"\n"刪掉，並加進"string_news"這個string的後面
      string_news = string_news + line.rstrip('\n')
      # 把每個字母通通小寫化
      string_news = string_news.casefold()

  # 最後加進"all_news"這個list
  # 迴圈跑完後，"all_news"裡面有1095個清完資料的strings，只差沒刪stopword
  all_news.append(string_news)

# training_new.txt檔案中的class
training_new_txt = '''1 11 19 29 113 115 169 278 301 316 317 321 324 325 338 341
2 1 2 3 4 5 6 7 8 9 10 12 13 14 15 16
3 813 817 818 819 820 821 822 824 825 826 828 829 830 832 833
4 635 680 683 702 704 705 706 708 709 719 720 722 723 724 726
5 646 751 781 794 798 799 801 812 815 823 831 839 840 841 842
6 995 998 999 1003 1005 1006 1007 1009 1011 1012 1013 1014 1015 1016 1019
7 700 730 731 732 733 735 740 744 752 754 755 756 757 759 760
8 262 296 304 308 337 397 401 443 445 450 466 480 513 533 534
9 130 131 132 133 134 135 136 137 138 139 140 141 142 143 145
10 31 44 70 83 86 92 100 102 305 309 315 320 326 327 328
11 240 241 243 244 245 248 250 254 255 256 258 260 275 279 295
12 535 542 571 573 574 575 576 578 581 582 583 584 585 586 588
13 485 520 523 526 527 529 530 531 532 536 537 538 539 540 541'''
# 以"\n"切分每一列別
training_new_splitN = training_new_txt.split('\n')
# 建立空的lists，等一下會裝東西
training_new_docID, training_new_classID = [], []
# 對每一類別跑迴圈
for line in training_new_splitN:
  # 以空格切割每一文本id
  class_ = line.split(' ')
  # 對單一類別中的每一文本向量跑迴圈。class_[0]是類別的id，文本的id是從class_[1]開始
  for id in class_[1:]:
    # 裝進該文本的所屬類別
    training_new_classID.append(int(class_[0]))
    # 裝進該文本的id
    training_new_docID.append(int(id))

# 先把所有的文本id裝進一個向量
test_new_docID = [id+1 for id in range(1095)]
# 此步驟剔除已為training data的id，剩下的即為需預測的test data之id
for id in training_new_docID:
  test_new_docID.remove(id)

# BERT-Base model資料夾放在Google Drive首頁
model_path = 'uncased_L-12_H-768_A-12'
# 建立embdding
embeddings = extract_embeddings(model_path, all_news)

# 將每個文本的CLS取出，CLS代表該文本的特徵
embeddings_CLS = [embeddings[text_vec][0] for text_vec in range(1095)]
# X為training data向量的numpy array
X = np.array([embeddings_CLS[id-1] for id in training_new_docID])
# y為training data類別的numpy array
y = np.array(training_new_classID)
# test為training data的numpy array
test = np.array([embeddings_CLS[id-1] for id in test_new_docID])

# 設立一個Support Vector Classification
# kernel為linear，以此將資料做非線性轉換
# 用來控制損失函數的懲罰係數C設為1，可限制模型的複雜度，防止過度擬合
SVM_model = SVC(kernel='linear', C=1.0)
# 對training data再切分成train data和evaluation data(取名還是用習慣的X_test和y_test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=17, stratify=y)
# 訓練Support Vector Classification模型
SVM_model.fit(X_train, y_train)

# predicted_y_results為模型預測的類別，expected_y_results為真正的類別
predicted_y_results, expected_y_results = [], []
expected_y_results.extend(y_test)
predicted_y_results.extend(SVM_model.predict(X_test))
# 計算出每一類別的precision, recall, f1-score
print(metrics.classification_report(expected_y_results, predicted_y_results))

# 預測training_new之外的test data
predicted_test_results = []
predicted_test_results.extend(SVM_model.predict(test))
# 輸出成符合格式的csv檔，放在Google Drive首頁
pa3_17_csv = pd.DataFrame({'Id':test_new_docID, 'Value':predicted_test_results})
pa3_17_csv.to_csv('pa3_17.csv', index = False)