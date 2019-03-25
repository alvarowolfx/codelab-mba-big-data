#!/usr/bin/env python3

import time
import json

from google.cloud import bigquery
from pubsub import sub, pub

client = bigquery.Client()


def query_images():
    query = """
        select t.image_id, t.original_url
        from `bigquery-public-data.open_images.images` t
        order by rand()
        limit 100
     """
    query_job = client.query(query)
    rows = query_job.result()
    df = rows.to_dataframe()
    output = df.to_json(orient='records')
    images = json.loads(output)
    return images


def main():
    images = query_images()
    for image in images:
        print(image)
        pub('photos', bytes(json.dumps(image), 'utf-8'))


if __name__ == '__main__':
    main()
