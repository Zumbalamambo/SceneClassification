import os, datetime
import numpy as np
import tensorflow as tf
import CNNModels_joe

class vgg_seg1:
    def __init__(self, x, seg_labels, obj_class, lam, keep_dropout, train_phase):
        self.logits_seg = CNNModels2.VGG_Seg1(x, keep_dropout, train_phase, num_seg_classes=176, batch_norm=True, seg=True, random_init_seg_score_fr=True, debug=True)
        self.loss = loss_seg(seg_labels, self.logits_seg)

def loss_seg(label_seg, logits_seg):
    label_seg = tf.nn.softmax(label_seg)
    return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=label_seg, logits=logits_seg))

