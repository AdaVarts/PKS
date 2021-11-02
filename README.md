# Protocols
The project is part of PKS curriculum WS 2019. The goal is to create a TCP protocol over a UDP in order to get a better understanding of the protocols' working principles. The project is done entirely in Python.

# Implementation

At the beginning we need to connect 2 nodes: write the IP-address of the nodes: ours and the one to which we will send messages. Then we need to establish the function of each node, whether it will be client or server (this can be changed during the running program).
## The protocol's header contains 13 bytes: 
type - 5 bytes \
serial number (of fragment) - 4 bytes \
length - 2 bytes \
checksum - 2 btes \

## Message types: when sending the messages, the "type" field in header contains the message type.
0file - file's fragment \
1file - repeat a file's fragment \
1text - repeats a fragment of text \
0 - wrong fragment (server requests to send the wrong fragment again) \
1 - ack (server response) \
2 - keep alive? \
3 - keep alive \
4 - break connection \
5 - number of fragments, type (the client sends a message to the server that we will now send some number of fragments, which at the end need to be composed into a file of some type or text) \
6 - text message \
7 - the client has changed its node to the receiver (now it is a server), therefore the server can be the sender (client) \

## Client 
The client can specify the size of the fragments (but not larger than 1500 - 20 - 8 - 13 = 1459 bytes; 20 - IP header, 8 - UDP header, 13 - implemented header) sent by the node, then the size may be changed during the program. The client sends a connection request to the server and waits for an ACK. \
There are 4 options: the client can send a text message from the console, a file from the computer, resize the fragment or change its node to the server. If the message is larger than the specified fragment size, the program divides it into fragments that will be sent sequentially to the server as packets. Before sending, if the user chooses, it is possible to flaw one fragment. If the server receives a message that a fragment is damaged or missing, the fragment will be sent again. Or the packets are sent again, if there is no response from the client about previous package after the certain amount of time passed. \
The program sends fragments in packages of 5 fragments; resends fragments if they did not arrive correctly one by one. \
When the server asks the client “Stay in connection? (Y / N): ”, the client can end the connection or prolong it. \

## Server
After the connection is established, the server waits a fixed period of time (50s) for a packet from the client. If that time passed, the server sends a question to the client whether it should close the connection or it has to wait. \
When a packet arrives to the server, it verifies them if any fragment is corrupted, or not all of them were recieved, the server sends a response - which fragment/-s the client must send again. If all fragments are fine, the server sends an ACK. When the last fragment arrives, the server verifies again that all of them have been recieved, if not - it asks the client for the missing fragments. In case everything is correct - the server sends the full address where the saved file is located or "ACK" for the whole text message. \
If a client changes its node to a server, the server can change that node to a client and send messages. \
