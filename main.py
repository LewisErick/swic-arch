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
    def __init__(self, sentences, params):
        super()
        '''
        Corrida 1: Parametros
        '''
        self._params = params
        self._sentences = sentences # list<Sentence>
    
    def _read_sentences(self):
        sentences = []
        for sentence in self._sentences.split("\n"):
            sentences.append(Sentence(sentence))
        return sentences

    def _remove_sentences_if_needed(self, sentences):
        '''
        Corrida 2:
        Remover lineas antes de permutacion
        '''
        line_to_remove = 0
        while line_to_remove >= 0:
            for i, sentence in enumerate(sentences):
                print(i+1, sentence.get_sentence_str())
            line_to_remove = int(input('Give number >= 1 to remove line, otherwise -1\n'))
            if line_to_remove > 0:
                del sentences[line_to_remove-1]
        return sentences

    def execute_filter(self):
        read_sentences = self._read_sentences()
        read_sentences = self._remove_sentences_if_needed(read_sentences)
        self.tokenizer = SentenceTokenizer(' ', read_sentences, self._params)
        self.tokenizer.execute_filter()

# Tokenizer

class SentenceTokenizer(Tokenizer):
    # array of sentences -> array of sentences
    # ["a b c", "d e f"] -> [["a", "b", "c"], ["d", "e", "f"]]
    def __init__(self, separator, sentences, params):
        super()
        '''
        Corrida 1: Parametros
        '''
        self._params = params
        self._stop_words = params.get('stop_words')
        self._sentences = sentences # list<Sentence>
        self._separator = separator
    
    def _tokenize(self):
        tmp = []
        for sentence in self._sentences:
            sentence_str = sentence.get_sentence_str()
            '''
            Corrida 1
            Filter out words if exact match with stop words in params
            '''
            sentence_words = [Word(s) for s in sentence_str.split(self._separator) if s not in self._stop_words]
            sentence.set_words(sentence_words)
            tmp.append(sentence)
        return tmp

    def execute_filter(self):
        tokenized_sentences = self._tokenize()
        self.permutator = SentencePermutator(tokenized_sentences, self._params)
        self.permutator.execute_filter()

# Permutator

class SentencePermutator(Permutator):
    def __init__(self, sentences, params):
        self._sentences = sentences # list<list<Sentence>>
        '''
        Corrida 1: Parametros
        '''
        self._params = params
    
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
        self.sorter = SentencesSorter(permutated_sentences, self._params)
        self.sorter.execute_filter()

# Sorter

# [["clouds", "are", "White"] , ["are", "White", "Clouds"], ["White", "clouds", "are"]]
class SentencesSorter(Sorter):
    def __init__(self, sentences, params):
        '''
        Corrida 1: Parametros
        '''
        self._params = params
        self._descending_order = params.get('descending_order')
        self._sentences = sentences # list<list<Sentences>>
    
    def _cmp(self, A: Sentence, B: Sentence):
        tmp = A.get_words()
        tmp2 = B.get_words()
        for n in range(min(len(tmp), len(tmp2))):
            if tmp[n].get_content() != tmp2[n].get_content():
                if tmp[n].get_content() < tmp2[n].get_content():
                    return -1
                else:
                    return 1
        if len(tmp) < len(tmp2):
            return -1
        else:
            return 1

    def _sort(self):
        '''
        Corrida 1
        Added reverse option from descending order param
        '''
        return sorted(self._sentences, key=functools.cmp_to_key(self._cmp), reverse=self._descending_order)

    def execute_filter(self):
        sorted_sentences = self._sort()
        self.presenter = SentencePresenter(sorted_sentences, self._params)
        self.presenter.execute_filter()

# Presenter

class SentencePresenter(Presenter):
    def __init__(self, sentences, params):
        self._sentences = sentences #list<list<Sentence>>
        '''
        Corrida 1: Parametros
        '''
        self._params = params
    
    def _remove_sentences_if_needed(self, sentences):
        '''
        Corrida 2:
        Remover lineas antes de permutacion
        '''
        line_to_remove = 0
        while line_to_remove >= 0:
            for i, sentence in enumerate(sentences):
                print(i+1, sentence.get_sentence_str())
            line_to_remove = int(input('Give number >= 1 to remove line, otherwise -1\n'))
            if line_to_remove > 0:
                del sentences[line_to_remove-1]
        return sentences
        
    def execute_filter(self):
        '''
        Corrida 3
        Eliminar oraciones de salida
        '''
        filtered_sentences = self._remove_sentences_if_needed(self._sentences)
        with open(self._params.get('output_file_path'), 'w') as f:
            for sentence in filtered_sentences:
                f.write(' '.join([w.get_content() for w in sentence.get_words()]) + '\n')

if __name__ == '__main__':
    if len(sys.argv) < 5:
        raise Exception('Specify one more param, the text file path')
    
    '''
    Corrida 1: Added params START
    '''
    params = {
        'input_file_path': sys.argv[1],
        'stop_words_file_path': sys.argv[2],
        'descending': sys.argv[3],
        'output_file_path': sys.argv[4]
    }

    with open(params.get('input_file_path'), 'r') as f:
        input_text = f.read()
    
    with open(params.get('stop_words_file_path'), 'r') as f:
        stop_words = f.read().split('\n')
    
    if params.get('descending') == 'true':
        descending_order = True
    else:
        descending_order = False

    '''
    Corrida 1: Added params END
    '''
    reader = SentenceReader(
        input_text,
        {
            'stop_words': stop_words,
            'descending_order': descending_order,
            'output_file_path': params.get('output_file_path')
        }
    )
    reader.execute_filter()