#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
# find_gene_by_nltk.py
# 该例子：获取所有含有基因单词的文章句子，以 pmid - [句子1, 句子2] 为返回结果
import os
import re

import nltk

from pubmed import MultiFilePubmud, OneFilePubmud


def splitSentence(paragraph):
    # 分句
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = tokenizer.tokenize(paragraph)
    return sentences


STOP_WORD = ('RNA', 'ABSTRACT', 'DNA', 'LAI', 'PROC', 'GLM', 'PROC', 'REG', 'T2', 'J2', 'NRC', 'AOAC',
             'SRM', 'CV', 'MALDI-TOF-MS', 'NO', 'NH', 'MT', 'CO', 'BP', 'HPLC', 'JN', 'ANCOVA', 'PCR')


def have_feature(word):
    """
    word: 单词
    ret: 是否有基因特征
    """
    if word in STOP_WORD:
        return False
    # 全部大写
    if len(word) > 1 and re.search('^[A-Z]+$', word):
        return True
    # 含有单个数字
    single_num_pattern = re.compile('\d')
    if len(single_num_pattern.findall(word)) == 1 and len(word) > 3:
        return True
    # 含有连接词
    if re.search('^[A-Z].*-', word):
        return True
    # 大写字母—数字
    if re.search('^[A-Z]+\d+$', word):
        return True
    # 大写字母-小写字母-大写字母
    if re.search('^[A-Z]+[a-z]+[A-Z]+$', word):
        return True
    # 单个大写字母
    # if len(word) == 1 and word.isupper():
    #     return True
    # 小写字母-数字-小写字母
    if re.search('^[a-z]+\d+[a-z]+$', word):
        return True
    # 大写字母-小写字母
    if re.search('^[A-Z]{2,}[a-z]+$', word):
        return True
    # 小写字母-大写字母
    if re.search('^[a-z]{2,}[A-Z]+$', word):
        return True
    if re.search(r'Glyma\d{2}[Gg]\d+(.\d)', word):
        return True
    if re.search(r'G[Mm].+', word):
        return True

    return False


def fetch_gene_by_feature(content):
    sents = splitSentence(content)
    result = dict()

    # find key sent by profix features
    flag_list = [
        'quantification of',
        'Expression patterns? of',
        'Relative quantification of',
        'Expression of',
        'validation of',
        'quantities of',
        'analysis of',
        'profiles of',
        'accumulation of',
        'expression levels? of',
        'targets? of',
        'transcript profiles? of',
        'transcript levels? of',
        'Transcript profiling of',
        'Expression study of',
        'mRNA abundance of',
    ]
    # 锁定句子 re.I忽略大小写匹配
    pattern_list = [re.compile(flag, re.I) for flag in flag_list]

    for sent in sents:
        for pattern in pattern_list:
            if pattern.search(sent):
                # 标注词性
                pos_sent = nltk.pos_tag(nltk.word_tokenize(sent))
                # 在词性为NNP的词中找基因(专有名词)
                for word in [w for (w, p) in pos_sent if 'NNP' in p]:
                    if have_feature(word):
                        result.setdefault(sent, []).append(word)
    return result


def get_gene_sentence(file_path, trai):
    if os.path.isfile(file_path):
        root = OneFilePubmud(file_path)
    elif os.path.isdir(file_path):
        root = MultiFilePubmud(file_path, trait)
    else:
        raise NotADirectoryError("路径出错")

    res = dict()

    for article, key, title in root.yield_all(["摘要", "PMID", "标题"]):
        if isinstance(article, list):
            # 如果该标题有好几个文章
            article = '\n'.join(article)
        
        # 通过摘要选出需要的句子
        result = fetch_gene_by_feature(article)
        # 通过标题选出需要的句子
        title_res = fetch_gene_by_feature(title)
        # 上传标题中的结果
        if title_res:
            result.update(title_res)

        # 如果有结果，以 PMID 为 key，结果为 value。上传键值对，输出打印信息
        if result:
            res[key] = result
            print('在PMID为:', key, "的文章中")
            print(result)

    return res

def main():
    get_gene_sentence("you/path/about/pubmed/files")

if __name__ == '__main__':
    main()