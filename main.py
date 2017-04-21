# -*- coding:utf8 -*-
import jieba
import jieba.posseg as pseg
import xml.etree.cElementTree as ET
import os


def getDicts():
    adv = {}
    with open("./data/adverb.txt", 'r') as fin:
        for line in fin:
            vocab, score = line.decode('gbk').strip().split(" ")
            adv[vocab] = score

    privative = []
    with open("./data/privative.txt", 'r') as fin:
        for line in fin:
            vocab = line.decode('gbk').strip()
            privative.append(vocab)

    specialnoun = []
    with open("./data/specialnoun.txt", 'r') as fin:
        for line in fin:
            vocab = line.decode('gbk').strip()
            specialnoun.append(vocab)

    minus_words = []
    with open('./data/minus.txt','r') as fin:
        for line in fin:
            vocab = line.decode('gbk').strip().split(" ")[0]
            minus_words.append(vocab)

    plus_words = []
    with open('./data/plus.txt','r') as fin:
        for line in fin:
            vocab = line.decode('gbk').strip().split(" ")[0]
            plus_words.append(vocab)

    return adv, privative, specialnoun, minus_words, plus_words

def getContext(filename):
    tree = ET.ElementTree(file=filename)
    root = tree.getroot()
    title = root[0].text
    url = root[1].text
    content = root[2].text.replace("\n", "")
    return title, url, content

def getCutAll(content):
    text_ = pseg.cut(content)
    text_list = []
    for w in text_:
        text_list.append(w.word + "/" + w.flag)
    cut_all = " ".join(text_list)
    return cut_all

def getFileName(filename):
    return filename.split("/")[-1].split(".")[0]

def getScore(content):
    words = jieba.cut(content)
    word_score = []
    words_ = [w for w in words]

    for word_idx in range(len(words_)):
        if words_[word_idx] in plus_words:
            if word_idx-1 > 0 and words_[word_idx-1] in adv.keys():
                ws = 0.8 * float(adv[words_[word_idx-1]])
                word_score.append((words_[word_idx-1] + "#" + words_[word_idx], ws))
            else:
                word_score.append((words_[word_idx], 0.8))

        if words_[word_idx] in minus_words:
            if word_idx-1 > 0 and words_[word_idx-1] in adv.keys():
                ws = -0.8 * float(adv[words_[word_idx-1]])
                word_score.append((words_[word_idx-1] + "#" + words_[word_idx], ws))
            else:
                word_score.append((words_[word_idx], -0.8))

    avg_score = 0
    for _, sc in word_score:
        avg_score += sc

    avg_score /= len(word_score)

    if avg_score > 0.0:
        if avg_score < 0.8:
            score_tag = u"褒义(微弱)"
        elif avg_score > 0.9:
            score_tag = u"褒义(强烈)"
        else:
            score_tag = u"褒义(一般)"
    elif avg_score == 0.0:
        score_tag = u"中性"
    else:
        if avg_score > -0.8:
            score_tag = u"贬义(微弱)"
        elif avg_score < -0.9:
            score_tag = u"贬义(强烈)"
        else:
            score_tag = u"贬义(一般)"

    word_score_list = []
    for ws_t, ws_s in word_score:
        word_score_list.append(ws_t + "=" + str(ws_s))

    word_score_str = "  ".join(word_score_list)

    return word_score_str, avg_score, score_tag

def genOutput(inpfilename, outpfilename):
    title, url, content = getContext(inpfilename)

    cut_all = getCutAll(content)
    word_score_str, avg_score, score_tag = getScore(content)


    with open(outpfilename, 'w') as fout:
        fout.write(title.encode('GBK'))
        fout.write("\r\n")
        fout.write(getFileName(inpfilename))
        fout.write("\r\n")
        fout.write(url)
        fout.write("\r\n")
        fout.write(content.encode('GBK').strip())
        fout.write("\r\n")
        fout.write(cut_all.encode('GBK'))
        fout.write("\r\n")
        fout.write("NULL\r\n")
        fout.write(str(avg_score))
        fout.write("\r\n")
        fout.write(word_score_str.encode('GBK'))
        fout.write("\r\n")
        fout.write(score_tag.encode('GBK'))
        fout.write("\r\n")

adv, privative, specialnoun, minus_words, plus_words = getDicts()


source_dir = "./output/"
target_dir = "./result/"


for dir_l1 in os.listdir(source_dir):
    for dir_l2 in os.listdir(source_dir+dir_l1):
        for filename in os.listdir(source_dir+dir_l1+"/"+dir_l2):
            source_filename = source_dir + dir_l1 + "/" + dir_l2 + "/" + filename
            target_filename = target_dir + dir_l1 + "/" + dir_l2 + "/" + filename.replace("xml", "txt")
            try:
                genOutput(source_filename, target_filename)
            except:
                print("ParseError.文件"+filename+"结构不正确,跳过处理.")
                pass
