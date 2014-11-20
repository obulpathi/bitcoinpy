from wallet import Wallet

wallet = Wallet()
account = wallet.getaccount()

balance = 0
for subaccount in account.itervalues():
    balance = balance + subaccount['balance']

vaults = wallet.getvaults()
emptyvaults = {}
for vault in vaults:
    if not vaults[vault]['balance']:
        emptyvaults[vault] = vaults[vault]

vaults = emptyvaults
vault_names = [vault for vault in vaults]
for count, vault in enumerate(vault_names):
    print count, ":", vault + " ", vaults[vault]['balance']

choice = int(input("Select the vault to transfer money to: "))
if choice < 0 or choice > len(vaults)-1:
    print("Invalid choice")
    exit(1)

vault_address = vault_names[choice]

amount = int(input("Enter the balance to transfer to vault: "))

if balance < amount:
    print("Not enough balance")
    exit(1)

print("Transfering %d to vault %s" % (amount, vault_address))
ret_value = wallet.sendtovault(vault_address, amount)
if not ret_value:
    print("An error occured while trasfering")
