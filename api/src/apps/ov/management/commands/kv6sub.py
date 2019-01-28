# pylint:disable=E1101
# pylint: disable=unbalanced-tuple-unpacking
import gzip
import logging
import time
from datetime import datetime

import zmq
from dateutil.tz import tzlocal
from django.core.management.base import BaseCommand
from django.db import connection

from apps.ov.bulk_inserter import bulk_inserter
from apps.ov.kv6xml import Kv6XMLProcessor
from apps.ov.models import OvRaw

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
KV6KEY = "KV6posinfo"
PUBLISHER = "tcp://pubsub.besteffort.ndovloket.nl:7658"
TIMEOUTMS = 60


class KV6Client(object):
    def __init__(self, publisher=PUBLISHER):
        self.stop = False
        self.context = zmq.Context()
        self.sock = None
        self.publisher = publisher
        self.inserter = bulk_inserter(table=OvRaw, batch_size=10)
        self.postproc = Kv6XMLProcessor()

    def __del__(self):
        if self.sock is not None:
            self.sock.close()
        if self.context is not None:
            self.context.term()

    def subscribe(self):
        try:
            self.sock = self.context.socket(zmq.SUB)
            log.info(f'Subscribing to {self.publisher}')
            self.sock.connect(self.publisher)
            self.sock.setsockopt(zmq.RCVTIMEO, 2 * TIMEOUTMS * 1000)
            self.sock.setsockopt_string(zmq.SUBSCRIBE, "")
            return True
        except Exception as err:
            log.error(err)
            return False

    def message_loop(self):
        while True:
            try:
                if self.stop:
                    # we need to close the connection within the
                    # thread, else it will be kept alive
                    connection.close()
                    log.info('Stop: Terminating message loop')
                    break
                [envelop, contents] = self.sock.recv_multipart()
                envelop = envelop.decode('utf-8')
                # contents is transferred as gzipped uni code
                log.info(f'{envelop} received')
                if KV6KEY in envelop:
                    record = OvRaw(feed=envelop, xml=contents)
                    self.inserter.add(record)
                    decompressed = gzip.decompress(record.xml).decode('utf-8')
                    now = datetime.now(tzlocal())
                    self.postproc.process(now, decompressed)
                else:
                    log.info(f'Skipping envelop {envelop}')
            # Timed out, close connection and try to reconnect.
            # (network could have been interrupted)
            except zmq.error.Again:
                log.info('EAgain')
                if self.sock is not None:
                    self.sock.close()
                break
            except Exception as err:
                log.error(err)

    def subscribe_and_process(self):
        while True:
            if self.subscribe():
                self.message_loop()
                log.info('Timed out, trying to reconnect...')
            else:
                log.info(f'Connection failed, sleeping {0.5 * TIMEOUTMS} (ms)')
            if self.stop:
                connection.close()
                log.info('Stop: Terminating pubsub')
                break
            time.sleep(0.5 * TIMEOUTMS)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('url', type=str, nargs='?')

    def handle(self, *args, **options):
        addr = None if 'url' not in options else options['url']
        client = KV6Client() if addr is None else KV6Client(addr)
        client.subscribe_and_process()