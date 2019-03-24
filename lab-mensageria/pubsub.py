import argparse
import time
import os
from google.cloud import pubsub_v1

project_id = os.getenv('GCLOUD_PROJECT')


def get_callback(api_future, data):
    """Wrap message data in the context of the callback function."""

    def callback(api_future):
        try:
            print("Published message {} now has message ID {}".format(
                data, api_future.result()))
        except Exception:
            print("A problem occurred when publishing {}: {}\n".format(
                data, api_future.exception()))
            raise
    return callback


def pub(topic_name, data):
    """Publishes a message to a Pub/Sub topic."""
    # [START pubsub_quickstart_pub_client]
    # Initialize a Publisher client
    client = pubsub_v1.PublisherClient()
    # [END pubsub_quickstart_pub_client]
    # Create a fully qualified identifier in the form of
    # `projects/{project_id}/topics/{topic_name}`
    topic_path = client.topic_path(project_id, topic_name)

    # When you publish a message, the client returns a future.
    api_future = client.publish(topic_path, data=data)
    api_future.add_done_callback(get_callback(api_future, data))

    # Keep the main thread from exiting until background message
    # is processed.
    while api_future.running():
        time.sleep(0.1)


def sub(subscription_name, callback):
    """Receives messages from a Pub/Sub subscription."""
    client = pubsub_v1.SubscriberClient()
    subscription_path = client.subscription_path(
        project_id, subscription_name)

    client.subscribe(subscription_path, callback=callback)
    print('Escutando mensagens no caminho {}..\n'.format(subscription_path))

    while True:
        time.sleep(60)
