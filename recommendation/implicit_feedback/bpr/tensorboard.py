import os
import numpy as np
import tensorflow as tf
from subprocess import call
from tensorflow.contrib.tensorboard.plugins import projector


def launch_tensorboard(embedding_file, log_dir, metadata_file = None):
    """

    References
    ----------
    Tensorflow Documentation: TensorBoard: Embedding Visualization
    - https://www.tensorflow.org/get_started/embedding_viz
    """
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    embedding = np.genfromtxt(embedding_file, dtype = np.float32, delimiter = '\t')
    embedding_var = tf.Variable(embedding, name = embedding_file.split('.')[0])

    # do a fake run of the model (not really running anything),
    # which simply initialize the variable and save it to checkpoint
    step = 1
    saver = tf.train.Saver()
    init = tf.global_variables_initializer()
    model_checkpoint = os.path.join(log_dir, 'model.ckpt')

    with tf.Session() as sess:
        sess.run(init)
        saver.save(sess, model_checkpoint, global_step = step)

    # boilerplate setup:
    # we can add multiple embeddings, here we add only one
    config = projector.ProjectorConfig()
    config_embedding = config.embeddings.add()
    config_embedding.tensor_name = embedding_var.name

    if metadata_file is not None:
        # Link to its metadata file (e.g. labels that provides descriptions
        # for the each data points in the embeddings)
        config_embedding.metadata_path = metadata_file

    # use the same log_dir where we stored our model checkpoint
    summary_writer = tf.summary.FileWriter(log_dir)

    # the next line writes a projector_config.pbtxt in the log_dir,
    # TensorBoard will read this file during startup
    projector.visualize_embeddings(summary_writer, config)

    # launch tensorboard
    call('tensorboard --logdir={}'.format(log_dir), shell = True)
