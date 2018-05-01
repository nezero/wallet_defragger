#!/usr/bin/python
import json
import subprocess
import sys
import traceback

class bcolours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def runCommandString(command):
    command = "DeepOniond {0}".format(command)
    if "listtransactions" not in command:
        logDebug("runCommand: {0}".format(command))
    stdoutdata = subprocess.getoutput(command)
    return stdoutdata

def runCommand(command):
    return json.loads(runCommandString(command))

def logDebug(msg):
    print(msg)

def logInfo(msg):
    print("{0}{1}{2}".format(bcolours.OKGREEN, msg, bcolours.ENDC))

def logWarn(msg):
    print("{0}{1}{2}".format(bcolours.WARNING, msg, bcolours.ENDC))

def logError(msg):
    print("{0}{1}{2}".format(bcolours.FAIL, msg, bcolours.ENDC))

def logCritical(msg):
    print("{0}{1}{2}{3}{4}".format(bcolours.BOLD, bcolours.UNDERLINE, bcolours.FAIL, msg, bcolours.ENDC))

def formatError(exc):
    failmsg = ""
    exc_type, exc_value, exc_traceback = sys.exc_info()
    exc_str = str(exc)
    if "unknown url type" in exc_str:
        logError("Invalid URL format, please try again with a valid server URL.")
    elif ("[Errno 101]" in exc_str):
        failmsg = "Waiting for network to come up."
    elif ("[Errno 111]" in exc_str):
        failmsg = "Connection refused. Server is down."
    else:
        failmsg = str(type(exc)) + ": " + str(exc) + "\n"
        stack = traceback.extract_tb(exc_traceback)
        if(stack != None):
            for f,ln,fn,text in stack:
                failmsg = failmsg + "File: " + f + "\n Line: " + repr(ln) + "\n  Function: " + fn + "\n" + text + "\n"
    logError(failmsg)
    if(exc_traceback != None):
        del exc_traceback;

def doSquash(transactions, toaddress):
    command = "createrawtransaction  '["
    total = 0

    # Create the raw transaction.
    first = True
    for transaction in transactions:
        comma = ""
        if first:
            first = False
        else:
            comma = ","

        command = command + comma + "{{\"txid\":\"{0}\",\"vout\":{1}}}".format(transaction["txid"], transaction["vout"])
        total = total + transaction["amount"]

    total = total - 0.001 # Transaction fee max
    logInfo("Fragment Total: {0}".format(total))

    command = command + "]' '{"
    command = "{0}\"{1}\":{2:.8f}".format(command,toaddress,total)
    command = command + "'}"
    tx_hex = runCommandString(command)
    tx_hex_signed = runCommandString("signrawtransaction {0}".format(tx_hex))
    index = tx_hex_signed.index('"hex" : "') + len('"hex" : "');
    tx_hex_signed = tx_hex_signed[index:]
    index = tx_hex_signed.index('"')
    tx_hex_signed = tx_hex_signed[:index]
    txid = runCommandString("sendrawtransaction {0}".format(tx_hex_signed))
    logDebug("Squashed transactions: {0}".format(txid))


def defrag(fromaddress, toaddress):
    global spentTransactions
    transactions = runCommand("listunspent 1 9999999 '[\"{0}\"]'".format(fromaddress))

    while len(transactions) > 0:
        squash = []
        for i in range(0, 67):
            if len(transactions) > 0:
                squash.append(transactions[0])
                logDebug("Squashing tx {0} at index {1}".format(transactions[0]["txid"], i))
                transactions.remove(transactions[0])
        if len(squash) > 0:
            doSquash(squash, toaddress)



if __name__ == "__main__":

    if len(sys.argv) == 3:
        try:
            # Print the version
            logInfo("DeepOnion Defragger v1.0.0")
            validFrom = runCommand("validateaddress {0}".format(sys.argv[1]))
            logInfo("{0}".format(validFrom))
            validTo = runCommand("validateaddress {0}".format(sys.argv[2]))
            logInfo("{0}".format(validTo))
            if validFrom["isvalid"] and validFrom["ismine"] and validTo["isvalid"] and validTo["ismine"]:
                defrag(sys.argv[1], sys.argv[2])
            else:
                logError("Addresses are not valid or yours. Only defrag to your own address.")
        except KeyboardInterrupt:
            logWarn("Exiting gracefully.")
        except Exception as e:
            formatError(e)
            logCritical("Exiting due to a Cirtical Error.")
        logInfo("Finished.")
    else:
        logError("Usage: ./onion_wallet_defrag.py <fromwallet> <towallet>")


