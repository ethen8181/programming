# https://blog.keras.io/building-a-simple-keras-deep-learning-rest-api.html
import io
import numpy as np
import tensorflow as tf
from tensorflow.python.framework.ops import Graph
from flask import Flask, request, jsonify
from keras import Model
from keras.applications.resnet50 import ResNet50
from keras.applications import imagenet_utils
from keras.preprocessing.image import img_to_array
from PIL.ImageFile import Image, ImageFile
from typing import Tuple


app: Flask = Flask(__name__)

"""
Here, we've defined our model as a global variable instead of putting it
as a load variable in the /predict route, because the latter will imply
that the model will be loaded each and every time a new request comes in,
which can be inefficient.
"""
model: Model = None
graph: Graph = None


def load_model():
    """
    Load the pre-trained keras Resnet50 model, we can
    substitute this with other models as well.
    """
    global model
    model = ResNet50(weights='imagenet')

    """
    Some tensorflow hacks to get the inferencing code to work, where
    right after loading our model, we save the tensorflow graph, then
    during the prediction, we then do:

    with graph.as_default():
        (... do inference here...)

    https://github.com/tensorflow/tensorflow/issues/14356#issuecomment-385962623
    """
    global graph
    graph = tf.get_default_graph()


def convert_image(raw_image):
    """
    Convert image uploaded to flask (FileStorage) to a pillow image.

    References
    ----------
    https://stackoverflow.com/questions/41340296/how-can-pillow-open-uploaded-image-file-from-stringio-directly
    """
    return Image.open(io.BytesIO(raw_image.read()))


def prepare_image(image: ImageFile, target_size: Tuple[int, int]) -> np.ndarray:
    """
    Preprocess the pillow image prior to converting to a numpy array which
    the model accepts for inferencing.

    Parameters
    ----------
    image :
        Pillow image.

    target_size :
        Target size of the image. Will resize the input image to the specified size.
        e.g. for Imagenet Resnet50, the expected target size is 224, 224

    Returns
    -------
    image_array : 4d ndarray [batch size, width, height, channel]
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')

    image = image.resize(target_size)
    image_array = img_to_array(image)
    image_array = np.expand_dims(image_array, axis=0)
    return imagenet_utils.preprocess_input(image_array)


def score_image(image_array: np.ndarray, top: int):
    with graph.as_default():
        raw_prediction = model.predict(image_array)

    decoded_predictions = imagenet_utils.decode_predictions(raw_prediction, top)

    predictions = []
    for imagenet_id, label, prob in decoded_predictions[0]:
        prediction = {'label': label, 'prob': round(float(prob), 4)}
        predictions.append(prediction)

    return predictions


@app.route('/predict', methods=['POST'])
def predict():
    """
    Examples
    --------
    curl -X POST -F image=@dog.jpg 'http://localhost:5000/predict'

    {
        "predictions": [
            {
                "label": "beagle",
                "prob": 0.9878
            },
            {
                "label": "pot",
                "prob": 0.0021
            }
        ],
        "top": 2
    }
    """
    raw_image = request.files.get('image')
    if raw_image is None:
        err_msg = {'message': "please pass an image in the body with 'image' as the key"}
        return jsonify(err_msg), 400

    top = request.args.get('top', default=5, type=int)

    image = convert_image(raw_image)
    image_array = prepare_image(image, target_size=(224, 224))
    predictions = score_image(image_array, top)
    data = {'top': top, 'predictions': predictions}
    return jsonify(data)


if __name__ == '__main__':
    load_model()
    app.run()
