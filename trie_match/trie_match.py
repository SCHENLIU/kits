import collections
import random
import functools
import os
from get_label import get_label
from article import article
import codecs
import json
import re
import time

class dataprocess(object):
    def read_json(self, input_file, quotechar=None):
        lists = []
        with codecs.open(input_file, "r", "utf-8") as fd:
            rc = json.loads(fd.read())
            for item in rc:
                artical_ins = article()
                label = "None" if "label" not in item.keys() else str(item["label"])
                title = "None" if "title" not in item.keys() else item["title"]
                content = "None" if "content" not in item.keys() else item["content"]
                ctime = "None" if "ctime" not in item.keys() else str(item["ctime"])
                url = "None" if "url" not in item.keys() else item["url"]
                uuid = "None" if "uuid" not in item.keys() else item["uuid"]
                artical_ins.label = label.replace("\n", "").replace("\r", "").replace("\t", "")
                artical_ins.title = title.replace("\n", "").replace("\r", "").replace("\t", "")
                artical_ins.content = content.replace("\n", "").replace("\r", "").replace("\t", "")
                artical_ins.ctime = ctime.replace("\n", "").replace("\r", "").replace("\t", "")
                artical_ins.url = url.replace("\n", "").replace("\r", "").replace("\t", "")
                artical_ins.uuid = uuid.replace("\n", "").replace("\r", "").replace("\t", "")

                lists.append(artical_ins)
        lists = list(self._dedupe(lists, key=lambda a:a.title))
        return lists


    def _dedupe(self, items, key=None):
        #dedupe list
        seen = set()
        for item in items:
            val = item if key is None else key(item)
            if val not in seen:
                yield item
                seen.add(val)




if __name__ == "__main__":


    dataprocesor = dataprocess()
    article_list = dataprocesor.read_json("esg1111.json")
    namedict = {"filename0":"name0",
                "filename1": "name1",
                "filename2": "name2",
                "filename3": "name3",
                "filename4": "name4",
                "filename5": "name5",
                "filename6": "name6",
                }
    rex = re.compile("测试")

    start = time.time()
    save_data_1 = []
    save_data_2 = []
    get_label = get_label()
    for i in range(len(article_list)):
        article_list[i].title_matched = get_label.match(article_list[i].title)
        article_list[i].content_matched = get_label.match(article_list[i].content[:40])
        words_filter = 0 if rex.search(article_list[i].title + article_list[i].content[:40]) is not None else 1
        if len(article_list[i].title_matched) == 1 and words_filter:
            save_data_1.append(article_list[i])
            article_list[i].label = namedict[article_list[i].title_matched[0]]
        elif len(article_list[i].content_matched) == 1 and words_filter:
            save_data_1.append(article_list[i])
            article_list[i].label = namedict[article_list[i].content_matched[0]]


        if len(article_list[i].title_matched) > 1 or len(article_list[i].content_matched) > 1:
            save_data_2.append(article_list[i])
            article_list[i].label = "esg"
    end = time.time()
    print("Time:", end - start)
    tuple_list = [(acl.title,acl.content,acl.label) for acl in save_data_1]
    print(len(save_data_1))
    print(len(save_data_2))

    with open("filename.tsv", "w", encoding="utf-8") as fw:
        sta_test = collections.defaultdict(lambda :100)
        data_test = []
        for i in range(len(tuple_list)):
            if sta_test[tuple_list[i][2]] >= 0:
                data_test.append(tuple_list[i])
                sta_test[tuple_list[i][2]] -= 1
        data_test = ["\t".join(r) for r in data_test]
        fw.write("\n".join(data_test))












