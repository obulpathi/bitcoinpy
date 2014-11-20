from wallet import Wallet

wallet = Wallet()
account = wallet.getaccount()

toaddress = raw_input("Enter the address to send coins to: ")
amount = int(input("Enter the balance to transfer to address: "))

balance = 0
for subaccount in account.itervalues():
    balance = balance + subaccount['balance']

if balance < amount:
    print("Not enough balance")
    exit(1)

print "Transferring: ", amount, " \tto: ", toaddress
wallet.connection.sendtoaddress(toaddress, amount)
