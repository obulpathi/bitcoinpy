#!/usr/bin/python
#
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import gevent
import gevent.pywsgi
from gevent import Greenlet

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
import re
import hashlib
import rpc

import chaindb
import mempool
import log

from common import *
from bitcoin.core import *
from bitcoin.serialize import *
from bitcoin.messages import *
from bitcoin.coredefs import NETWORKS

settings = {}


class Node(Greenlet): # its not a greenlet .. its just a module
    def __init__(self, peermgr, log, mempool, chaindb, netmagic):
        Greenlet.__init__(self)
        self.log = log
        self.peermgr = peermgr
        self.mempool = mempool
        self.chaindb = chaindb
        self.netmagic = netmagic
        self.hash_continue = None
        self.ver_send = MIN_PROTO_VERSION

    # we don't need this function ... this module just needs to respond to outside function call
    def _run(self):
        self.log.write(self.dstaddr + " connected")
        while True:
            try:
                t = self.sock.recv(8192)
                if len(t) <= 0: raise ValueError
            except (IOError, ValueError):
                self.handle_close()
                return
            self.recvbuf += t
            self.got_data()

    def send_getblocks(self, connection, timecheck=True):
        if not connection.getblocks_ok:
            print "getblock_ok is false .. not fetching any blocks"
            return
        now = time.time()
        if timecheck and (now - connection.last_getblocks) < 5:
            print "time chack failed .. not getting blocks"
            return
        connection.last_getblocks = now
        our_height = self.chaindb.getheight()
        if our_height < 0:
            gd = msg_getdata(self.ver_send)
            inv = CInv()
            inv.type = 2
            inv.hash = self.netmagic.block0
            gd.inv.append(inv)
            connection.send_message(gd)
        elif our_height < self.remote_height:
            gb = msg_getblocks(self.ver_send)
            if our_height >= 0:
                gb.locator.vHave.append(self.chaindb.gettophash())
            connection.send_message(gb)

    def got_message(self, connection, message):
        gevent.sleep()
        if connection.last_sent + 30 * 60 < time.time():
            connection.send_message(msg_ping(self.ver_send))
        if verbose_recvmsg(message):
            self.log.write("recv %s" % repr(message))
        if message.command == "version":
            self.ver_send = min(PROTO_VERSION, message.nVersion)
            if self.ver_send < MIN_PROTO_VERSION:
                self.log.write("Obsolete version %d, closing" % (self.ver_send,))
                self.handle_close()
                return
            if (self.ver_send >= NOBLKS_VERSION_START and self.ver_send <= NOBLKS_VERSION_END):
                connection.getblocks_ok = False
            self.remote_height = message.nStartingHeight
            connection.send_message(msg_verack(self.ver_send))
            if self.ver_send >= CADDR_TIME_VERSION:
                connection.send_message(msg_getaddr(self.ver_send))
            self.send_getblocks(connection)
        elif message.command == "verack":
            self.ver_recv = self.ver_send
            if self.ver_send >= MEMPOOL_GD_VERSION:
                self.send_message(msg_mempool())
            self.send_getblocks(connection)
        elif message.command == "ping":
            if self.ver_send > BIP0031_VERSION:
                self.send_message(msg_pong(self.ver_send))
        elif message.command == "addr":
            self.peermgr.new_addrs(message.addrs)
        elif message.command == "inv":
            # special message sent to kick getblocks
            if (len(message.inv) == 1 and
                message.inv[0].type == MSG_BLOCK and
                self.chaindb.haveblock(message.inv[0].hash, True)):
                self.send_getblocks(False)
                return
            want = msg_getdata(self.ver_send)
            for i in message.inv:
                if i.type == 1:
                    want.inv.append(i)
                elif i.type == 2:
                    want.inv.append(i)
            if len(want.inv):
                self.send_message(want)
        elif message.command == "tx":
            if self.chaindb.tx_is_orphan(message.tx):
                self.log.write("MemPool: Ignoring orphan TX %064x" % (message.tx.sha256,))
            elif not self.chaindb.tx_signed(message.tx, None, True):
                self.log.write("MemPool: Ignoring failed-sig TX %064x" % (message.tx.sha256,))
            else:
                self.mempool.add(message.tx)
        elif message.command == "block":
            self.chaindb.putblock(message.block)
            self.last_block_rx = time.time()
        elif message.command == "getdata":
            self.getdata(connection, message)
        elif message.command == "getblocks":
            self.getblocks(message)
        elif message.command == "getheaders":
            self.getheaders(message)
        elif message.command == "getaddr":
            msg = msg_addr()
            msg.addrs =self.peermgr.random_addrs()
            connection.send_message(msg)
        elif message.command == "mempool":
            msg = msg_inv()
            for k in self.mempool.pool.iterkeys():
                inv = CInv()
                inv.type = MSG_TX
                inv.hash = k
                msg.inv.append(inv)
                if len(msg.inv) == 50000:
                    break
            self.send_message(msg)
        # if we haven't seen a 'block' message in a little while,
        # and we're still not caught up, send another getblocks
        last_blkmsg = time.time() - connection.last_block_rx
        if last_blkmsg > 5:
            connection.send_getblocks()

    def getdata_tx(self, txhash):
        if txhash in self.mempool.pool:
            tx = self.mempool.pool[txhash]
        else:
            tx = self.chaindb.gettx(txhash)
            if tx is None:
                return
        msg = msg_tx()
        msg.tx = tx
        self.send_message(msg)

    def getdata_block(self, connection, blkhash):
        block = self.chaindb.getblock(blkhash)
        if block is None:
            return
        msg = msg_block()
        msg.block = block
        connection.send_message(msg)
        if blkhash == self.hash_continue:
            self.hash_continue = None
            inv = CInv()
            inv.type = MSG_BLOCK
            inv.hash = self.chaindb.gettophash()
            msg = msg_inv()
            msg.inv.append(inv)
            connection.send_message(msg)

    def getdata(self, connection, message):
        if len(message.inv) > 50000:
            self.handle_close()
            return
        for inv in message.inv:
            if inv.type == MSG_TX:
                self.getdata_tx(inv.hash)
            elif inv.type == MSG_BLOCK:
                self.getdata_block(connection, inv.hash)

    def getblocks(self, message):
        blkmeta = self.chaindb.locate(message.locator)
        height = blkmeta.height
        top_height = self.getheight()
        end_height = height + 500
        if end_height > top_height:
            end_height = top_height
        msg = msg_inv()
        while height <= end_height:
            hash = long(self.chaindb.height[str(height)])
            if hash == message.hashstop:
                break
            inv = CInv()
            inv.type = MSG_BLOCK
            inv.hash = hash
            msg.inv.append(inv)
            height += 1
        if len(msg.inv) > 0:
            self.send_message(msg)
            if height <= top_height:
                self.hash_continue = msg.inv[-1].hash

    def getheaders(self, message):
        blkmeta = self.chaindb.locate(message.locator)
        height = blkmeta.height
        top_height = self.getheight()
        end_height = height + 2000
        if end_height > top_height:
            end_height = top_height
        msg = msg_headers()
        while height <= end_height:
            blkhash = long(self.chaindb.height[str(height)])
            if blkhash == message.hashstop:
                break
            db_block = self.chaindb.getblock(blkhash)
            block = copy.copy(db_block)
            block.vtx = []
            msg.headers.append(block)
            height += 1
        self.send_message(msg)
