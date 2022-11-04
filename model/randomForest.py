import time
import joblib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
file_name = ['../data/3SGP---63554 events', '../data/3SLP---62910 events',
             '../data/LSTaP---64097 events', '../data/STetraP---63445 events']
for i in range(4):
    file_name[i] += 'By3on2000.csv'
def load_random_forest_data(file_name):
    features = []
    labels = []
    for index, file in enumerate(file_name):
        raw_data = pd.read_csv(file, header=0)  # 读取csv数据，并将第一行视为表头，返回DataFrame类型
        length = raw_data.shape[0]
        data = raw_data.values
        features.extend(data[::, 1::])
        labels.extend([index] * length)
    # 选取20%数据作为测试集，剩余为训练集
    # stratify=labels 这个是分组的标志，用到自己数据集上即为四个分子的类别，保证每个分子取到的样本数差不多，分层抽样
    train_features, test_features, train_labels, test_labels = train_test_split(features, labels,
                                                                                test_size=0.2, stratify=labels)
    return train_features, test_features, train_labels, test_labels

if __name__ == '__main__':
    epoch = 100
    print('prepare datasets...')
    # Iris数据集
    # iris=datasets.load_iris()
    # features=iris.data
    # labels=iris.target
    time_2 = time.time()
    model_path = None
    test_acc = []
    train_acc = []
    confusion_matrix = np.zeros((4, 4))
    confusion_matrix.tolist()
    ps, rs, fs, cs, roc = [], [], [], [], []
    for i in range(epoch):
        # 自己数据集加载
        train_features, test_features, train_labels, test_labels = load_random_forest_data(file_name)
        print('Start training...')

        # n_estimators表示要组合的弱分类器个数；
        # algorithm可选{‘SAMME’, ‘SAMME.R’}，默认为‘SAMME.R’，表示使用的是real boosting算法，‘SAMME’表示使用的是discrete boosting算法
        clf = RandomForestClassifier(n_estimators=30)
        clf.fit(train_features, train_labels)  # training the svc model
        train_score = clf.score(train_features, train_labels)
        train_acc.append(train_score)
        print("训练集：", train_score)

        joblib.dump(clf, "randomForest_model.m")
        time_3 = time.time()
        print('training cost %f seconds' % (time_3 - time_2))

        print('Start predicting...')
        test_predict = clf.predict(test_features)
        # 获取验证集的准确率
        test_score = clf.score(test_features, test_labels)
        test_acc.append(test_score)
        print("The test accruacy score is %f" % test_score)
        time_4 = time.time()
        print('predicting cost %f seconds' % (time_4 - time_3))

        # 采用混淆矩阵（metrics）计算各种评价指标
        ps.append(metrics.precision_score(test_labels, test_predict, average='weighted'))
        rs.append(metrics.recall_score(test_labels, test_predict, average='weighted'))
        fs.append(metrics.f1_score(test_labels, test_predict, average='weighted'))
        cs.append(np.mean(test_labels == test_predict))

        # 分类报告
        class_report = metrics.classification_report(test_labels, test_predict,
                                                     target_names=["3SGP", "3SLP", "LSTaP", "STetraP"])
        print(class_report)

        # 输出混淆矩阵
        confusion_matrix += metrics.confusion_matrix(test_labels, test_predict, normalize='true')
    print('--混淆矩阵--')
    print(confusion_matrix / 100)
    # 画出混淆矩阵
    # ConfusionMatrixDisplay 需要的参数: confusion_matrix(混淆矩阵), display_labels(标签名称列表)
    labels = ['3SGP', '3SLP', 'LSTaP', 'STetraP']
    disp = ConfusionMatrixDisplay(confusion_matrix=confusion_matrix / 100, display_labels=labels)
    disp.plot()
    plt.title('randomForest')
    plt.savefig('../picture/randomForest3.png')
    plt.show()
    mean_acc_train = sum(train_acc) / 100
    mean_acc_test = sum(test_acc) / 100
    print("The mean of train accruacy score is %f" % mean_acc_train)
    print("The mean of test accruacy score is %f" % mean_acc_test)
    print('*' * 10, 'one hundray time', '*' * 10)
    print('精准值：%.5f' % (sum(ps) / 100))
    print('召回率：%.5f' % (sum(rs) / 100))
    print('F1: %.5f' % (sum(fs) / 100))
    print("准确率:%.5f" % (sum(cs) / 100))

