
import keras
import numpy as np
import requests
from PIL import Image
from io import BytesIO

from keras.applications import mobilenet

from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.imagenet_utils import decode_predictions


class Classifier:
    def __init__(self):
        self.model = mobilenet.MobileNet(weights='imagenet')

    def load_resize_img(self, url):
        response = requests.get(url)
        img_bytes = BytesIO(response.content)
        img = load_img(img_bytes, target_size=(224, 224))
        return img

    def classify(self, url):
        original = self.load_resize_img(url)
        numpy_image = img_to_array(original)
        image_batch = np.expand_dims(numpy_image, axis=0)

        processed_image = mobilenet.preprocess_input(image_batch.copy())
        predictions = self.model.predict(processed_image)
        labels = decode_predictions(predictions)
        return labels[0]

    def labels_to_dict(self, labels):
        output = dict()
        for lbl in labels:
            (id, name, prob) = lbl
            output[name] = "%.4f" % prob
        return output


def main():
    c = Classifier()
    urls = [
        'https://c3.staticflickr.com/4/3900/15094647589_26b372f4d8_o.jpg',
        'https://farm1.staticflickr.com/2135/5812679118_04e855591f_o.jpg',
        'https://farm7.staticflickr.com/2652/4086229070_bd50174cae_o.jpg',
        'https://c3.staticflickr.com/4/3900/15094647589_26b372f4d8_o.jpg']
    for url in urls:
        labels = c.classify(url)
        label_map = c.labels_to_dict(labels)
        print(label_map)


if __name__ == '__main__':
    main()
