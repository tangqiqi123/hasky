#!/usr/bin/env python
# -*- coding: gbk -*-
# ==============================================================================
#          \file   predict.py
#        \author   chenghuige  
#          \date   2016-10-19 06:54:26.594835
#   \Description  
# ==============================================================================

  
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
flags = tf.app.flags
FLAGS = flags.FLAGS

#FIXME: attention will hang..., no attention works fine
#flags.DEFINE_string('model_dir', '/home/gezi/temp/textsum/model.seq2seq.attention/', '')
flags.DEFINE_string('model_dir', '/home/gezi/temp/textsum/model.seq2seq/', '')
flags.DEFINE_string('vocab', '/home/gezi/temp/textsum/tfrecord/seq-basic.10w/train/vocab.txt', 'vocabulary file')

import sys, os, math
import gezi, melt
import numpy as np

from deepiu.util import text2ids

import conf  
from conf import TEXT_MAX_WORDS, INPUT_TEXT_MAX_WORDS, NUM_RESERVED_IDS, ENCODE_UNK

#TODO: now copy from prpare/gen-records.py
def _text2ids(text, max_words):
  word_ids = text2ids.text2ids(text, 
                               seg_method=FLAGS.seg_method, 
                               feed_single=FLAGS.feed_single, 
                               allow_all_zero=True, 
                               pad=False)
  word_ids = word_ids[:max_words]
  word_ids = gezi.pad(word_ids, max_words, 0)

  return word_ids

def predict(predictor, input_text):
  word_ids = _text2ids(input_text, INPUT_TEXT_MAX_WORDS)
  print('word_ids', word_ids, 'len:', len(word_ids))
  print(text2ids.ids2text(word_ids))

  timer = gezi.Timer()
  initial_state, ids, logprobs = predictor.inference([
                                        'beam_search_initial_state', 
                                        'beam_search_initial_ids', 
                                        'beam_search_initial_logprobs'
                                        ], 
                                        feed_dict= {
                                          tf.get_collection('input_text_feed')[0] : [word_ids]
                                        })

  print('inital_state_shape', np.shape(initial_state))
  #[1, beam_size]
  ids = ids[0]
  logprobs = logprobs[0]

  print(ids, text2ids.ids2text(ids))
  print('logprob', logprobs)
  print('prob', [math.exp(x) for x in logprobs])
  print('inital_state', initial_state[0])

  print('first step using time(ms):', timer.elapsed_ms())

  timer = gezi.Timer()

  input_feed = np.array(ids)
  state_feed = np.array([initial_state[0]] * len(ids))
  print('input_feed_shape', np.shape(input_feed))
  print('state_feed_shape', np.shape(state_feed))
  #state_feed = np.array(initial_state)

  state, ids, logprobs = predictor.inference([
                                        'beam_search_state', 
                                        'beam_search_ids', 
                                        'beam_search_logprobs'
                                        ], 
                                        feed_dict= {
                                          tf.get_collection('beam_search_input_feed')[0] : input_feed,
                                          tf.get_collection('beam_search_state_feed')[0] : state_feed
                                        })

  #print(state)
  print(ids)
  print(logprobs)

  ids = ids[0]
  logprobs = logprobs[0]

  print(ids, text2ids.ids2text(ids))
  print('logprob', logprobs)
  print('prob', [math.exp(x) for x in logprobs])
  print('state', state[0])

  print('second step using time(ms):', timer.elapsed_ms())



def main(_):
  text2ids.init()
  predictor = melt.Predictor(FLAGS.model_dir)
  
  predict(predictor, "����̫����ô����")
  predict(predictor, "���������һ�Ը�Ů�ڿ�����ջ�͸����˿¶�δ���������ڿ�Ů��-�Ա���")
  predict(predictor, "����������ʵ��С��ô��,����������ʵ��С���δ�ʩ")

if __name__ == '__main__':
  tf.app.run()
