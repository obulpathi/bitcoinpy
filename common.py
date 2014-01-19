import collections

MY_SUBVERSION = "/pynode:0.0.1/"

debugnet = False

def verbose_sendmsg(message):
    if debugnet:
        return True
    if message.command != 'getdata':
        return True
    return False


def verbose_recvmsg(message):
    skipmsg = {
        'tx',
        'block',
        'inv',
        'addr',
    }
    if debugnet:
        return True
    if message.command in skipmsg:
        return False
    return True

Received = collections.namedtuple('Received', 'txhash n value scriptPubKey')

