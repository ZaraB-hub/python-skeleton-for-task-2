from unittest.mock import AsyncMock
from jcs import canonicalize
import json
from create_db import main as initialize_database  
from main import handle_object_msg,handle_getobject_msg,mk_object_msg,get_objid,gossip_object,validate_object_msg,handle_ihaveobject_msg

# Example of a mock writer setup
class MockWriter(AsyncMock):
    def __init__(self):
        super().__init__()
        self.sent_data = []  # Store messages sent for verification

    async def write(self, data):
        # Override write to store data instead of sending it
        self.sent_data.append(data.decode('utf-8'))  # Store as decoded string for easier inspection

    def get_sent_data(self):
        # Helper to retrieve all sent data for inspection
        return self.sent_data

    def reset_sent_data(self):
        # Clear the sent data log for fresh tests
        self.sent_data.clear()


coinbase_tx = {
    "object": {
        "height": 0,
        "outputs": [
            {
                "pubkey": "85acb336a150b16a9c6c8c27a4e9c479d9f99060a7945df0bb1b53365e98969b",
                "value": 50000000000000
            }
        ],
        "type": "transaction"
    },
    "type": "object"
}

spending_tx = {
    "object": {
        "inputs": [
            {
                "outpoint": {
                    "index": 0,
                    "txid": "d46d09138f0251edc32e28f1a744cb0b7286850e4c9c777d7e3c6e459b289347"
                },
                "sig": "6204bbab1b736ce2133c4ea43aff3767c49c881ac80b57ba38a3bab980466644cdbacc86b1f4357cfe45e6374b963f5455f26df0a86338310df33e50c15d7f04"
            }
        ],
        "outputs": [
            {
                "pubkey": "b539258e808b3e3354b9776d1ff4146b52282e864f56224e7e33e7932ec72985",
                "value": 10
            },
            {
                "pubkey": "8dbcd2401c89c04d6e53c81c90aa0b551cc8fc47c0469217c8f5cfbae1e911f9",
                "value": 49999999999990
            }
        ],
        "type": "transaction"
    },
    "type": "object"
}
coinbase_tx_id = get_objid(coinbase_tx["object"])
spending_tx_id = get_objid(spending_tx["object"])

import asyncio

async def test_grader_sends_and_requests():
    writer = MockWriter()  # Simulate the connection writer

    # Assume handle_object_msg and handle_getobject_msg are defined as discussed
    await handle_object_msg(coinbase_tx,None, writer)  # Grader sends coinbase_tx

    # Inspect that an ihaveobject message was sent
    ihave_msg = {"type": "ihaveobject", "objectid": coinbase_tx_id}
    assert json.dumps(ihave_msg) + '\n' in writer.get_sent_data(), "Failed to send ihaveobject message"

    # Reset and simulate Grader requesting the same object
    writer.reset_sent_data()
    await handle_getobject_msg({"type": "getobject", "objectid": coinbase_tx_id}, writer)

    # Inspect that the coinbase_tx was returned
    assert json.dumps(coinbase_tx) + '\n' in writer.get_sent_data(), "Failed to return requested object"

    print("Test 1 passed: Grader sends and requests transaction")

async def test_grader1_sends_grader2_requests():
    writer1 = MockWriter()  # Writer for Grader 1
    writer2 = MockWriter()  # Writer for Grader 2

    # Grader 1 sends the transaction
    await handle_object_msg(coinbase_tx,None, writer1)

    # Grader 2 requests the same object
    writer2.reset_sent_data()
    await handle_getobject_msg({"type": "getobject", "objectid": coinbase_tx_id}, writer2)

    # Inspect that Grader 2 received the object data
    assert json.dumps(coinbase_tx) + '\n' in writer2.get_sent_data(), "Failed to return requested object to Grader 2"

    print("Test 2 passed: Grader 1 sends, Grader 2 requests")

async def test_request_object_on_ihaveobject():
    writer = MockWriter()  # Simulate the connection writer

    # Simulate Grader 1 sending ihaveobject for a missing object
    ihaveobject_msg = {"type": "ihaveobject", "objectid": spending_tx_id}
    await handle_ihaveobject_msg(ihaveobject_msg, writer)

    # Inspect that getobject message was sent
    getobject_msg = {"type": "getobject", "objectid": spending_tx_id}
    assert json.dumps(getobject_msg) + '\n' in writer.get_sent_data(), "Failed to send getobject request for missing object"

    print("Test 3 passed: Node requests missing object on ihaveobject")

async def main():
    initialize_database()
    await test_grader_sends_and_requests()
    await test_grader1_sends_grader2_requests()
    await test_request_object_on_ihaveobject()


# Run all tests
asyncio.run(main())
