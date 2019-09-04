from typing import Tuple

REDIS_QUEUE_KEY: str = 'image_queue'
REDIS_QUEUE_BATCH_SIZE: int = 32
REDIS_PAYLOAD_ID: str = 'id'
REDIS_PAYLOAD_IMAGE: str = 'image'
IMAGE_ENCODING = 'utf-8'
IMAGE_WIDTH: int = 224
IMAGE_HEIGHT: int = 224
IMAGE_CHANNEL: int = 3
IMAGE_DTYPE: str = 'float32'
IMAGE_SHAPE: Tuple[int, int, int] = (IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_CHANNEL)
IMAGE_SINGLE_BATCH_SHAPE: Tuple[int, int, int, int] = (1, *IMAGE_SHAPE)
