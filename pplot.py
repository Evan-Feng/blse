import numpy as np
import argparse
import pickle
from sklearn.manifold import TSNE
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from itertools import accumulate
from utils.dataset import *
from utils.math import *
from utils.bdi import *
from utils.model import *


COLORS = ['b', 'b', 'r', 'g', 'k', 'y', 'c']

np.random.seed(0)


def load_W_source(model_path):
    with tf.variable_scope('projection', reuse=tf.AUTO_REUSE):
        W_source = tf.get_variable(
            'W_source', dtype=tf.float32, initializer=tf.constant(np.zeros((300, 300), dtype=np.float32)))

    with tf.Session() as sess:
        tf.train.Saver().restore(sess, model_path)
        W_source_ = sess.run(W_source)

    return W_source_


def main(args):
    dic = load_model(args.W)
    W_src = dic['W_source']
    W_trg = dic['W_target']
    src_lang = dic['source_lang']
    trg_lang = dic['target_lang']
    model = dic['model']
    with open('pickle/%s.bin' % src_lang, 'rb') as fin:
        src_wv = pickle.load(fin)
    with open('pickle/%s.bin' % trg_lang, 'rb') as fin:
        trg_wv = pickle.load(fin)
    src_senti_words = SentiWordSet('categories/categories.%s' % src_lang).to_index(src_wv)
    trg_senti_words = SentiWordSet('categories/categories.%s' % trg_lang).to_index(trg_wv)
    src_offsets = [0] + list(accumulate([len(t) for t in src_senti_words.wordsets]))
    trg_offsets = [0] + list(accumulate([len(t) for t in trg_senti_words.wordsets]))
    src_word_idx = sum(src_senti_words.wordsets, [])
    trg_word_idx = sum(trg_senti_words.wordsets, [])

    if model == 'ubise':
        src_proj_emb = np.dot(src_wv.embedding, W_src)
        trg_proj_emb = np.dot(trg_wv.embedding, W_trg)
        length_normalize(src_proj_emb, inplace=True)
        length_normalize(trg_proj_emb, inplace=True)
    elif model == 'ubi':
        src_proj_emb = np.dot(src_wv.embedding, W_src)
        trg_proj_emb = np.dot(trg_wv.embedding, W_trg)

    fig, ax = plt.subplots()

    X = src_proj_emb[src_word_idx]
    ax = fig.add_subplot(121)
    X = TSNE(2, verbose=2).fit_transform(X)
    for i, label in enumerate(src_senti_words.labels):
        tmp = X[src_offsets[i]:src_offsets[i + 1]]
        ax.scatter(tmp[:, 0], tmp[:, 1], s=10, label=label, color=COLORS[i])
    ax.legend()
    ax.set_title(args.W + '-source')

    X = trg_proj_emb[trg_word_idx]
    ax = fig.add_subplot(122)
    X = TSNE(2, verbose=2).fit_transform(X)
    for i, label in enumerate(trg_senti_words.labels):
        tmp = X[trg_offsets[i]:trg_offsets[i + 1]]
        ax.scatter(tmp[:, 0], tmp[:, 1], s=10, label=label, color=COLORS[i])
    ax.legend()
    ax.set_title(args.W + '-target')

    fig.set_size_inches(20, 8)
    fig.savefig(args.output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('W',
                        help='W_src and W_trg')
    parser.add_argument('output',
                        help='output file')

    args = parser.parse_args()
    main(args)
