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


# Initialize a Publisher client
pub_client = pubsub_v1.PublisherClient()


def pub(topic_name, data):
    """Publishes a message to a Pub/Sub topic."""
    # [END pubsub_quickstart_pub_client]
    # Create a fully qualified identifier in the form of
    # `projects/{project_id}/topics/{topic_name}`
    topic_path = pub_client.topic_path(project_id, topic_name)

    # When you publish a message, the client returns a future.
    api_future = pub_client.publish(topic_path, data=data)
    api_future.add_done_callback(get_callback(api_future, data))

    # Keep the main thread from exiting until background message
    # is processed.
    while api_future.running():
        time.sleep(0.1)


sub_client = pubsub_v1.SubscriberClient()


def sub(subscription_name, callback):
    """Receives messages from a Pub/Sub subscription."""
    subscription_path = sub_client.subscription_path(
        project_id, subscription_name)

    sub_client.subscribe(subscription_path, callback=callback)
    print('Escutando mensagens no caminho {}..\n'.format(subscription_path))

    while True:
        time.sleep(60)
