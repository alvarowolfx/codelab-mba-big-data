#!/usr/bin/env python3

import argparse
import time
import uuid
from google.cloud import pubsub_v1

from pubsub import sub, pub


def callback(message):
    id = str(message.data)
    print('Pedido Confirmado recebido {} com id {}'.format(message, id))

    print('Enviando pedido {} ao DW'.format(id))
    time.sleep(1)

    print('Pedido {} consolidado no DW'.format(id))

    message.ack()


def main():
    sub('pedidos-confirmados-dw', callback)


if __name__ == '__main__':
    main()
