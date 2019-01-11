import tensorflow as tf


class AveragePooling(object):
    """docstring for FastText"""

    def __init__(self, vocab_size, learning_rate, decay_steps, decay_rate, embed_size, sequence_length,
                 is_training, initializer=tf.random_normal_initializer(stddev=0.01), clip_gradients=5.0, decay_rate_big=0.50):
        self.vocab_size = vocab_size
        self.embed_size = embed_size
        self.sequence_length = sequence_length
        self.is_training = is_training
        self.initializer = initializer
        self.clip_gradients = clip_gradients
        # self.count = 0
        # add placeholder (X,label)
        self.input_x = tf.placeholder(tf.int32, [None, self.sequence_length], name="input_x")  # X
        self.input_length = tf.placeholder(tf.float32, [None, 1], name="input_length")  # X
        self.input_y = tf.placeholder(tf.float32, [None, 1], name="input_y")
        # self.actual = tf.placeholder(tf.float32, [None, 1], name="actual")
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")

        # self.pred = tf.placeholder(tf.int32, [None, 1], name="pred")  # X

        self.global_step = tf.Variable(0, trainable=False, name="Global_Step")
        self.epoch_step = tf.Variable(0, trainable=False, name="Epoch_Step")
        self.epoch_increment = tf.assign(self.epoch_step, tf.add(self.epoch_step, tf.constant(1)))
        self.decay_steps, self.decay_rate = decay_steps, decay_rate

        self.instantiate_weights()
        self.logits = self.inference()  # [None, self.label_size]. main computation graph is here.
        if not is_training:
            return
        self.loss_val = self.loss()
        self.lr = learning_rate
        self.lr_decay = tf.train.exponential_decay(learning_rate, self.epoch_step, self.decay_steps, self.decay_rate, staircase=False)
        self.train_op = self.train()

    def instantiate_weights(self):
        """define all weights here"""
        with tf.name_scope("embedding"):  # embedding matrix
            # [vocab_size,embed_size] tf.random_uniform([self.vocab_size, self.embed_size],-1.0,1.0)
            self.Embedding = tf.get_variable("Embedding", shape=[self.vocab_size, self.embed_size], initializer=self.initializer)
            self.W_projection = tf.get_variable("W_projection", shape=[self.embed_size,
                                                                       1], initializer=self.initializer)  # [embed_size,label_size]
            self.b_projection = tf.get_variable("b_projection", shape=[1], initializer=self.initializer)  # [label_size] #ADD 2017.06.09

    def inference(self):
        self.embedded_words = tf.nn.embedding_lookup(self.Embedding, self.input_x)
        self.embedded_texts_sum = tf.reduce_sum(self.embedded_words, axis=1)
        self.embedded_texts = tf.div(self.embedded_texts_sum, self.input_length)
        # with tf.name_scope("dropout"):
        #     self.h_drop = tf.nn.dropout(self.embedded_texts, keep_prob=self.dropout_keep_prob)  # [None,num_filters_total]
        # shape:[None, self.num_classes]==tf.matmul([None,self.embed_size],[self.embed_size,self.num_classes])
        # self.embedded_texts = tf.reduce_mean(self.embedded_words, axis=1)
        logits = tf.nn.sigmoid(tf.matmul(self.embedded_texts, self.W_projection) + self.b_projection)
        return logits

    def loss(self, l2_lambda=0.00001):  # 0.0001#this loss function is for multi-label classification
        with tf.name_scope("loss"):
            # losses = tf.nn.sigmoid_cross_entropy_with_logits(labels=self.input_y, logits=self.logits)
            # losses = tf.reduce_sum(losses, axis=1)  # shape=(?,). loss for all data in the batch
            # print("Use sigmoid_cross_entropy_with_logits.")
            # losses = tf.nn.softmax_cross_entropy_with_logits(labels=self.input_y, logits=self.logits)
            # print("Use softmax_cross_entropy_with_logits.")
            # loss = tf.reduce_mean(losses)  # shape=().   average loss in the batch
            loss = -tf.reduce_mean(tf.reduce_sum(self.input_y * tf.log(self.logits + 1e-10) + (1 - self.input_y) * tf.log(1 - self.logits + 1e-10), axis=1))
            l2_losses = tf.add_n([tf.nn.l2_loss(v) for v in tf.trainable_variables() if 'bias' not in v.name]) * l2_lambda
            loss = loss + l2_losses
            # self.count += 1
        return loss

    def train(self):
        """based on the loss, use SGD to update parameter"""
        train_op = tf.contrib.layers.optimize_loss(self.loss_val, global_step=self.global_step,
                                                   learning_rate=self.lr, optimizer="Adam", clip_gradients=self.clip_gradients)
        return train_op
