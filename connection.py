#!/usr/bin/python

import gevent
import gevent.pywsgi
from gevent import Greenlet

import signal
import struct
import socket
import time
import sys
import hashlib
import log
import cStringIO

from common import *
from bitcoin.coredefs import MIN_PROTO_VERSION
from bitcoin.messages import messagemap, msg_version, msg_ping, message_to_str

class Connection(Greenlet):
    def __init__(self, node, peersocket, address, port = None):
        # for incoming connection, port = None
        # for outgoing conneciton, socket = None
        Greenlet.__init__(self)
        self.node = node
        self.socket = peersocket
        self.dstaddr = address
        self.dstport = port
        self.recvbuf = ""
        self.last_sent = 0
        self.getblocks_ok = True
        self.last_block_rx = time.time()
        self.last_getblocks = 0
        self.hash_continue = None
        self.log = log
        self.ver_recv = MIN_PROTO_VERSION
        self.remote_height = -1

        if self.socket:
            self.direction = "INCOMING"
            print("in coming connection")
        else:
            self.socket = gevent.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.direction = "OUTGOING"
            print("outgoing connection!")
            print("connecting")
            try:
                self.socket.connect((self.dstaddr, self.dstport))
            except Exception, err:
                print "Exception: ", Exception, err
                print "Unable to establish connection"
                self.handle_close()
            self.sendVersionMessage()

    def sendVersionMessage(self):
        #stuff version msg into sendbuf
        vt = msg_version()
        vt.addrTo.ip = self.dstaddr
        vt.addrTo.port = self.dstport
        vt.addrFrom.ip = "0.0.0.0"
        vt.addrFrom.port = 0
        vt.nStartingHeight = self.node.chaindb.getheight()
        vt.strSubVer = MY_SUBVERSION
        self.send_message(vt)

    def _run(self):
        print  self.dstaddr, " connected"
        # wait for message and respond using hooks in node
        while True:
            try:
                data = self.socket.recv(1024)
                if len(data) <= 0: raise ValueError
            except (IOError, ValueError):
                self.handle_close()
                return
            self.recvbuf = self.recvbuf + data
            self.got_data()

    def handle_close(self):
        print self.dstaddr, " close"
        self.recvbuf = ""
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.close()
        except:
            pass

    def got_data(self):
        while True:
            if len(self.recvbuf) < 4:
                return
            if self.recvbuf[:4] != self.node.netmagic.msg_start:
                raise ValueError("got garbage %s" % repr(self.recvbuf))
            # check checksum
            if len(self.recvbuf) < 4 + 12 + 4 + 4:
                return
            command = self.recvbuf[4:4+12].split("\x00", 1)[0]
            msglen = struct.unpack("<i", self.recvbuf[4+12:4+12+4])[0]
            checksum = self.recvbuf[4+12+4:4+12+4+4]
            if len(self.recvbuf) < 4 + 12 + 4 + 4 + msglen:
                return
            msg = self.recvbuf[4+12+4+4:4+12+4+4+msglen]
            th = hashlib.sha256(msg).digest()
            h = hashlib.sha256(th).digest()
            if checksum != h[:4]:
                raise ValueError("got bad checksum %s" % repr(self.recvbuf))
            self.recvbuf = self.recvbuf[4+12+4+4+msglen:]

            if command in messagemap:
                f = cStringIO.StringIO(msg)
                t = messagemap[command](self.ver_recv)
                t.deserialize(f)
                self.node.got_message(self, t)
            else:
                print("UNKNOWN COMMAND %s %s" % (command, repr(msg)))

    def send_message(self, message):
        if verbose_sendmsg(message):
            print("send %s" % repr(message))
        tmsg = message_to_str(self.node.netmagic, message)
        try:
            self.socket.sendall(tmsg)
            self.last_sent = time.time()
        except Exception, err:
            print "Exception: ", Exception, err
            self.handle_close()
