import io
import json
import time
import base64
import numpy as np
from redis import Redis
from keras import Model
from keras.applications.resnet50 import ResNet50
from keras.applications import imagenet_utils
from keras.preprocessing.image import img_to_array
from PIL.ImageFile import Image, ImageFile
from typing import Tuple, List
from flask_deploy.redis_queue import constants


def base64_encode_image(image_array: np.ndarray) -> str:
    image_c_ordered = image_array.copy(order='C')
    encoded_image = base64.b64encode(image_c_ordered).decode(constants.IMAGE_ENCODING)
    return encoded_image


def base64_decode_image(encoded_image: str) -> np.ndarray:
    decoded_image = base64.decodebytes(encoded_image.encode(constants.IMAGE_ENCODING))
    image = np.frombuffer(decoded_image, dtype=constants.IMAGE_DTYPE)
    return image.reshape(*constants.IMAGE_SINGLE_BATCH_SHAPE)


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


def score_images(model: Model, image_array: np.ndarray, top: int=2) -> List[List[Tuple[str, str, np.float32]]]:
    raw_prediction = model.predict(image_array)
    return imagenet_utils.decode_predictions(raw_prediction, top)


def parse_image_queue(image_queue: List[bytes]) -> Tuple[List[str], np.ndarray]:
    image_ids = []
    image_batch_shape = (len(image_queue), *constants.IMAGE_SHAPE)
    image_batch = np.zeros(image_batch_shape, dtype=constants.IMAGE_DTYPE)

    for idx, queue in enumerate(image_queue):
        payload = json.loads(queue.decode(constants.IMAGE_ENCODING))
        image_id = payload[constants.REDIS_PAYLOAD_ID]
        image = base64_decode_image(payload[constants.REDIS_PAYLOAD_IMAGE])
        image_batch[idx] = image
        image_ids.append(image_id)

    return image_ids, image_batch


def score_image_queue(redis_client: Redis):
    """
    Load the pre-trained keras Resnet50 model, we can
    substitute this with other models as well.
    """
    model = ResNet50(weights='imagenet')

    while True:
        image_queue = redis_client.lrange(constants.REDIS_QUEUE_KEY, 0, constants.REDIS_QUEUE_BATCH_SIZE - 1)
        if not image_queue:
            continue

        image_ids, image_batch = parse_image_queue(image_queue)
        decoded_predictions = score_images(model, image_batch)
        for image_id, decoded_prediction in zip(image_ids, decoded_predictions):
            predictions = []
            for imagenet_id, label, prob in decoded_prediction:
                prediction = {'label': label, 'prob': round(float(prob), 4)}
                predictions.append(prediction)

            redis_client.set(image_id, json.dumps(predictions))

        redis_client.ltrim(constants.REDIS_QUEUE_KEY, len(image_ids), -1)
