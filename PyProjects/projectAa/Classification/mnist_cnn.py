from tensorflow.examples.tutorials.mnist import input_data
import tensorflow as tf


# hello = tf.constant("Hello Tensorflow!")
# sess=tf.Session()
# print(sess.run(hello))


# 用于构建2层的卷积神经网络
def deepnn(x):
    # 因为卷积会利用到空间信息，所以要将1D的转化为2D的，所以要把数据给的1 * 784转为28 * 28d的
    # 图片最终尺寸为[-1,28,28,1]，-1是样本不固定的意思，最后一维代表图片的颜色通道数（灰度图为1，rgb彩色图为3）
    x_image = tf.reshape(x, [-1, 28, 28, 1])

    # 第一层卷积
    # [卷积核的高度，卷积核的宽度，输入的通道数量，输出的通道数量]
    W_conv1 = weight_variable([5, 5, 1, 32])
    # 每一个输出通道都有一个对应的偏置量，长度为32的向量
    b_conv1 = bias_variable([32])
    # relu函数，即f(x) = max(0, x)
    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)

    # 第二层卷积
    W_conv2 = weight_variable([5, 5, 32, 64])
    b_conv2 = bias_variable([64])
    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    # 这里的边长经历了两个池化，只剩1/4，卷积核数量为64，故共还有参数7*7*64
    h_pool2 = max_pool_2x2(h_conv2)

    # 全连接层，共1024个神经元
    W_fc1 = weight_variable([7 * 7 * 64, 1024])
    b_fc1 = bias_variable([1024])
    # 不管你有多少个样本数量，反正第二维就是图片全展开的列
    h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    # 为了减少过拟合，下面加一个Dropout层，这个是通过一个placeholder传入keep_prob比率来控制
    # 这个是通过随机丢弃一部分节点的数据来减轻过拟合，这个Dropout的作用和正则很相似
    keep_prob = tf.placeholder(tf.float32)
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    # softmax层，最后把全连接层连接到一个个数为10的输出层
    W_fc2 = weight_variable([1024, 10])
    b_fc2 = bias_variable([10])
    y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

    return y_conv, keep_prob


# 定义权重和偏置的初始化函数，后面会重复调用
def weight_variable(shape):
    # 截断的正态分布噪声，标准差为0.1，这里值大于2倍标准差的都被干掉了
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)
# 用于分配系数
def bias_variable(shape):
    # 偏置，加微弱的正值，避免死亡节点
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


# 定义卷积层、池化层的函数
def conv2d(x, W):
    # conv2d是二维卷积，x是输入，W是参数，如[5,5,1,32]前面两个是尺寸
    # 第三个是channel，单色是1，RGB是3，第4个是卷积核数量
    # SAME是保持输入输出尺寸一样
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')
# pooling函数,平面数据的pool模板2*2，平面数据滑动步长2*2（非重叠的pool）
def max_pool_2x2(x):
    # 这里都是横竖降成一半，每二个取灰度最大的那个，保留最显著的特征
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')


# 读取数据
mnist = input_data.read_data_sets('../data/MNIST_data/', one_hot=True)
# 定义图片和标签的占位符，x是输入的图像，y_是对应的标签，None表示不限输入维度
x = tf.placeholder(tf.float32, [None, 784])
y_ = tf.placeholder(tf.float32, [None, 10])

y_conv, keep_prob = deepnn(x)

# 定义损失函数，使用优化器Adam，学习率设为1e-4
# 这里的resuce_mean就是普通的均值，不传axis就默认全局均值
cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y_conv), reduction_indices=[1]))
# 用交叉熵来计算loss
# cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))
# AdamOptimizer调参
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

# 定义评测准确率
# tf.argmax就是从一个Tensor中找到值最大的序号
# equal判断相等就返回True
# tf.cast把correct_prdiction的bool转成float32，e.g.[1,0,1,0]
correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# 开始训练，初始化所有参数
# keep_prob=o.5,mini-batch50,iter=20000（注，cpu跑这个量还是有点蛋疼）,样本数量为100w，每100次对准确率进行评估
# 添加用于初始化变量的节点，然后求出来
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    for i in range(20000):
        # batch队列，每次50张图片
        batch = mnist.train.next_batch(50)
        # 每100次迭代输出一次日志
        if i % 100 == 0:
            # t.eval()时，等价于：tf.get_default_session().run(t)
            # accuracy run不影响训练
            train_accuracy = accuracy.eval(feed_dict={x: batch[0], y_: batch[1], keep_prob: 1.0})
            print("step %d, training accuracy %g" % (i, train_accuracy))
        # train_step run就会改变值了
        train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})
    # 验证最终的准确率
    print("test accuracy :%g" % accuracy.eval(feed_dict={x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0}))
