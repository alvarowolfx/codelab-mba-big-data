#!/usr/bin/env python3

import time
import uuid

from pubsub import pub, sub


def main():
    while True:
        id = str(uuid.uuid4())
        print('Enviando pedido {} para fila'.format(id))
        pub('pedidos', bytes(id, 'utf-8'))
        time.sleep(10)


if __name__ == '__main__':
    main()
