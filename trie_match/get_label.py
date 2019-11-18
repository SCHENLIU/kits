import os
import collections
from trie import Trie

class get_label(object):
    def __init__(self):
        '''
        Build Trie for each class,

        Data save in collections.defaultdict , key stands for the dict name and value is the datastructure(class Trie).

        '''
        self.data_dir = "keywords_dict"
        _, _, file_name_list = list(os.walk(self.data_dir))[0]
        self.keywords_dict = collections.defaultdict(Trie)

        for name in file_name_list:
            with open(os.path.join(self.data_dir, name), "r", encoding="utf-8") as fr:
                words = fr.readlines()
                for word in words:
                    word = word.strip().replace("\n", "").replace("\r", "")
                    self.keywords_dict[name[:-4]].insert(word)
            print(name[:-4], "Words dict has been loaded")

    def match(self, match_string):
        result = []
        for dict_name in self.keywords_dict.keys():
            match_result = self._match(match_string, dict_name)
            if match_result is not False:
                result.append(dict_name)
        return result


    def _match(self, match_string, dict_name):
        '''

        :param match_string: Input string. Type str
        :return: words matched in dict. Type: list

        Complexity: O(n)
        '''
        labels = collections.defaultdict(lambda :0)
        begin = 0
        while begin < len(match_string):
            k=0
            begin_change = 0
            current = self.keywords_dict[dict_name].root
            while begin + k < len(match_string):
                current = current.children.get(match_string[begin + k])
                if current is None:
                    begin = begin + 1
                    begin_change = 1
                    break

                if current.is_word is True:
                    labels[match_string[begin:begin + k + 1]] += 1
                    begin = begin + k + 1
                    begin_change = 1
                    break
                k += 1
            if begin_change == 0:
                begin += 1
        return False if len(labels) == 0 else list(labels.keys())