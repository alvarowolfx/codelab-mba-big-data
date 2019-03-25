#!/usr/bin/env python3

import argparse
import time
import uuid
from google.cloud import pubsub_v1

from pubsub import sub, pub


def callback(message):
    id = str(message.data)
    print('Pedido recebido {} com id {}'.format(message, id))

    print('Processando pedido com id {}'.format(id))
    time.sleep(3)

    print('Processamento finalizado para pedido com id {}'.format(id))
    pub('pedidos-confirmados', bytes(id, 'utf-8'))

    print('Pedido {} enviado a fila de confirmados'.format(id))
    message.ack()

    print('Pedido confirmado {}\n'.format(id))


def main():
    sub('pedidos-sub', callback)


if __name__ == '__main__':
    main()
