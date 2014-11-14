#!/usr/bin/python
#
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import random
from node import Node
from connection import Connection

class PeerManager(object):
    def __init__(self, node, log, mempool, chaindb, netmagic):
        self.node = node
        self.log = log
        self.mempool = mempool
        self.chaindb = chaindb
        self.netmagic = netmagic
        self.peers = []
        self.addrs = {}
        self.tried = {}
        self.connections = []

    def add(self, host, port):
        self.log.write("PeerManager: connecting to %s:%d" % (host, port))
        self.tried[host] = True
        connection = Connection(self.node, None, host, port)
        self.connections.append(connection)
        # self.peers.append(peer)
        return connection

    def new_addrs(self, addrs):
        for addr in addrs:
            if addr.ip in self.addrs:
                continue
            self.addrs[addr.ip] = addr

        self.log.write("PeerManager: Received %d new addresses (%d addrs, %d tried)" % (len(addrs), len(self.addrs), len(self.tried)))

    def random_addrs(self):
        ips = self.addrs.keys()
        random.shuffle(ips)
        if len(ips) > 1000:
            del ips[1000:]

        vaddr = []
        for ip in ips:
            vaddr.append(self.addrs[ip])

        return vaddr

    def closeall(self):
        for peer in self.peers:
            peer.handle_close()
        self.peers = []
