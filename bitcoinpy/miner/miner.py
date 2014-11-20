#!/usr/bin/python
#
# Copyright 2011 Jeff Garzik
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.

import time
import json
import pprint
import hashlib
import struct
import re
import base64
import httplib
import logging
import sys
import os
from time import sleep
from multiprocessing import Process

ERR_SLEEP = 15
GET_WORK_SLEEP = 30
MAX_NONCE = 1000000000000L

settings = {}
pp = pprint.PrettyPrinter(indent=4)

class BitcoinRPC:
    OBJID = 1

    def __init__(self, host, port, username, password, logger):
        authpair = "%s:%s" % (username, password)
        self.authhdr = "Basic %s" % (base64.b64encode(authpair))
        self.conn = httplib.HTTPConnection(host, port, False, 30)
        self.logger = logger

    def rpc(self, method, params=None):
        self.OBJID += 1
        obj = { 'version' : '1.1',
            'method' : method,
            'id' : self.OBJID }
        if params is None:
            obj['params'] = []
        else:
            obj['params'] = params
        self.conn.request('POST', '/', json.dumps(obj),
            { 'Authorization' : self.authhdr,
              'Content-type' : 'application/json' })

        resp = self.conn.getresponse()
        if resp is None:
            return None

        body = resp.read()
        resp_obj = json.loads(body)
        if resp_obj is None:
            self.logger.debug("JSON-RPC: cannot JSON-decode body")
            return None
        if 'error' in resp_obj and resp_obj['error'] != None:
            return resp_obj['error']
        if 'result' not in resp_obj:
            self.logger.debug("JSON-RPC: no result in object")
            return None

        return resp_obj['result']
    def getblockcount(self):
        return self.rpc('getblockcount')
    def getwork(self, data=None):
        self.logger.debug("Sleeping before going for get work")
        sleep(GET_WORK_SLEEP)
        return self.rpc('getwork', data)

def uint32(x):
    return x & 0xffffffffL

def bytereverse(x):
    return uint32(( ((x) << 24) | (((x) << 8) & 0x00ff0000) |
            (((x) >> 8) & 0x0000ff00) | ((x) >> 24) ))

def bufreverse(in_buf):
    out_words = []
    for i in range(0, len(in_buf), 4):
        word = struct.unpack('@I', in_buf[i:i+4])[0]
        out_words.append(struct.pack('@I', bytereverse(word)))
    return ''.join(out_words)

def wordreverse(in_buf):
    out_words = []
    for i in range(0, len(in_buf), 4):
        out_words.append(in_buf[i:i+4])
    out_words.reverse()
    return ''.join(out_words)

