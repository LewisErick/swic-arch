from copy import copy

import functools
import os
import sys

# Interfaces
class Filter:
    def execute_filter():
        raise Exception('interface method')

class Text:
    def __init__(self, content: str):
        self._content = content

class Reader(Filter):
    def __init__(self):
        self._children = []
        self.tokenizer = None

    def add(self, c: Filter):
        self._children.append(c)

    def getChildren(self):
        return self._children

class Tokenizer(Filter):
    def __init__(self):
        self._children = []
        self.permutator = None

    def add(self, c: Filter):
        self._children.append(c)

    def getChildren(self):
        return self._children
        
class Permutator(Filter):
    def __init__(self):
        self._children = []
        self.sorter = None

    def add(self, c: Filter):
        self._children.append(c)

    def getChildren(self):
        return self._children

class Sorter(Filter):
    def __init__(self):
        self._children = []
        self.presenter = None

    def add(self, c: Filter):
        self._children.append(c)

    def getChildren(self):
        return self._children

class Presenter(Filter):
    def __init__(self):
        pass
    

# Derived classes

# Text

class Sentence(Text):
    def __init__(self, sentence_str: str):
        self._sentence_str = sentence_str
        self._words = [] # list<words>
    
    def get_sentence_str(self):
        return self._sentence_str

    def get_words(self):
        return self._words
    
    def set_words(self, words):
        self._words = words

class Word(Text):
    def __init__(self, content: str):
        self._content = content

    def get_content(self):
        return self._content

# Reader

class SentenceReader(Reader):
    # string -> array of sentences
    # "a b c\nd e f\n" -> ["a b c", "d e f"]
    def __init__(self, sentences):
        super()
        self._sentences = sentences # list<Sentence>
    
    def _read_sentences(self):
        sentences = []
        for sentence in self._sentences.split("\n"):
            sentences.append(Sentence(sentence))
        return sentences

    def execute_filter(self):
        read_sentences = self._read_sentences()
        self.tokenizer = SentenceTokenizer(' ', read_sentences)
        self.tokenizer.execute_filter()

# Tokenizer

class SentenceTokenizer(Tokenizer):
    # array of sentences -> array of sentences
    # ["a b c", "d e f"] -> [["a", "b", "c"], ["d", "e", "f"]]
    def __init__(self, separator, sentences):
        super()
        self._sentences = sentences # list<Sentence>
        self._separator = separator
    
    def _tokenize(self):
        tmp = []
        for sentence in self._sentences:
            sentence_str = sentence.get_sentence_str()
            sentence_words = [Word(s) for s in sentence_str.split(self._separator)]
            sentence.set_words(sentence_words)
            tmp.append(sentence)
        return tmp

    def execute_filter(self):
        tokenized_sentences = self._tokenize()
        self.permutator = SentencePermutator(tokenized_sentences)
        self.permutator.execute_filter()

# Permutator

class SentencePermutator(Permutator):
    def __init__(self, sentences):
        self._sentences = sentences # list<list<Sentence>>
    
    def _permutate(self):
        rotations = []
        for sentence in self._sentences:
            # ["Clouds", "are", "white"]
            sentence_words = sentence.get_words()
            for n in range(len(sentence_words)):
                rotated_words = sentence_words
                rotated_words = [rotated_words[(i + n) % len(rotated_words)] for i, x in enumerate(rotated_words)]

                rotated_sentence = Sentence(' '.join([w.get_content() for w in rotated_words]))
                rotated_sentence.set_words(rotated_words)
                rotations.append(rotated_sentence)
        return rotations
    
    def execute_filter(self):
        permutated_sentences = self._permutate()
        self.sorter = SentencesSorter(permutated_sentences)
        self.sorter.execute_filter()

# Sorter

# [["clouds", "are", "White"] , ["are", "White", "Clouds"], ["White", "clouds", "are"]]
class SentencesSorter(Sorter):
    def __init__(self, sentences):
        self._sentences = sentences # list<list<Sentences>>
    
    def _cmp(self, A: Sentence, B: Sentence):
        tmp = A.get_words()
        tmp2 = B.get_words()
        for n in range(min(len(tmp), len(tmp2))):
            if tmp[n].get_content() != tmp2[n].get_content():
                return tmp[n].get_content() < tmp2[n].get_content()
        return len(tmp) < len(tmp2)

    def _sort(self):
        return sorted(self._sentences, key=functools.cmp_to_key(self._cmp))

    def execute_filter(self):
        sorted_sentences = self._sort()
        self.presenter = SentencePresenter(sorted_sentences)
        self.presenter.execute_filter()

# Presenter

class SentencePresenter(Presenter):
    def __init__(self, sentences):
        self._sentences = sentences #list<list<Sentence>>
        
    def execute_filter(self):
        for sentence in self._sentences:
            print(' '.join([w.get_content() for w in sentence.get_words()]))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('Specify one more param, the text file path')

    file_path = sys.argv[1]
    with open(file_path, 'r') as f:
        input_text = f.read()

    reader = SentenceReader(
        input_text
    )
    reader.execute_filter()