from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import chi2
import numpy as np
import pandas
import jieba_fast
import sklearn.preprocessing
import json
import collections

class chi_square(object):

    def __init__(self):
        self.vocabulary = None
        self.data_size = 0
        self.chi2_statistics_collections = []
        self.classes_ = None
        self.vocabulary_ = None

    def _cut(self, item):
        return " ".join(jieba_fast.cut(item))

    def _dedupe(self, items, key=None):
        #dedupe list
        seen = set()
        for item in items:
            val = item if key is None else key(item)
            if val not in seen:
                yield item
                seen.add(val)

    def _data_pre(self, title_list, content_list, label_list, pred_list):
        if len(title_list) == len(content_list) == len(label_list):
            self.data_size = len(title_list)
        else:
            print("The lengh of input list should be equal.")
            return
        data = [a + b[:min(400, len(b))] for a, b in zip(title_list, content_list)]
        count_vect = CountVectorizer()
        jieba_fast.load_userdict("/data1/sina_dw/shichen/FastText/cppjieba/dict/user.dict.utf8")
        train_data_terms = [self._cut(r) for r in data]
        train_data = count_vect.fit_transform(train_data_terms)
        lb = sklearn.preprocessing.LabelBinarizer()
        Y = lb.fit_transform(label_list)
        if self.classes_ is None:
            self.classes_ = lb.classes_
        if self.vocabulary_ is None:
            self.vocabulary_ = count_vect.vocabulary_

        return train_data, Y, train_data_terms, count_vect

    def fit(self, title_list, content_list, label_list, pred_list):
        """Compute chi-squared stats between each non-negative feature and class.

            This score uses term counts in document classification to caculate
            chi-square stats of train data.

            Parameters
            ----------
            title_list, content_list, label_list, pred_list: array-like, shape = (n_samples, )

            The length of these lists should keep in same.

            Notes
            -----
            Train result save in self.chi2_statistics_collections: array-like, shape = (n_terms, n_category)

            """
        train_data, Y, train_data_terms, _ = self._data_pre(title_list, content_list, label_list, pred_list)
        chi2_statistics_collections = []
        for i in range(Y.shape[1]):
            chi2_statistics = chi2(train_data, Y[:, i])
            chi2_statistics_collections.append(chi2_statistics[0])
        self.chi2_statistics_collections = chi2_statistics_collections

    def transform(self, title_list, content_list, label_list, pred_list):
        """计算测试数据中的chi-squared stats

            Parameters
            ----------
            title_list, content_list, label_list, pred_list: array-like, shape = (n_samples, )

            The length of these lists should keep in same.

            Returns
            -------
            chi2_words_in_doc_sorted_pred: Terms list with chi-squared stats for pred label.

            chi2_words_in_doc_sorted_label: Terms list with chi-squared stats for manu label.
        """
        train_data, Y, train_data_terms, count_vect= self._data_pre(title_list, content_list, label_list,pred_list)
        chi2_words_in_doc_sorted_pred = []
        chi2_words_in_doc_sorted_label = []
        for i in range(self.data_size):
            word_chi2_statistics_list_pred = []
            word_chi2_statistics_list_label = []
            word_list = list(self._dedupe(train_data_terms[i].split(" ")))
            for word in word_list:
                if word in self.vocabulary_:
                    index_of_word_train = count_vect.vocabulary_[word]
                    index_of_word_Y = self.vocabulary_[word]
                    if label_list[i] in self.classes_:
                        index_of_label_label = np.argwhere(self.classes_ == label_list[i])[0][0]
                        index_of_label_pred = np.argwhere(self.classes_ == pred_list[i])[0][0]
                        word_chi2_statistics_list_pred.append((word, train_data[i,index_of_word_train], self.chi2_statistics_collections[index_of_label_pred][index_of_word_Y]))
                        word_chi2_statistics_list_label.append((word, train_data[i,index_of_word_train], self.chi2_statistics_collections[index_of_label_label][index_of_word_Y]))
            word_chi2_statistics_list_pred = sorted(word_chi2_statistics_list_pred, key=lambda x: x[2], reverse=True)
            word_chi2_statistics_list_pred = word_chi2_statistics_list_pred[:20]
            chi2_words_in_doc_sorted_pred.append(word_chi2_statistics_list_pred.copy())

            word_chi2_statistics_list_label = sorted(word_chi2_statistics_list_label, key=lambda x: x[2], reverse=True)
            word_chi2_statistics_list_label = word_chi2_statistics_list_label[:20]
            word_chi2_statistics_list_label.append(len(word_list))
            chi2_words_in_doc_sorted_label.append(word_chi2_statistics_list_label.copy())

        sta = collections.defaultdict(list)
        value_key = zip(self.vocabulary_.values(), self.vocabulary_.keys())
        value_key = sorted(value_key)
        for i in range(Y.shape[1]):
            word_list = []
            sorted_data = sorted(enumerate(self.chi2_statistics_collections[i]), key=lambda x:x[1], reverse=True)
            idx = [r[0] for r in sorted_data]
            for j in range(25):
                word_list.append((value_key[idx[j]][1], self.chi2_statistics_collections[i][idx[j]]))
            sta[self.classes_[i]].append(word_list)

        return chi2_words_in_doc_sorted_pred, chi2_words_in_doc_sorted_label, sta

if __name__ == "__main__":

    cq = chi_square()
    # excel 读取
    # dataframe = pandas.read_excel("caijing_e4.xlsx")
    # title_list = dataframe["title"]
    # content_list = dataframe["content"]
    # label_list = dataframe["label"]
    # pred_list = dataframe["pred"]
    #
    # title_list_Y = dataframe["title"]
    # content_list_Y = dataframe["content"]
    # label_list_Y = dataframe["label"]
    # pred_list_Y = dataframe["pred"]


    #json读取
    # with open("filename", "r", encoding="utf-8") as fr:
    #     data = json.loads(fr.read())
    # title_list = [r["title"] for r in data]
    # content_list = [r["content"] for r in data]
    # label_list = [r["label"] for r in data]
    # pred_list = [r["pred"] for r in data]

    #tsv读取
    with open("test_results_train1018.tsv", "r", encoding="utf-8") as fr:
        data = [(r.split("\t")[0], r.split("\t")[1], r.split("\t")[2], r.split("\t")[3]) for r in fr]
    title_list = [r[0] for r in data]
    content_list = [r[1] for r in data]
    label_list = [r[2] for r in data]
    pred_list = [r[3] for r in data]

    with open("test_results_test1018.tsv", "r", encoding="utf-8") as fr:
        data = [(r.split("\t")[0], r.split("\t")[1], r.split("\t")[2], r.split("\t")[3]) for r in fr]
    title_list_Y = [r[0] for r in data]
    content_list_Y = [r[1] for r in data]
    label_list_Y = [r[2] for r in data]
    pred_list_Y = [r[3] for r in data]

    cq.fit(title_list, content_list, label_list, pred_list)

    chi2_sta_pred, chi2_sta_label, sta = cq.transform(title_list_Y, content_list_Y, label_list_Y, pred_list_Y)

    write_data = [str(a) + '\t' + str(b) for a, b in zip(chi2_sta_label, chi2_sta_pred)]
    print(sta)
    with open("chi2_sta.tsv", "w", encoding="utf-8") as fw:
        fw.write("\n".join(write_data))



