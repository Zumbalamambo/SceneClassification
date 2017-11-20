import os, datetime
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from DataLoaderOld import *
from architect import *
from exp import *
import sys
# Dataset Parameters
Parameters=sys.argv[1]
if Parameters =="exp1":
    settings = exp1
elif Parameters =="exp2":
    settings = exp2
elif Parameters =="exp3":
    settings = exp3
elif Parameters =="val":
    settings = expVal
else:
    print ("no dict of parameters found")
    assert 1==2
# Training Parameters
learning_rate = settings['learning_rate']
training_iters = settings['training_iters']
step_display = settings['step_display']
step_save = settings['step_save']
exp_name = settings['exp_name']
num = settings['num']
selectedmodel= settings['selectedmodel']

train = settings['train']
validation = settings['validation']

path_save = './save/'+exp_name+'/'
start_from=''
if len(num)>0:
    start_from = path_save+'-'+num

batch_size = 64
load_size = 256
fine_size = 224
c = 3
data_mean = np.asarray([0.45834960097,0.44674252445,0.41352266842])
dropout = 0.5 # Dropout, probability to keep units
# Construct dataloader
opt_data_train = {
    #'data_h5': 'miniplaces_256_train.h5',
    'data_root': './data/images/',   # MODIFY PATH ACCORDINGLY
    'data_list': './data/train.txt', # MODIFY PATH ACCORDINGLY
    'load_size': load_size,
    'fine_size': fine_size,
    'data_mean': data_mean,
    'randomize': True,
    'perm' : True
    }

opt_data_val = {
    #'data_h5': 'miniplaces_256_val.h5',
    'data_root': './data/images/',   # MODIFY PATH ACCORDINGLY
    'data_list': './data/val.txt',   # MODIFY PATH ACCORDINGLY
    'load_size': load_size,
    'fine_size': fine_size,
    'data_mean': data_mean,
    'randomize': False,
    'perm' : False
    }

loader_train = DataLoaderDisk(**opt_data_train)
loader_val = DataLoaderDisk(**opt_data_val)

print ("finish loading data")
# tf Graph input
x = tf.placeholder(tf.float32, [None, fine_size, fine_size, c])
y = tf.placeholder(tf.int64, None)
keep_dropout = tf.placeholder(tf.float32)
train_phase = tf.placeholder(tf.bool)

# # Construct model
# logits = alexnet(x, keep_dropout, train_phase)

if selectedmodel=="VGG":
    logits = VGG(x, keep_dropout, train_phase)
if selectedmodel=="VGG_BN":
    logits = VGG_BN(x, keep_dropout, train_phase)
if alexnet=="alexnet":
    logits = alexnet(x, keep_dropout, train_phase)  
# Define loss and optimizer
loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(labels=y, logits=logits))
train_optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(loss)

# Evaluate model
accuracy1 = tf.reduce_mean(tf.cast(tf.nn.in_top_k(logits, y, 1), tf.float32))
accuracy5 = tf.reduce_mean(tf.cast(tf.nn.in_top_k(logits, y, 5), tf.float32))

# define initialization
init = tf.global_variables_initializer()

# define saver
saver = tf.train.Saver()

# define summary writer
#writer = tf.train.SummaryWriter('.', graph=tf.get_default_graph())

# Launch the graph
with tf.Session() as sess:
    # Initialization
    if len(start_from)>1:
        saver.restore(sess, start_from)
    else:
        sess.run(init)

    def validation():
        # Evaluate on the whole validation set
        print('Evaluation on the whole validation set...')
        num_batch = loader_val.size()//batch_size+1
        acc1_total = 0.
        acc5_total = 0.
        loader_val.reset()
        for i in range(num_batch):
            images_batch, labels_batch = loader_val.next_batch(batch_size)    
            acc1, acc5 = sess.run([accuracy1, accuracy5], feed_dict={x: images_batch, y: labels_batch, keep_dropout: 1., train_phase: False})
            acc1_total += acc1
            acc5_total += acc5
            print("Validation Accuracy Top1 = " + "{:.4f}".format(acc1) + ", Top5 = " + "{:.4f}".format(acc5))
        acc1_total /= num_batch
        acc5_total /= num_batch
        print('Evaluation Finished! Accuracy Top1 = ' + "{:.4f}".format(acc1_total) + ", Top5 = " + "{:.4f}".format(acc5_total))
        return acc1_total,acc5_total
    
    step = 0

    if train:
        train_accs=[]
        val_accs=[]
        while step < training_iters:
            # Load a batch of training data
            images_batch, labels_batch = loader_train.next_batch(batch_size)
            
            if step % step_display == 0:
                print('[%s]:' %(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                # Calculate batch loss and accuracy on training set
                l, acc1, acc5 = sess.run([loss, accuracy1, accuracy5], feed_dict={x: images_batch, y: labels_batch, keep_dropout: 1., train_phase: False}) 
                print("-Iter " + str(step) + ", Training Loss= " + \
                      "{:.6f}".format(l) + ", Accuracy Top1 = " + \
                      "{:.4f}".format(acc1) + ", Top5 = " + \
                      "{:.4f}".format(acc5))
                train_accs.append(acc5)

                # # Calculate batch loss and accuracy on validation set
                # images_batch_val, labels_batch_val = loader_val.next_batch(batch_size)    
                # l, acc1, acc5 = sess.run([loss, accuracy1, accuracy5], feed_dict={x: images_batch_val, y: labels_batch_val, keep_dropout: 1., train_phase: False}) 
                # print("-Iter " + str(step) + ", Validation Loss= " + \
                #       "{:.6f}".format(l) + ", Accuracy Top1 = " + \
                #       "{:.4f}".format(acc1) + ", Top5 = " + \
                #       "{:.4f}".format(acc5))
                acc1, acc5=validation()
                val_accs.append(acc5)

                fig = plt.figure()
                a=np.arange(1,len(val_accs)+1,1)
                print a
                print train_accs
                plt.plot(a,train_accs,'-',label='Training')
                plt.plot(a,val_accs,'-',label='Validation')
                plt.xlabel("Iteration")
                plt.ylabel("Accuracy")
                plt.legend()
                fig.savefig("./fig/pic_"+str(modelind)+".png")   # save the figure to file
                plt.close(fig)
                print "finish saving figure to view"

                
            
            # Run optimization op (backprop)
            sess.run(train_optimizer, feed_dict={x: images_batch, y: labels_batch, keep_dropout: dropout, train_phase: True})
            
            step += 1
            
            # Save model
            if step % step_save == 0 or step==1:
                saver.save(sess, path_save, global_step=step)
                print("Model saved at Iter %d !" %(step))
        print("Optimization Finished!")

    if validation:
        validation()
