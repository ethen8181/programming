import os
import numpy as np
import tensorflow as tf
from subprocess import call
from tensorflow.contrib.tensorboard.plugins import projector


__all__ = ['launch_tensorboard']


def launch_tensorboard(embedding_path, log_dir, metadata_path = None, launch = False):
    """
    Visualizing embedding in Tensorboard [1]_.

    Parameters
    ----------
    embedding_path : str
        tsv file path that contains the embedding. Absolute path is strongly recommended.

    log_dir : str
        Logging directory. Absolute path is strongly recommended.

    metadata_path : str, default None
        Optional tsv file path that contains the embedding's corresponding metadata.
        If we were to have more than 1 column as the metadata, we can include a header.
        On the other hand, we only have 1 column as the metadata, then no header is allowed.
        Absolute path is strongly recommended.

    launch : bool, default False
        Whether to directly launch the tensorboard or not.

    References
    ----------
    .. [1] `Tensorflow Documentation: TensorBoard: Embedding Visualization
            <https://www.tensorflow.org/get_started/embedding_viz>`_
    """
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    # use last section of the file path as the embedding's tensorflow variable name
    # e.g. '/Users/ethen/logdir/topics.tsv', then the name would be 'topics'
    path, _ = os.path.splitext(embedding_path)
    path = path.split('/')[-1]
    embedding = np.genfromtxt(embedding_path, dtype = np.float32, delimiter = '\t')
    embedding_var = tf.Variable(embedding, name = path)

    # do a fake run of the model (not really running anything),
    # simply initialize the variable and save it to checkpoint
    saver = tf.train.Saver()
    init = tf.global_variables_initializer()
    model_checkpoint = os.path.join(log_dir, 'model.ckpt')

    with tf.Session() as sess:
        sess.run(init)
        saver.save(sess, model_checkpoint, global_step = 1)

    # boilerplate setup
    # we can add multiple embeddings, here we add only one
    config = projector.ProjectorConfig()
    config_embedding = config.embeddings.add()
    config_embedding.tensor_name = embedding_var.name

    if metadata_path is not None:
        # Link to its metadata file (e.g. labels that provides descriptions
        # for the each data points in the embeddings)
        config_embedding.metadata_path = metadata_path

    # use the same log_dir where we stored our model checkpoint
    summary_writer = tf.summary.FileWriter(log_dir)

    # the next line writes a projector_config.pbtxt in the log_dir
    # TensorBoard will read this file during startup
    projector.visualize_embeddings(summary_writer, config)

    # launch TensorBoard by passing the log directory
    if launch:
        call('tensorboard --logdir={}'.format(log_dir), shell = True)
