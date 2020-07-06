import json
import requests
import xpring
import sys

def pay_xrp_testnet(wallet_seed, address, amount):
    # Create a wallet instance using the seed
    wallet = xpring.Wallet.from_seed(wallet_seed)

    # The XRP testnet
    url = 'test.xrp.xpring.io:50051'
    client = xpring.Client.from_url(url)

    # Create a transaction
    txn = client.send(wallet, address, str(amount))

    # Submit txn to the network
    res = client.submit(txn)

    return res


def get_address_from_payid(payid, network, environment):
    # Convert the PayID into a URL e.g.
    # pay$username.github.io -> https://username.github.io/pay
    local_part, domain = payid.split('$')
    url = f'https://{domain}/{local_part}'
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    # Look for an address that matches the network
    # and environment we want to use
    for address in data['addresses']:
        if address['paymentNetwork'] == network and \
           address['environment'] == environment:
            return address['addressDetails']['address']
    

def main(args):
    """
    Given a dictionary. Return a dictionary.
    """

    # The wallet seed (secret key) is passed in, as a bound
    # parameter to this function
    xrp_wallet_seed = args['xrp_wallet_seed']


    # Extract the username of the pusher from the
    # Github hook payload
    pusher = args['pusher']['name']

    # Assume a PayID on Github of this form
    payid = f'pay${pusher}.github.io'

    # Calculate the amount based on number of commits
    # this is just an example and could be any metric
    try:
        num_commits = len(args['commits'])
    except KeyError:
        num_commits = 1
    amount = 1000 * num_commits
    
    # Get the address from the PayID and make payment
    address = get_address_from_payid(payid, 'XRPL', 'TESTNET')
    res = pay_xrp_testnet(xrp_wallet_seed, address, amount)

    return {
        'address': address,
        'amount': amount,
    }

if __name__ == "__main__":
    # Invoke with python webhook.py hammertoe snzBUmvTTAzCCRwGvGfKeA6Zqn4Yf
    args = {
        'pusher': {'name': sys.argv[1]},
        'xrp_wallet_seed': sys.argv[2]
    }
    main(args)
