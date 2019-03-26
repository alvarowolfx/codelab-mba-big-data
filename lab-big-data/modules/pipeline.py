

import argparse
import logging
import json
from past.builtins import unicode

import apache_beam as beam
from apache_beam.io import WriteToText
import apache_beam.transforms.window as window
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.options.pipeline_options import StandardOptions


import keras
import numpy as np
import requests
from PIL import Image
from io import BytesIO

import tensorflow as tf
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.mobilenet import MobileNet
from keras.applications.mobilenet import preprocess_input, decode_predictions
# from keras.applications.imagenet_utils import decode_predictions


class KerasMobileNetDoFn(beam.DoFn):
    """
    Read files from url and classify using Keras
    """

    def __init__(self):
        self.model = None
        #self.session = None

    def load_resize_img(self, url):
        response = requests.get(url)
        img_bytes = BytesIO(response.content)
        img = load_img(img_bytes, target_size=(224, 224))
        return img

    def classify(self, url):
        original = self.load_resize_img(url)
        numpy_image = img_to_array(original)
        image_batch = np.expand_dims(numpy_image, axis=0)

        processed_image = preprocess_input(image_batch.copy())
        labels = []
        with self.graph.as_default():
            with self.session.as_default():
                predictions = self.model.predict(processed_image)
                labels = decode_predictions(predictions, top=5)
        return labels[0]

    def labels_to_dict(self, labels):
        output = dict()
        for lbl in labels:
            (id, name, prob) = lbl
            output[name] = "%.4f" % prob
        return output

    def start_bundle(self, context=None):
        graph = tf.Graph()
        with graph.as_default():
            session = tf.Session()
            with session.as_default():
                self.model = MobileNet(weights='imagenet')
                self.graph = graph
                self.session = session

    def process(self, element):
        try:
            image_id, original_url = element.element
        except AttributeError:
            image_id, original_url = element

        print(element)
        print(original_url)
        labels = self.classify(original_url)
        label_map = self.labels_to_dict(labels)

        yield image_id, original_url, label_map


class WriteToBigQuery(beam.PTransform):
    """Generate, format, and write BigQuery table row information."""

    def __init__(self, table_name, dataset, schema, project):
        """Initializes the transform.
        Args:
          table_name: Name of the BigQuery table to use.
          dataset: Name of the dataset to use.
          schema: Dictionary in the format {'column_name': 'bigquery_type'}
          project: Name of the Cloud project containing BigQuery table.
        """
        super(WriteToBigQuery, self).__init__()
        self.table_name = table_name
        self.dataset = dataset
        self.schema = schema
        self.project = project

    def get_schema(self):
        """Build the output table schema."""
        return ', '.join(
            '%s:%s' % (col, self.schema[col]) for col in self.schema)

    def expand(self, pcoll):
        return (
            pcoll
            | 'ConvertToRow' >> beam.Map(
                lambda elem: {col: elem[col] for col in self.schema})
            | beam.io.WriteToBigQuery(
                self.table_name, self.dataset, self.project, self.get_schema()))


class WriteToFile(beam.PTransform):

    def __init__(self, output):
        super(WriteToFile, self).__init__()
        self.output = output

    def format_result(self, result):
        # Format the counts into a PCollection of strings.
        (image_id, original_url, label_map) = result
        return '"%s","%s","%s"' % (image_id, original_url, json.dumps(label_map))

    def expand(self, pcoll):
        output = (pcoll
                  | 'Format' >> beam.Map(self.format_result)
                  | 'Encode' >> beam.Map(lambda x: x.encode('utf-8'))
                  .with_output_types(bytes))

        return output | 'Write to File' >> WriteToText(self.output)


def run_pipeline(options, known_args):
    p = beam.Pipeline(options=options)

    # Read from PubSub into a PCollection.
    if known_args.input_subscription:
        messages = (p | beam.io.ReadFromPubSub(
            subscription=known_args.input_subscription).with_output_types(bytes))
    else:
        messages = (p | beam.io.ReadFromPubSub(
            topic=known_args.input_topic).with_output_types(bytes))

    json_strings = messages | 'Decode' >> beam.Map(
        lambda x: x.decode('utf-8'))

    def get_image_url(json_str):
        d = json.loads(json_str)
        return d['image_id'], d['original_url']

    images = (json_strings | 'Get Image URL' >> beam.Map(get_image_url))

    results = (images
               | 'Classify using Mobilenet' >> beam.ParDo(KerasMobileNetDoFn()))

    # results | 'Write To File' >> WriteToFile(known_args.output)

    def format_result_dict(result):
        (image_id, original_url, label_map) = result
        return {
            'image_id': image_id,
            'original_url': original_url,
            'label_map': json.dumps(label_map)
        }

    (results
     | 'Format Results' >> beam.Map(format_result_dict)
     | 'Write to BigQuery' >> WriteToBigQuery(known_args.table_name, known_args.dataset, {
         'image_id': 'STRING',
         'original_url': 'STRING',
         'label_map': 'STRING'
     }, options.view_as(GoogleCloudOptions).project))

    result = p.run()
    result.wait_until_finish()


def run(argv=None):
    """Build and run the pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',
                        dest='output',
                        required=True,
                        help='Output file to write results to.')
    parser.add_argument('--dataset',
                        type=str,
                        required=True,
                        help='BigQuery Dataset to write tables to. '
                        'Must already exist.')
    parser.add_argument('--table_name',
                        default='photos_classification',
                        help='The BigQuery table name. Should not already exist.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--input_topic',
        help=('Input PubSub topic of the form '
              '"projects/<PROJECT>/topics/<TOPIC>".'))
    group.add_argument(
        '--input_subscription',
        help=('Input PubSub subscription of the form '
              '"projects/<PROJECT>/subscriptions/<SUBSCRIPTION>."'))
    known_args, pipeline_args = parser.parse_known_args(argv)

    # We use the save_main_session option because one or more DoFn's in this
    # workflow rely on global context (e.g., a module imported at module level).
    options = PipelineOptions(pipeline_args)
    if options.view_as(GoogleCloudOptions).project is None:
        parser.print_usage()
        print(sys.argv[0] + ': error: argument --project is required')
        sys.exit(1)
    options.view_as(SetupOptions).save_main_session = True
    options.view_as(StandardOptions).streaming = True

    run_pipeline(options, known_args)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
