# Wallet Defragger
This script will defragment the unspent transactions on your DeepOnion wallet address, squashing 67 inputs at a time.

## System Requiremnts
1. DeepOniond must be available to your $PATH.
2. DeepOnion.conf must contain rpcuser and rpcpassword configurations.
3. Wallet must be unlocked.
4. python3

## Usgage
`python3 wallet_dfragger.py <fromaddress> <toaddress>`

From address and to address can be the same and the script will also only allow you to defragment your wallet to an address you own.

Enjoy!

### Appendix
With minor changes, this scrypt can be used for any wallet daemon that supports the following commands.

* validateaddress
* listunspent
* createrawtransaction
* signrawtransaction
* sendrawtransaction
