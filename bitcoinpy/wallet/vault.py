from wallet import Wallet

class Vault(object):
    def __init__(self):
        self.wallet = Wallet()

    def getaccount(self):
        account = self.wallet.getaccount()
        return account

    def send(self):
        account = self.getaccount()
        if len(account) < 2:
            print("Not enough accounts to create vault, quitting")
            return 1

        balance = 0
        for subaccount in account.itervalues():
            balance = balance + subaccount['balance']

        if balance < 20:
            print("Not enough balance")
            return 2

        subaccount, vault_subaccount = list(account.itervalues())[:2]
        toaddress = subaccount['address']
        tomaster_address = vault_subaccount['address']
        timeout = 20
        amount = 20

        print("Transfering: %d toaddress: %s tomaster_address: %s" % \
             (amount, toaddress, tomaster_address))
        self.wallet.sendtovault(toaddress, tomaster_address, timeout, amount)
        return 0

    def withdraw(self):
        account = self.getaccount()

        fromaddress = ''
        toaddress = ''
        for subaccount in account.itervalues():
            if subaccount['address'][0] == '4':
                fromaddress = subaccount['address']
            if not toaddress and subaccount['address'][0] == '1':
                toaddress = subaccount['address']
            if fromaddress and toaddress:
                break

        if not fromaddress:
            print("No vault account, quitting")
            sys.exit(1)
        if not toaddress:
            print("No empty accounts, quitting")
            sys.exit(2)

        amount = 15
        print("Transfering: %d from address: %s to address: %s" % \
            (amount, fromaddress, toaddress))
        self.wallet.withdrawfromvault(fromaddress, toaddress, amount)
        return 0

    def fastwithdraw(self):
        account = self.getaccount()

        fromaddress = None
        toaddress = None
        for subaccount in account.itervalues():
            if not fromaddress and subaccount['address'][0] == '4' \
                and subaccount['balance'] >= 20:
                fromaddress = subaccount['address']
            elif not toaddress and subaccount['address'][0] == '1':
                toaddress = subaccount['address']
            if fromaddress and toaddress:
                break

        if not fromaddress:
            print("No vault accounts to send from, quitting")
            sys.exit(1)

        if not toaddress:
            print("No empty accounts to send, quitting")
            sys.exit(2)

        amount = 15
        print("Transfering: %d from address: %s to address: %s" % \
            (amount, fromaddress, toaddress))
        self.wallet.fastwithdrawfromvault(fromaddress, toaddress, amount)
        return 0
