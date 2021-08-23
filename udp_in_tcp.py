# Yelyzaveta Klysa 2019
import socket
import threading 
from threading import Timer
import time
import hashlib 
import os
import sys

print("Enter local IP: ")
localIP = input()
print("Enter second host IP: ")
serverIP = input()
global posArray
global recievedFrag
global servAsk
servAsk = 0

def timeFinish(clientSocket):
    print("Time is over")
    msgFromServer = clientSocket.recvfrom(1500)
    if (((msgFromServer[0])[0:5]).decode() == "00002"):
        global servAsk
        servAsk = 1
        print("Server request: keep alive connection? (Y/N):")

def timeServFinish(serverSocket, clientAddr):
    print("Time is over, sending the question")
    message = str.encode("00002")
    serverSocket.sendto(message, clientAddr)

def newTimerServ(serverSocket, clientAddr):
    global timer
    timer = Timer(50.0, timeServFinish, args=[serverSocket, clientAddr])

def timerClient(clientSocket):
    global timerCl
    timerCl = Timer(49.0, timeFinish, args=[clientSocket])

# checksum from internet
def calc_checksum(string):
    '''
    Calculates checksum for sending commands to the ELKM1.
    Sums the ASCII character values mod256 and takes
    the Twos complement.
    '''
    sum = 0
    for i in range(len(string)):
        sum = sum + ord(string[i])

    temp = sum % 256  # mod256
#    rem = (temp ^ 0xFF) + 1  # two's complement, hard way (one's complement + 1)
    rem = -temp  # two's complement, easier way
    return '%2X' % (rem & 0xFF)
# checksum from internet

def makeMistake(head):
    head += ("00").encode()
    return head

def requestFragments(serverSocket, clientAddr, posArr, recievedFrag, amountOfFrag):
    if(recievedFrag != amountOfFrag):
        if(len(posArr)>=5 and
            (posArr[-1] != 0 or posArr[-2] != 0 or posArr[-3] != 0 or posArr[-4] != 0 or posArr[-5] !=0)):
            reqFrag = []
            j = 0
            for i in range(1, amountOfFrag, 1):
                if(posArr[i] == 0):
                    reqFrag.insert(j, i)
                    j += 1
        else:
            reqFrag = []
            j = 0
            k = 0
            for i in range(1, amountOfFrag, 1):
                if(posArr[i] == 0):
                    reqFrag.insert(j, i)
                    j += 1
                    k = 1
                if(k == 1 and i%5 == 0):
                    break
        if (len(reqFrag) != 0):
            strFrag = ""
            for k in range(j):
                strFrag += str(reqFrag[k]) + "+"
            # checkS
            checkS = calc_checksum(strFrag).encode()
            head = str.encode("00000") + (0).to_bytes(4, byteorder="big") + (len(strFrag)+13).to_bytes(2, byteorder="big") + checkS + str.encode(strFrag)
            serverSocket.sendto(head, clientAddr)
            
def tBadFragment(serverSocket, clientAddr, posArr, recievedFrag, amountOfFrag):
    global tBad
    tBad = Timer(2.0, requestFragments, args=[serverSocket, clientAddr, posArr, recievedFrag, amountOfFrag])

