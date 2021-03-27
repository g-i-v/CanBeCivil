#Creazione di uno script python che realizza un socket server TCP-IP capace di ricevere segnalazioni in arrivo dal client (Lopy) ponendosi in ascolto e inoltrare un messaggio di notifica via BOT Telegram a seconda della condizione del cestino che si sta monitorando.

import socket #Import della libreria dedicata ai Socket in Python
import os #Import della libreria che permette di interagire con il sistema operativo
import sys #Import della libreria che fornisce l'accesso ad alcune variabili usate o mantenute dall'interprete e a funzioni che interagiscono fortemente con l'interprete stesso.

print("----------------------------------------------------------------")
print("\n  Buongiorno, questo server monitora la situazione dei cestini.\n")
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Crea una istanza di TCP/IP socket
print 'Socket created'
try:
    serversocket.bind(('192.168.43.114', 8089)) #Lega l'indirizzo IP e la porta e li assegna all'istanza serversocket. La porta 8089 e' stata selta tra quelle non well-known e indica la porta sulla quale il server e' in ascolto
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'
print("\n  Il server e' in attesa di una connessione \n")
print("----------------------------------------------------------------\n")
#Start listening on socket
serversocket.listen(10) # Abilitazione del server socket che potrà accettare al più 10 connessioni

connection, address = serversocket.accept() #Viene accettata una connessione tra il server e il client
print ('\nConnected to ' + address[0] + ':' + str(address[1]) + '\n')

while True: #Finche' la connessione non viene interrotta manualmente il server resta in ascolto

        buf = connection.recv(64) #Ricezione su buf di dati fino a 64 byte
        if (buf=="Ces1"): #Situazione in cui il cestino e' mezzo pieno
            print 'Cestino mezzo pieno'
            os.system('curl -s -X POST https://api.telegram.org/bot509765588:AAG76DK3MQP54_PCo5dCOpDVDM7ZHvFwmXk/sendMessage -d chat_id=-226231007 -d text="Attenzione Prego: Si registra cestino mezzo pieno" > /dev/null') #Esecuzione del comando curl che ci permette di inoltrare il messaggio di notifica sul BOT Telegram

        elif(buf=="Ces2"): #Situazione in cui il cestino e' completamente pieno
            print 'Cestino pieno 100%'
            os.system('curl -s -X POST https://api.telegram.org/bot509765588:AAG76DK3MQP54_PCo5dCOpDVDM7ZHvFwmXk/sendMessage -d chat_id=-226231007 -d text="Cestino pieno al 100%. Provvedere al ricambio busta" > /dev/null') #Esecuzione del comando curl che ci permette di inoltrare il messaggio di notifica sul BOT Telegram
            connection, address = serversocket.accept() #Quando si notifica il cestino completamente pieno, il client viene riavviato. Conseguentemente, il server si appresta ad accettare una nuova connessione
            print ('\nConnected to ' + address[0] + ':' + str(address[1]) + '\n')


        elif(buf=="Ces3"): #Situazione in cui il cestino e' otturato
            print 'Cestino otturato'
	        os.system('curl -s -X POST https://api.telegram.org/bot509765588:AAG76DK3MQP54_PCo5dCOpDVDM7ZHvFwmXk/sendMessage -d chat_id=-226231007 -d text="Cestino otturato. Provvedere al ripristino" > /dev/null') #Esecuzione del comando curl che ci permette di inoltrare il messaggio di notifica sul BOT Telegram
	        connection, address = serversocket.accept() #Quando si notifica che il cestino e' otturato, il client viene riavviato. Conseguentemente, il server si appresta ad accettare una nuova connessione
            print ('\nConnected to ' + address[0] + ':' + str(address[1]) + '\n')

serversocket.close() #Segna la chiusura del socket. Tutte le future operazioni sull'oggetto socket falliranno e il server non ricevera' piu' dati