class Miner:
    def __init__(self, id, logger):
        self.id = id
        self.max_nonce = MAX_NONCE
        self.logger = logger

    def work(self, datastr, targetstr):
        self.logger.debug("datastr: {0}".format(datastr))
        self.logger.debug("targerstr: {0}".format(targetstr))
        # decode work data hex string to binary
        static_data = datastr.decode('hex')
        static_data = bufreverse(static_data)

        # the first 76b of 80b do not change
        blk_hdr = static_data[:76]

        # decode 256-bit target value
        targetbin = targetstr.decode('hex')
        # do not uncomment the following line
        #targetbin = targetbin[::-1] # byte-swap and dword-swap
        targetbin_str = targetbin.encode('hex')
        target = long(targetbin_str, 16)

        # pre-hash first 76b of block header
        static_hash = hashlib.sha256()
        static_hash.update(blk_hdr)

        for nonce in xrange(self.max_nonce):
            # encode 32-bit nonce value
            nonce_bin = struct.pack("<I", nonce)

            # hash final 4b, the nonce value
            hash1_o = static_hash.copy()
            hash1_o.update(nonce_bin)
            hash1 = hash1_o.digest()

            # sha256 hash of sha256 hash
            hash_o = hashlib.sha256()
            hash_o.update(hash1)
            hash = hash_o.digest()

            # quick test for winning solution: high 8 bits zero?
            if hash[-2:] != '\0\0':
                continue

            # convert binary hash to 256-bit Python long
            hash = bufreverse(hash)
            hash = wordreverse(hash)

            hash_str = hash.encode('hex')
            l = long(hash_str, 16)

            self.logger.debug("target: {0}".format(target))
            self.logger.debug("nonce: {0}".format(l))
            # proof-of-work test:  hash < target
            if l < target:
                self.logger.debug("PROOF-OF-WORK found: {0}".format(l))
                return (nonce + 1, nonce_bin)
            else:
                self.logger.debug("PROOF-OF-WORK found: false positive %064x".format(l))

        return (nonce + 1, None)

    def submit_work(self, rpc, original_data, nonce_bin):
        nonce_bin = bufreverse(nonce_bin)
        nonce = nonce_bin.encode('hex')
        solution = original_data[:152] + nonce + original_data[160:256]
        param_arr = [ solution ]
        result = rpc.getwork(param_arr)
        self.logger.debug("Upstream RPC result: {0}".format(result))

    def iterate(self, rpc):
        work = rpc.getwork()
        if work is None:
            time.sleep(ERR_SLEEP)
            return
        if 'data' not in work or 'target' not in work:
            time.sleep(ERR_SLEEP)
            return

        time_start = time.time()

        (hashes_done, nonce_bin) = self.work(work['data'], work['target'])

        time_end = time.time()
        time_diff = time_end - time_start

        self.max_nonce = long((hashes_done * settings['scantime']) / time_diff)
        if self.max_nonce > 0xfffffffaL:
            self.max_nonce = 0xfffffffaL

        if settings['hashmeter']:
            self.logger.debug("HashMeter({0}): {1} hashes, {2} Khash/sec".format(
                  self.id, hashes_done,
                  round((hashes_done / 1000.0) / time_diff, 2)))

        if nonce_bin is not None:
            self.submit_work(rpc, work['data'], nonce_bin)

    def loop(self):
        rpc = BitcoinRPC(settings['host'], settings['port'], settings['rpcuser'], settings['rpcpass'], self.logger)
        if rpc is None:
            return

        while True:
            self.iterate(rpc)

def miner_thread(id, logger):
    miner = Miner(id, logger)
    miner.loop()

def run(config_file = "~/.bitcoinpy-miner.cfg"):
    f = open(os.path.expanduser(config_file))
    for line in f:
        # skip comment lines
        m = re.search('^\s*#', line)
        if m:
            continue

        # parse key=value lines
        m = re.search('^(\w+)\s*=\s*(\S.*)$', line)
        if m is None:
            continue
        settings[m.group(1)] = m.group(2)
    f.close()

    if 'host' not in settings:
        settings['host'] = '127.0.0.1'
    if 'port' not in settings:
        settings['port'] = 8332
    if 'threads' not in settings:
        settings['threads'] = 1
    if 'hashmeter' not in settings:
        settings['hashmeter'] = 0
    if 'scantime' not in settings:
        settings['scantime'] = 30L
    if 'rpcuser' not in settings or 'rpcpass' not in settings:
        print "Missing username and/or password in cfg file"
        sys.exit(1)
    if 'log' not in settings or (settings['log'] == '-'):
        settings['log'] = None

    settings['port'] = int(settings['port'])
    settings['threads'] = int(settings['threads'])
    settings['hashmeter'] = int(settings['hashmeter'])
    settings['scantime'] = long(settings['scantime'])

    # setup logging
    if settings['log']:
        logging.basicConfig(filename=settings['log'], level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    thr_list = []
    for thr_id in range(settings['threads']):
        p = Process(target=miner_thread, args=(thr_id,logger))
        p.start()
        thr_list.append(p)
        time.sleep(1)           # stagger threads

    logger.debug("{0} mining threads started".format(settings['threads']))
    logger.debug("Miner Starts - {0}:{1}".format(settings['host'], settings['port']))
    try:
        for thr_proc in thr_list:
            thr_proc.join()
    except KeyboardInterrupt:
        pass
    logger.debug("Miner Stops - {0}:{1}".format(settings['host'], settings['port']))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: minerpy.py CONFIG-FILE"
        sys.exit(1)
    run(sys.argv[1])
