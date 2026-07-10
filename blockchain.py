import hashlib
import datetime


class Blockchain:

    def __init__(self):
        self.chain = []

    def create_transaction(
        self,
        product_id,
        sender,
        receiver,
        location,
        previous_hash="0000"
    ):

        timestamp = str(datetime.datetime.now())

        data = (
            product_id +
            sender +
            receiver +
            location +
            timestamp +
            previous_hash
        )

        current_hash = hashlib.sha256(
            data.encode()
        ).hexdigest()

        block = {
            "product_id": product_id,
            "sender": sender,
            "receiver": receiver,
            "location": location,
            "timestamp": timestamp,
            "hash": current_hash,
            "previous_hash": previous_hash
        }

        self.chain.append(block)

        return block

    def get_last_hash(self):

        if len(self.chain) == 0:
            return "0000"

        return self.chain[-1]["hash"]

    def is_valid(self):

        for i in range(1, len(self.chain)):

            if self.chain[i]["previous_hash"] != self.chain[i-1]["hash"]:
                return False

        return True