import os
import random
import threading
import time

class BitcoinpyDaemon(threading.Thread):
     def run(self):
         os.system('bitcoinpy')

class BitcoinpyMiner(threading.Thread):
     def run(self):
         os.system('minerpy')

def wait_until_blocks_are_generated(connection):
    # wait until you have generated some blocks
    while True:
        info = connection.getinfo()
        if info.blocks > 1:
            return info
        time.sleep(1)

def wait_until_n_blocks_are_generated(connection, n):
    info = connection.getinfo()
    old_num_of_blocks = info.blocks
    while True:
        info = connection.getinfo()
        if info.blocks >= n:
            return info
        time.sleep(1)

def wait_until_n_more_blocks_are_generated(connection, n):
    info = connection.getinfo()
    old_num_of_blocks = info.blocks
    while True:
        info = connection.getinfo()
        if info.blocks >= old_num_of_blocks + n:
            return info
        time.sleep(1)

def wait_until_account_has_balance(connection, address):
    # check for updated balance
    while True:
        account = connection.getaccount('account')
        subaccount = account[address]
        if subaccount['balance'] > 0:
            return subaccount
        time.sleep(1)

def get_total_balance(connection):
    account = connection.getaccount('account')
    total_balance = 0
    for subaccount in account.itervalues():
        total_balance = total_balance + subaccount['balance']
    return int(total_balance)
