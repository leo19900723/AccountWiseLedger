from Blockchain import *


class AccountWiseLedger(object):

    def __init__(self, ownerID, subNetwork, powDifficulty=4, transactionBalance=0, transactionTask=None, transactionTaskHandler=None, blockchain=None):
        self.__ownerID = ownerID
        self.__subNetwork = subNetwork
        self.__powDifficulty = powDifficulty
        self.__transactionBalance = transactionBalance
        self.__transactionTask = json.loads(json.dumps(transactionTask)) if transactionTask else {}
        self.__transactionTaskHandler = json.loads(json.dumps(transactionTaskHandler)) if transactionTask else {}

        self.__blockchain = Blockchain.createByJsonBytes(json.dumps(blockchain)) if blockchain else Blockchain(self.__ownerID, self.__powDifficulty)

    @classmethod
    def createByJsonBytes(cls, inputStr):
        input = json.loads(inputStr)
        return cls(input["ownerID"], input["subNetwork"], input["powDifficulty"], input["transactionBalance"], input["transactionTask"], input["transactionTaskHandler"], input["blockchain"])

    def __str__(self):
        return str(self.outputDict)

    def __repr__(self):
        return str(self.outputDict)
    
    def __len__(self):
        return len(self.__blockchain)

    def setTransaction(self, task, handlerDict):
        if task["senderID"] == self.__ownerID or task["receiverID"] == self.__ownerID:
            self.__transactionTask = task
            self.__transactionTaskHandler = handlerDict
            self.__transactionBalance += task["amount"] if task["receiverID"] == self.__ownerID else -task["amount"]
            return True
        else:
            return False
    
    def createNewBlock(self, task, preHash, taskAbortSignal=False):
        return Blockchain.createNewBlock(self.__powDifficulty, Blockchain.hash256(task), task["senderID"], task["receiverID"], task["amount"], preHash, taskAbortSignal)

    def receiveResult(self, block):
        if block["msg"] == "Task Abort":
            self.__transactionTask = {}
            self.__transactionTaskHandler = {}
            self.__transactionBalance += block["amount"] if block["senderID"] == self.__ownerID else -block["amount"]
            return False

        elif self.__transactionTask["senderID"] == block["senderID"] and self.__transactionTask["receiverID"] == block["receiverID"] and self.__transactionTask["amount"] == block["amount"] and self.__blockchain.append(block):
            self.__transactionTask = {}
            self.__transactionTaskHandler = {}
            self.__transactionBalance += block["amount"] if block["senderID"] == self.__ownerID else -block["amount"]
            return True

        return False

    @property
    def viewOwnerID(self):
        return self.__ownerID

    @property
    def viewSubNetwork(self):
        return self.__subNetwork

    @property
    def viewPowDifficulty(self):
        return self.__powDifficulty

    @property
    def viewActualBalance(self):
        return self.__blockchain.viewBalance

    @property
    def viewPendingBalance(self):
        return self.__transactionBalance

    @property
    def viewPlanningBalance(self):
        return self.__transactionBalance + self.__blockchain.viewBalance

    @property
    def viewTransactionTask(self):
        return self.__transactionTask

    @property
    def viewTransactionTaskHandler(self):
        return self.__transactionTaskHandler

    @property
    def viewLastBlock(self):
        return self.__blockchain.viewLastBlock

    @property
    def viewBlockchain(self):
        return self.__blockchain.viewBlockchain

    @property
    def outputDict(self):
        ans = {
            "ownerID": self.__ownerID,
            "subNetwork": self.__subNetwork,
            "powDifficulty": self.__powDifficulty,
            "transactionBalance": self.__transactionBalance,
            "transactionTask": self.__transactionTask,
            "transactionTaskHandler": self.__transactionTaskHandler,
            "blockchain": self.__blockchain.outputDict}
        return ans

    @property
    def outputJsonBytes(self):
        return json.dumps(self.outputDict).encode()


def __unitTest():
    testAccount = AccountWiseLedger("testOwner", "A")
    testTask = {
        "senderID": "testSender",
        "receiverID": "testOwner",
        "amount": 1500
    }

    print("New Transaction Creation: ", testAccount.setTransaction(testTask, {"HandlerA": True, "HandlerB": True}))
    print("Actual, Pending, Planning Balance: ", testAccount.viewActualBalance, testAccount.viewPendingBalance, testAccount.viewPlanningBalance)
    testBlock = testAccount.createNewBlock(testTask, Blockchain.hash256(testAccount.viewLastBlock))
    print("Transaction Handler: ", testAccount.viewTransactionTaskHandler.keys())
    print("Block Append:", testAccount.receiveResult(testBlock))
    print(testAccount, testAccount.viewActualBalance, testAccount.viewPendingBalance)

    testTask = {
        "senderID": "testOwner",
        "receiverID": "testReceiver",
        "amount": 500
    }

    print("New Transaction Creation: ", testAccount.setTransaction(testTask, {"HandlerA": True, "HandlerB": True}))
    print("Actual, Pending, Planning Balance: ", testAccount.viewActualBalance, testAccount.viewPendingBalance, testAccount.viewPlanningBalance)
    testBlock = testAccount.createNewBlock(testTask, Blockchain.hash256(testAccount.viewLastBlock))
    print("Transaction Handler: ", testAccount.viewTransactionTaskHandler.keys())
    print("Block Append:", testAccount.receiveResult(testBlock))
    print(testAccount, testAccount.viewActualBalance, testAccount.viewPendingBalance)

    print(AccountWiseLedger.createByJsonBytes(testAccount.outputJsonBytes))

    return


if __name__ == "__main__":
    __unitTest()
