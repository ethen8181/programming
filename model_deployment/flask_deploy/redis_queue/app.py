# https://www.pyimagesearch.com/2018/01/29/scalable-keras-deep-learning-rest-api/
import uuid
import json
from redis import Redis
from threading import Thread
from flask import Flask, request, jsonify
from flask_deploy.redis_queue import utils, constants

app: Flask = Flask(__name__)
redis_client: Redis = Redis()


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
        ]
    }
    """
    raw_image = request.files.get('image')
    if raw_image is None:
        err_msg = {'message': "please pass an image in the body with 'image' as the key"}
        return jsonify(err_msg), 400

    image = utils.convert_image(raw_image)
    image_array = utils.prepare_image(image, target_size=(constants.IMAGE_WIDTH, constants.IMAGE_HEIGHT))

    image_id = str(uuid.uuid4())
    payload = {
        constants.REDIS_PAYLOAD_ID: image_id,
        constants.REDIS_PAYLOAD_IMAGE: utils.base64_encode_image(image_array)
    }
    redis_client.rpush(constants.REDIS_QUEUE_KEY, json.dumps(payload))

    while True:
        raw_predictions = redis_client.get(image_id)
        if raw_predictions is None:
            continue

        predictions = raw_predictions.decode(constants.IMAGE_ENCODING)
        data = {'predictions': json.loads(predictions)}
        redis_client.delete(image_id)
        return jsonify(data)


if __name__ == '__main__':
    thread = Thread(target=utils.score_image_queue, args=(redis_client,))
    thread.start()
    app.run()
