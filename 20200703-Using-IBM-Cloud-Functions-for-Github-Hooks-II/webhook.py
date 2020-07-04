import json
import requests
import xpring
import sys

def pay_xrp(reciever, mult=1):
    amount = int(1 * 1e6 * mult) # drops - ideally related to "value" of contribution...

    url = 'test.xrp.xpring.io:50051'
    client = xpring.Client.from_url(url)

    txn = client.send(PAYMENTS['xrp']['wallet'], reciever, str(amount)) # create txn
    res = client.submit(txn) # submit txn to the network

PAYMENTS = {
    'xrp': {
        'function': pay_xrp,
        'wallet': None
    },
    'btc': {
        'function': None,
        'wallet': None
    }
}

def make_payment(payid, mult=1):
    reciever = False
    for address in payid['addresses']:
        # Don't steal our imaginary imaginary money!
        if address['paymentNetwork'] == 'XRPL' and address['environment'] == 'TESTNET':
            reciever = address['addressDetails']['address']
            break
    if reciever:
        return PAYMENTS['xrp']['function'](reciever, mult)

def pay_pusher(code_pusher, mult=1):
    url = f'https://{code_pusher}.github.io/pay'
    response = requests.get(url)
    response.raise_for_status()
    payid = response.json()
    
    make_payment(payid, mult)

    result = f'I have paid {code_pusher}'
    return result

def main(args):
    """
    Given a dictionary. Return a dictionary.
    """
    payments = []
    xrp_sender = args.get('xrp_sender', None)
    if xrp_sender:
        PAYMENTS['xrp']['wallet'] = xpring.Wallet.from_seed(xrp_sender)
    # PAYMENTS['btc']['wallet'] = generate_bitcoin_wallet(args.get('btc_sender', None))
    pusher = f'{args["pusher"]["name"]}'
    url = f'https://{pusher}.github.io/pay'
    response = requests.head(url)
    # TODO: only pay on a merge to master (or pay on the PR, not the merge)
    # TODO: secure xrp_sender
    # TODO: deploy as function or action
    if response.status_code < 400:
        payments.append(pay_pusher(pusher, len(args['commits'])))
    return {
        'payments': payments
    }

if __name__ == "__main__":
    # Invoke with python webhook.py hammertoe snzBUmvTTAzCCRwGvGfKeA6Zqn4Yf
    args = {
        'pusher': {'name': sys.argv[1]},
        'xrp_sender': sys.argv[2]
    }
    main(args)