while(True):
    clientOrServer = 0
    print("select mode client/server: ")
    mode = input()

    if(mode == "client"):
        clientOrServer = 1
        print("Enter buffer size: ")
        bufferSize = int(input())
        if(bufferSize>1459 or bufferSize<1): #1500-20-8-13 = 1459
            while(bufferSize>1459):
                print("Size can't be more then 1449 bytov")
                bufferSize = int(input())
        serverAddressPort = (serverIP, 12345)
        clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        headerMes = str.encode("conne")
        clientSocket.sendto(headerMes, serverAddressPort)
        msgFromServer = clientSocket.recvfrom(1500)
        if (((msgFromServer[0])[0:5]).decode() == "conne"):
            print("Connection with server is set")
            timerClient(clientSocket)
            timerCl.start()
            while(True):
                print("Available functions:\nfile - send file\ntext - send text message from console\nset buffer size - set new buffer size\nchange mode - to change your mode")
                print("Enter command: ")
                timerCl.cancel()
                timerClient(clientSocket)
                timerCl.start()
                command = input()
                if(servAsk == 1 and command == "Y"):
                    head = str.encode("00003")
                    clientSocket.sendto(head, (serverIP, 12345))
                    servAsk = 0
                    timerCl.cancel()
                    timerClient(clientSocket)
                    timerCl.start()
                    continue
                elif(servAsk == 1 and command == "N"):
                    timerCl.cancel()
                    head  = str.encode("00004")
                    clientSocket.sendto(head, serverAddressPort)
                    clientSocket.close()
                    clientOrServer = 0
                    break
                elif(command=="file"):
                    timerCl.cancel()
                    print("Enter the file type (ex. pdf, txt..): ")
                    typ = input()
                    typ = "."+typ
                    print("Enter file path: ")
                    path = input()
                    print("Make mistake? (Y/N): ")
                    mis = input()
                    bytesToSend = open(path, "rb").read()  
                    amountOfFragments =  len(range(0, len(bytesToSend), bufferSize))
                    print("amount of fragments: " + str(amountOfFragments))
                    # checkS
                    checkS = (calc_checksum(typ+","+str(amountOfFragments))).encode()
                    headerMes = str.encode("00005") + int(0).to_bytes(4, byteorder="big") + (len(typ+","+str(amountOfFragments))+13).to_bytes(2, byteorder="big") + checkS + (str(typ+","+str(amountOfFragments))).encode()
                    clientSocket.sendto(headerMes, serverAddressPort)

                    msgFromServer = clientSocket.recvfrom(1500)
                    
                    if (((msgFromServer[0])[0:5]).decode() == "00001"):
                        print("ACK information")
                        j = 0
                        fileArr = []
                        for i in range(0, len(bytesToSend), bufferSize):
                            fileArr.insert(j, bytesToSend[i:(i+bufferSize)])
                            j += 1
                        j = 0
                        for i in range(0, len(bytesToSend), bufferSize):
                            # checkS
                            checkS = (calc_checksum(hashlib.md5(bytesToSend[i:(i+bufferSize)]).hexdigest())).encode()
                            head = str.encode("0file") + (int(i/bufferSize)).to_bytes(4, byteorder="big") + (len(bytesToSend[i:(i+bufferSize)])+13).to_bytes(2, byteorder="big") 
                            
                            if(j == 1 and mis == "Y"):
                                head = makeMistake(head)
                            else:
                                head += checkS
                            messageFrCl = head + bytesToSend[i:(i+bufferSize)]
                            
                            clientSocket.sendto(messageFrCl, serverAddressPort)
                            print(str(int(i/bufferSize)))
                            j += 1
                            if(j%5==0 or i+bufferSize>=len(bytesToSend)):
                                msgFromServer = clientSocket.recvfrom(1500)
                                if(((msgFromServer[0])[0:5]).decode() == "00001"):
                                    print("ACK")
                                elif(((msgFromServer[0])[0:5]).decode() == "00001" and len(msgFromServer[0].decode())>6):
                                    print(msgFromServer[0][5:len(msgFromServer[0].decode())])
                                elif(((msgFromServer[0])[0:5]).decode() == "00000"):
                                    print("bad fragment")
                                    fragArray = (msgFromServer[0][13:int.from_bytes(msgFromServer[0][9:11], byteorder="big")]).decode().split("+")
                                    
                                    while(True):
                                        k = 0
                                        while(len(fragArray) != 1):
                                            head = str.encode("1file") + (int(fragArray[k])).to_bytes(4, byteorder="big") + (len(fileArr[int(fragArray[k])])+13).to_bytes(2, byteorder="big") 
                                            # checkS
                                            head += (calc_checksum(hashlib.md5(fileArr[int(fragArray[k])]).hexdigest())).encode()
                                            messageFrCl = head + fileArr[int(fragArray[k])]
                                            clientSocket.sendto(messageFrCl, serverAddressPort)
                                            print(str(int(fragArray[k])))
                                            msgFromServer = clientSocket.recvfrom(1500)
                                            if(int.from_bytes(msgFromServer[0][5:7], byteorder="big")==int(fragArray[k])):
                                                del fragArray[k]
                                                k = 0
                                            if(((msgFromServer[0])[0:5]).decode() == "00001"):
                                                print("ACK")
                                        if(len(fragArray)==1):
                                                break
                            if(i+bufferSize>=len(bytesToSend)):
                                while(True):
                                    msgFromServer = clientSocket.recvfrom(1500)
                                    if(((msgFromServer[0])[0:5]).decode() == "00001" and len(msgFromServer[0].decode())>6):
                                        print("ACK")
                                        print((msgFromServer[0][5:len(msgFromServer[0].decode())]).decode())
                                        break
                                    elif(((msgFromServer[0])[0:5]).decode() == "00000"):
                                        print("bad fragment")
                                        fragArray = (msgFromServer[0][13:int.from_bytes(msgFromServer[0][9:11], byteorder="big")]).decode().split("+")
                                        
                                        while(True):
                                            k = 0
                                            while(len(fragArray) != 1):
                                                head = str.encode("1file") + (int(fragArray[k])).to_bytes(4, byteorder="big") + (len(fileArr[int(fragArray[k])])+13).to_bytes(2, byteorder="big") 
                                                # checkS
                                                head += (calc_checksum(hashlib.md5(fileArr[int(fragArray[k])]).hexdigest())).encode()
                                                messageFrCl = head + fileArr[int(fragArray[k])]
                                                clientSocket.sendto(messageFrCl, serverAddressPort)
                                                print(str(int(fragArray[k])))
                                                msgFromServer = clientSocket.recvfrom(1500)
                                                if(int.from_bytes(msgFromServer[0][5:7], byteorder="big")==int(fragArray[k])):
                                                    del fragArray[k]
                                                    k = 0
                                                if(((msgFromServer[0])[0:5]).decode() == "00001"):
                                                    print("ACK")
                                            if(len(fragArray)==1):
                                                    break
                                        msgFromServer = clientSocket.recvfrom(1500)
                                        if(((msgFromServer[0])[0:5]).decode() == "00001" and len(msgFromServer[0].decode())>6):
                                            print("ACK")
                                            print((msgFromServer[0][5:len(msgFromServer[0].decode())]).decode())
                elif(command=="text"):
                    timerCl.cancel()
                    print("Enter your message:")
                    messageFromClient = input()
                    bytesToSend = str.encode(messageFromClient)

                    print("Make mistake? (Y/N)")
                    mis = input()

                    amountOfFragments = len(range(0, len(messageFromClient), bufferSize))
                    print("amount of fragments: " + str(amountOfFragments))
                    # checkS
                    checkS = (calc_checksum(str("00006"+","+str(amountOfFragments)))).encode()
                    headerMes = str.encode("00005") + int(0).to_bytes(4, byteorder="big") + (len(str("00006" + "," + str(amountOfFragments)))+13).to_bytes(2, byteorder="big") + checkS + (str("00006"+","+str(amountOfFragments))).encode()
                    clientSocket.sendto(headerMes, serverAddressPort)

                    msgFromServer = clientSocket.recvfrom(1500)
                    if (((msgFromServer[0])[0:5]).decode() == "00001"):
                        print("ACK information")
                        j = 0
                        textArr = []
                        for i in range(0, len(messageFromClient), bufferSize):
                            textArr.insert(j, messageFromClient[i:i+bufferSize])
                            j += 1
                        j = 0
                        for i in range(0, len(messageFromClient), bufferSize):
                            message = str.encode(messageFromClient[i:i+bufferSize])
                            numberOfFragment = (int(j)).to_bytes(4, byteorder="big")
                            length = (len(messageFromClient[i:i+bufferSize])+13).to_bytes(2, byteorder="big")
                            # checkS
                            checkS = (calc_checksum(messageFromClient[i:i+bufferSize])).encode()
                            header  = str.encode("00006") + numberOfFragment + length
                            if(j == 1 and mis == "Y"):
                                header = makeMistake(header)
                            else:
                                header += checkS
                            fragment = header + message
                            clientSocket.sendto(fragment, serverAddressPort)
                            print(str(j))
                            j += 1
                            if(j%5==0 or i+bufferSize>=len(messageFromClient)):
                                msgFromServer = clientSocket.recvfrom(1500)
                                if(((msgFromServer[0])[0:5]).decode() == "00001"):
                                    print("ACK")
                                elif(((msgFromServer[0])[0:5]).decode() == "00000"):
                                    print("bad fragment")
                                    textArray = (msgFromServer[0][13:int.from_bytes(msgFromServer[0][9:11], byteorder="big")]).decode().split("+")
                                    while(True):
                                        k = 0
                                        while(len(textArray) != 1):
                                            head = str.encode("1text") + (int(textArray[k])).to_bytes(4, byteorder="big") + (len(textArr[int(textArray[k])])+13).to_bytes(2, byteorder="big") 
                                            # checkS
                                            head += (calc_checksum(textArr[int(textArray[k])])).encode()
                                            messageFrCl = head + (textArr[int(textArray[k])]).encode()
                                            clientSocket.sendto(messageFrCl, serverAddressPort)
                                            print(str(int(textArray[k])))
                                            msgFromServer = clientSocket.recvfrom(1500)
                                            if(int.from_bytes(msgFromServer[0][5:7], byteorder="big")==int(textArray[k])):
                                                del textArray[k]
                                                k = 0
                                            if(((msgFromServer[0])[0:5]).decode() == "00001"):
                                                print("ACK")
                                        if(len(textArray)==1):
                                                break
                            if(i+bufferSize>=len(messageFromClient)):
                                while(True):
                                    msgFromServer = clientSocket.recvfrom(1500)
                                    if(((msgFromServer[0])[0:5]).decode() == "00001" and len(msgFromServer[0].decode())>6):
                                        print("ACK for the whole message")
                                        break
                                    elif(((msgFromServer[0])[0:5]).decode() == "00001"):
                                        print("ACK")
                                    elif(((msgFromServer[0])[0:5]).decode() == "00000"):
                                        textArray = (msgFromServer[0][13:int.from_bytes(msgFromServer[0][9:11], byteorder="big")]).decode().split("+")
                                        while(True):
                                            k = 0
                                            while(len(textArray) != 1):
                                                head = str.encode("1text") + (int(textArray[k])).to_bytes(4, byteorder="big") + (len(textArr[int(textArray[k])])+13).to_bytes(2, byteorder="big") 
                                                # checkS
                                                head += (calc_checksum(textArr[int(textArray[k])])).encode()
                                                messageFrCl = head + (textArr[int(textArray[k])]).encode()
                                                clientSocket.sendto(messageFrCl, serverAddressPort)
                                                print(str(int(textArray[k])))
                                                msgFromServer = clientSocket.recvfrom(1500)
                                                if(int.from_bytes(msgFromServer[0][5:7], byteorder="big")==int(textArray[k])):
                                                    del textArray[k]
                                                    k = 0
                                                if(((msgFromServer[0])[0:5]).decode() == "00001"):
                                                    print("ACK")
                                            if(len(textArray)==1):
                                                    break
                elif(command=="set buffer size"):
                    timerCl.cancel()
                    print("Enter buffer size")
                    bufferSize = int(input())
                    if(bufferSize>1449):
                        while(bufferSize>1449):
                            print("Size can't be more then 1449 bytov")
                            bufferSize = int(input())
                elif(command=="break connection"):
                    timerCl.cancel()
                    header  = str.encode("00004")
                    clientSocket.sendto(header, serverAddressPort)
                    clientSocket.close()
                    clientOrServer = 0
                    break
                elif(command == "change mode"):
                    timerCl.cancel()
                    header = str.encode("00007")
                    clientSocket.sendto(header, serverAddressPort)
                    clientSocket.close()
                    clientOrServer = 2
                    break
    elif(mode == "server"):
        clientOrServer = 2
        bufferSize = 1500
        
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.bind((localIP, 12345))
        print("UDP server up and listening")
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]

        if((message[0:5]).decode() == "conne"):
            newTimerServ(UDPServerSocket, address) 
            msgFromServer = str.encode("conne")
            UDPServerSocket.sendto(msgFromServer, address)
            timer.start()
            print("Connection with client is set")
        amountOfFrag = 0
        i = 0
        while(True):
            timer.cancel()
            newTimerServ(UDPServerSocket, address)
            timer.start()
            bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
            message = bytesAddressPair[0]
            address = bytesAddressPair[1]


            timer.cancel()
            typ = (message[0:5]).decode()
            if(typ == "00005"):
                # checkS
                checkS = (calc_checksum((message[13:int.from_bytes(message[9:11], byteorder="big")]).decode()))
                if(checkS == (message[11:13]).decode()):

                    mesArray = (message[13:int.from_bytes(message[9:11], byteorder="big")]).decode().split(",")
                    amountOfFrag = int(mesArray[1])
                    print("amount of fragments: "+str(amountOfFrag))
                    recievedFrag = 0

                    if((message[13:18]).decode() == "00006"):
                        textMsg = []
                        posArray = []
                        for i in range(amountOfFrag):
                            posArray.insert(i, 0)
                        msgFromServer = str.encode("00001") + int(0).to_bytes(2, byteorder="big") + int(13).to_bytes(2, byteorder="big") + (1).to_bytes(2, byteorder="big")
                        UDPServerSocket.sendto(msgFromServer, address)
                        tBadFragment(UDPServerSocket, address, posArray, recievedFrag, amountOfFrag)
                        tBad.start()
                        timer.cancel()

                        while(True):
                            bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
                            message = bytesAddressPair[0]
                            tBad.cancel()
                            tBadFragment(UDPServerSocket, address, posArray, recievedFrag, amountOfFrag)
                            tBad.start()
                            length = len(message)-13

                            # checkS
                            checkS = calc_checksum((message[13:13+length]).decode())
                            if(checkS == (message[11:13]).decode()):
                                recievedFrag += 1
                                position = int.from_bytes(message[5:9], byteorder="big")
                                if(posArray[position] != 0):
                                    recievedFrag -=1
                                else:
                                    textMsg.insert(position, (message[13:13+length]).decode())
                                posArray[position] = position
                                
                                if((message[0:5]).decode() == "1text"):
                                    print("I'm at ACK")
                                    msgFromServer = str.encode("00001") + int(position).to_bytes(2, byteorder="big")
                                    UDPServerSocket.sendto(msgFromServer, address)
                                if(recievedFrag%5 == 0 or recievedFrag == amountOfFrag):
                                    print("I'm at ACK")
                                    msgFromServer = str.encode("00001")
                                    UDPServerSocket.sendto(msgFromServer, address)
                                if(recievedFrag == amountOfFrag):
                                    print("I'm at final ACK")
                                    tBad.cancel()
                                    msgFromServer = str.encode("00001") + str.encode("final")
                                    UDPServerSocket.sendto(msgFromServer, address)
                                    text = ""
                                    j = 0
                                    while(j<amountOfFrag):
                                        text += textMsg[j]
                                        j += 1
                                    print(text)
                                    # Doimplementacia ------------
                                    print("obsah spravy v bajtoch: "+str(len(text.encode("utf8"))))
                                    # Doimplementacia --------------
                                    break
                    elif((message[13:14]).decode() == "."):
                        print("Enter the path to save file:")
                        filePath = input()
                        filePath += mesArray[0]
                        fileMess = []
                        posArray = []
                        for i in range(amountOfFrag):
                            posArray.insert(i, 0)
                        msgFromServer = str.encode("00001")
                        UDPServerSocket.sendto(msgFromServer, address)
                        tBadFragment(UDPServerSocket, address, posArray, recievedFrag, amountOfFrag)
                        tBad.start()
                        timer.cancel()
                        while(True):
                            bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
                            tBad.cancel()
                            tBadFragment(UDPServerSocket, address, posArray, recievedFrag, amountOfFrag)
                            tBad.start()
                            message = bytesAddressPair[0]
                            length = len(message)-13
                            # checkS
                            checkS = calc_checksum(hashlib.md5(message[13:13+length]).hexdigest())
                            if(checkS == (message[11:13]).decode()):
                                recievedFrag += 1
                                position = int.from_bytes(message[5:9], byteorder="big")
                                if(posArray[position] != 0):
                                    recievedFrag -=1
                                else:
                                    fileMess.insert(position, (message[13:13+length]))
                                posArray[position] = position
                                
                                if((message[0:5]).decode() == "1file"):
                                    print("I'm at ACK")
                                    msgFromServer = str.encode("00001") + int(position).to_bytes(2, byteorder="big")
                                    UDPServerSocket.sendto(msgFromServer, address)
                                if(recievedFrag%5 == 0 or recievedFrag == amountOfFrag):
                                    print("I'm at ACK")
                                    msgFromServer = str.encode("00001") 
                                    UDPServerSocket.sendto(msgFromServer, address)
                                if(recievedFrag == amountOfFrag):
                                    print("I'm at final ACK")
                                    tBad.cancel()
                                    msgFromServer = str.encode("00001" + filePath)
                                    UDPServerSocket.sendto(msgFromServer, address)
                                    newFile = open(filePath, "ab")
                                    print(filePath)
                                    j = 0
                                    while(j<amountOfFrag):
                                        newFile.write(fileMess[j])
                                        j += 1
                                    newFile.close()
                                    # Doimplementacia -------------
                                    b = os.path.getsize(filePath)
                                    print("obsah spravy v bajtoch: "+str(b))
                                    # Doimplementacia ---------------
                                    break
            elif(typ == "00003"):
                print("Stay in connection")
                timer.cancel()
                newTimerServ(UDPServerSocket, address)
                timer.start()        
            elif(typ == "00004"):
                timer.cancel()
                print("Client has broken connection")
                UDPServerSocket.close()
                clientOrServer = 0
                break
            elif(typ == "00007"):
                timer.cancel()
                UDPServerSocket.close()
                print("Client wants to change mode")
                break
    if (clientOrServer == 0):
        break
                    