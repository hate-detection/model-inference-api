import WordsPy as Wp
import pandas as pd
from LID_tool.getLanguage import langIdentify
from indictrans import Transliterator
import enchant
import string
import re
import emoji
from Levenshtein import distance as levenshtein_distance
from collections import defaultdict


# ====================== Preparing lists, dicts, and Transliterators ======================

hindi = Wp.Hindi()
profane_words = pd.read_csv("data/profanity.csv")
proper_nouns = pd.read_csv("data/names.csv")

hindi_words = hindi.get_all_words()
hi_all = pd.Series(hindi_words)
hi_all.name = 0
hi_all.head()

hi_small = pd.read_csv('data/hindi_words.csv')
hi_small.dropna()
hi_small.columns = [i for i in range(46)]
hi_small.head()

hi_small = [str(x) for x in hi_small.values.flatten()]
names_list = [str(x) for x in proper_nouns.values.flatten()]
hi_small_list = set(hi_small + names_list)
profane_list = set([str(x) for x in profane_words["roman"].values.flatten()])
hi_all_list = set(hi_all.tolist())

trn_h2e = Transliterator(source='hin', target='eng', build_lookup=True)
trn_e2h = Transliterator(source='eng', target='hin', build_lookup=True)

cache = defaultdict(dict)
dictionary = enchant.Dict("hi")

# ====================== Preparation Done ======================


class PrelimProcess:
    def __init__(self):
        self.punct = string.punctuation
        self.user_pattern = re.compile('@[\w]+')
        self.html_pattern = re.compile('<.*?>')
        self.url_pattern = re.compile(r'https?://\S+|www\.\S+')
        self.emoji = emoji.EMOJI_DATA

    def trans_h2e(self, text: str) -> str:
        return trn_h2e.transform(text)

    def remove_usernames(self, text: str) -> str:
        return self.user_pattern.sub(r'', text)

    def remove_punct(self, text: str) -> str:
        return text.translate(str.maketrans('', '', self.punct))

    def remove_html_tag(self, text: str) -> str:
        return self.html_pattern.sub(r'', text)

    def remove_urls(self, text: str) -> str:
        return self.url_pattern.sub(r'', text)

    def remove_emojis(self, text: str) -> str:
        return ''.join(char for char in text if char not in self.emoji)
    
    def prelim_process(self, text: str) -> str:
        text = text.lower()
        text = self.remove_usernames(text)
        text = self.remove_html_tag(text)
        text = self.remove_urls(text)
        text = self.remove_emojis(text)

        return text




class TransProcess:
    def __init__(self):
        self.label = "EN"
    
    def lang_check(self, text: str):
        return [item for sublist in (langIdentify(text, "LID_tool/classifiers/HiEn.classifier")) for item in sublist]


    def find_nearest_neighbour(self, word: str) -> str:
        if word in cache:
            return cache[word]

        nearest_neighbour = min(hi_small_list, key=lambda x: levenshtein_distance(word, x))
        if not nearest_neighbour:
            nearest_neighbour = min(hi_all_list, key=lambda x: levenshtein_distance(word, x))

        cache[word] = nearest_neighbour
        word = nearest_neighbour

        return word


    def check_and_trans(self, word: str, label:str) -> str:
        if word in profane_list:
            word = profane_words.loc[profane_words.roman == word, "deva"].values[0]
            return word

        if label == "HI":
            if dictionary.check(word) == False and word not in profane_list:
                word = self.find_nearest_neighbour(word)
        return word


    def trans_2h(self, text: str) -> str:
        word_label_pairs = self.lang_check(text)
        transformed_words = [
            trn_e2h.transform(word) if label != self.label and word not in profane_list else word
            for word, label in word_label_pairs
        ]
        trans = [self.check_and_trans(word, label) for word, label in zip(transformed_words, [label for _, label in word_label_pairs])]

        return ' '.join(trans)



def main(text):
    prelim_process = PrelimProcess()
    trans_process = TransProcess()

    cleaned_text = prelim_process.prelim_process(text)
    transformed_text = trans_process.trans_2h(cleaned_text)

    return transformed_text


if __name__=="__main__":
    text = "@pikachu Mera naam roshan hai main ek https://example.com engineer hoon"
    transformed_text = main(text)
    print(transformed_text)