#!/usr/bin/python
#
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import gevent
import gevent.pywsgi
from gevent import Greenlet
from gevent.server import StreamServer

import os
import signal
import struct
import socket
import binascii
import time
import sys
import re
import random
import cStringIO
import copy
import shutil

import rpc
from wallet import Wallet
from log import Log
from node import Node
from mempool import MemPool
from chaindb import ChainDb
from connection import Connection
from peermanager import PeerManager
from bitcoin.coredefs import NETWORKS

settings = {}

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: bitcoinpy.py CONFIG-FILE")
        sys.exit(1)

    f = open(sys.argv[1])
    for line in f:
        m = re.search('^(\w+)\s*=\s*(\S.*)$', line)
        if m is None:
            continue
        settings[m.group(1)] = m.group(2)
    f.close()

    if 'host' not in settings:
        settings['host'] = '127.0.0.1'
    if 'port' not in settings:
        settings['port'] = 8333
    if 'rpcport' not in settings:
        settings['rpcport'] = 9332
    if 'db' not in settings:
        settings['db'] = '/tmp/chaindb'
    if 'chain' not in settings:
        settings['chain'] = 'mainnet'
    chain = settings['chain']
    if 'log' not in settings or (settings['log'] == '-'):
        settings['log'] = None

    if ('rpcuser' not in settings or
        'rpcpass' not in settings):
        print("You must set the following in config: rpcuser, rpcpass")
        sys.exit(1)

    settings['port'] = int(settings['port'])
    settings['rpcport'] = int(settings['rpcport'])
    settings['db'] = os.path.expanduser(settings['db'])

    log = Log(settings['log'])

    log.write("\n\n\n\n")

    if chain not in NETWORKS:
        log.write("invalid network")
        sys.exit(1)

    netmagic = NETWORKS[chain]

    datadir = settings['db']
    new_install = False
    # if datadir is not there, create and initialize
    if not os.path.isdir(datadir):
        new_install = True
        os.mkdir(datadir)
        os.mkdir(datadir + '/leveldb')
        # create blocks.dat file
        shutil.copy('genesis.dat', os.path.join(datadir + '/blocks.dat'))
        print os.path.join(datadir + '/blocks.dat')
        # create lock file for db
        with open(datadir + '/__db.001', 'a'):
            pass

    # create wallet
    wallet = Wallet()
    if new_install:
        # initialize wallet
        wallet.initialize()
    mempool = MemPool(log)
    chaindb = ChainDb(settings, settings['db'], log, mempool, wallet, netmagic, False, False)
    node = Node(None, log, mempool, chaindb, netmagic)
    peermgr = PeerManager(node, log, mempool, chaindb, netmagic)
    node.peermgr = peermgr
    wallet.chaindb = chaindb

    # load blocks.dat into db, if db is newly created
    if new_install:
        chaindb.loadfile(datadir + '/blocks.dat')
    
    if 'loadblock' in settings:
        chaindb.loadfile(settings['loadblock'])

    threads = []

    def new_connection_handler(socket, address):
        print "New incoming connection >>>>>>>>>>>"
        connection = Connection(node, socket, address)
        connection.start()

    # start HTTP server for JSON-RPC
    rpcexec = rpc.RPCExec(peermgr, mempool, chaindb, wallet, log, settings['rpcuser'], settings['rpcpass'])
    rpcserver = gevent.pywsgi.WSGIServer(('', settings['rpcport']), rpcexec.handle_request)
    rpc_server_thread = gevent.Greenlet(rpcserver.serve_forever)
    threads.append(rpc_server_thread)

    # start server
    server = StreamServer((settings['host'], settings['port']), new_connection_handler)
    server_thread = gevent.Greenlet(server.serve_forever)
    threads.append(server_thread)

    # connect to specified peers
    if 'peers' in settings and settings['peers']:
        for ipport in settings['peers'].split():
            peerip, peerport = ipport.split(":")
            peer = peermgr.add(peerip, int(peerport))
            threads.append(peer)
            time.sleep(2)

    # program main loop
    def start(timeout=None):
        for thread in threads:
            thread.start()
        try:
            gevent.joinall(threads, timeout=timeout, raise_error=True)
        finally:
            for t in threads: t.kill()
            gevent.joinall(threads)
            log.write('Flushing database...')
            del chaindb.db
            chaindb.blk_write.close()
            log.write('OK')

    start()
