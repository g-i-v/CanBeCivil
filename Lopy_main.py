# -----------------------------------------------------------------------------------------
#
# Questo è il CODICE SORGENTE relativo al lato client di un sistema di monitoraggio
# di cestini della spazzatura: i dispositivi effettueranno un controllo sulla pienezza
# dei contenitori, segnalando di volta in volta se questi saranno stati riempiti per il
# 50 oppure il 100 %. Nel caso in cui dovessero essere utilizzati in maniera inappropriata
# il sistema è in grado di riconoscere un cestino otturato da un oggetto di grosse dimensio-
# ni posto sul bordo del recipiente.
# ----------------------------------------------------------------------------------------
# Il programma, scritto in linguaggio MicroPython è pensato principalmente per funzionare
# su dispositivi Pycom. Nel nostro caso sono stati utilizzati :
#  1- LoPy : Microcontrollore dotato di protocolli di comunicazioni quali Bluetooth,
#            Wifi e LoRa.
#  2- Expansion Board : Scheda di espansione compatibile con il LoPy per alimentarlo e
#            collegare i sensori utili mediante i pin forniti da essa.
#
# -----------------------------------------------------------------------------------------


# Importazione  delle librerie necessarie
from machine import Timer
import time
from machine import Pin
import pycom
import network
import time
import socket

# Istanziazione, mediante la funzione Chrono inclusa nella libreria Timer, di un cronometro
chrono = Timer.Chrono()

# Assegnazione, degli output dei sensori montati sul cestino, alle variabili "pir#"
# mediante l'utilizzo dei pin in dotazione alla Expansion Board.
s1 = Pin('G5',mode=Pin.IN,pull=Pin.PULL_UP)
s2 = Pin('G4',mode=Pin.IN,pull=Pin.PULL_UP) #G4 e G5 Top Bin
s3 = Pin('G0',mode=Pin.IN,pull=Pin.PULL_UP)
s4 = Pin('G31',mode=Pin.IN,pull=Pin.PULL_UP) #G0 e G31 Middle Bin

# Dichiarazione di tre variabili booleane per il controllo della trasmissione
# delle segnalazioni verso il server.
bool1 = 0
bool2 = 0
bool3 = 0

# Connessione, sfruttando la libreria network, ad una rete internet utilizzando SSID e relativa PASSWORD (WPA2)
wlan = network.WLAN(mode=network.WLAN.STA)
wlan.connect('giv', auth=(network.WLAN.WPA2, '4qwerty2'))
while not wlan.isconnected():
    time.sleep_ms(50)
print(wlan.ifconfig()) # Questo comando stampa a video l'indirizzo IP assegnato al LoPy
                       # maschera ed indirizzo IP del Gaterway.

# Istanziazione del socket che verrà utilizzato per comunicare con
# il Raspberry Pi che svolgerà il compito di server.
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # La costante socket.AF_INET serve a specificare il dominio sul quale
                                                                 # il network funzionerà ovvero IPv4.
                                                                 # La costante socket.SOCK_STREAM indica che stiamo creando una socket per
                                                                 # una connessione TCP (per UDP serve usare: socket.SOCK_DGRAM).

# Connessione del client all'indirizzo IP locale del Raspberry Pi, sulla porta scelta per il server in ascolto :
# in poche parole questa funzione connette il socket istanziato sul client a quello istanziato sul server.
clientsocket.connect(('192.168.43.114', 8089))


# main loop

print("Starting main loop")

# il corpo del nostro programma è inserito in un loop di controllo che terminerà solo quando
# verrà rilevato il cestino pieno al 100% o sarà sfortunatamente otturato dal posizionamento di un oggetto
# di grossa taglia sul suo bordo.

while True:

# avvio del cronometro istanziato precedentemente nel momento in cui viene rilevata la presenza di un oggetto da
# uno qualsiasi dei sensori posizionati all'interno del cestino.
    if s1() == 0 or s2() == 0 or s3() == 0 or s4() == 0:
        chrono.start()
# Inizializzazzione delle variabili temporali.
        t1 = 0
        t2 = 0
        x = 0 # mi permetterà di contare 5 secondi trascorsi fra t2 e t1

# stampa a video di una stringa ("Oggetto inserito") fintanto che non sono passati più di 5 secondi dal
# momento della rilevazione di un oggetto immesso all'interno del contenitore.
        while t1<5 and (s1() == 0 or s2() == 0 or s3() == 0 or s4() == 0):
            t1 = chrono.read() # aggiornamento della variabile tempo
            print("Oggetto inserito")
            pycom.heartbeat(False) # spegnimento del led blu  che lampeggia sul LoPy
            pycom.rgbled(0x000000) # il led rimane spento spento in caso di "Oggetto inserito"
        chrono.stop() # fermo il cronometro nel momento in cui il tempo supera i 5 secondi lasciando t1 = 5

# Nel caso di corretto utilizzo del cestino, questo per forza di cose dovrà riempirsi
# prima per metà e successivamente al 100%: per questo motivo viene effettuato
# un controllo prima sui sensori posti a media altezza; un successivo controllo
# interno provvede a valutare i sensori posti sul top del contenitore per la verifica
# di cestino pieno al 100%.
        if (s3()==0 and s4()==0) :
            print("Cestino mezzo pieno") # stampa a video di una stringa
            pycom.heartbeat(False)  # spegnimento del led blu  che lampeggia sul LoPy
            pycom.rgbled(0x000099) # il led del LoPy resta costantemente BLU appena viene scoperto
                                   # che il cestino è pieno al 50%
          # utilizzo della variabile booleana per inviare un solo messaggio verso il server
            while bool1 == 0 :
                clientsocket.send('Ces1') # Trasmissione della stringa "Ces1" che verrà riconosciuta
                                           # dal server ed avviera il processo di segnalazione
                                           # su cellulare mediante BOT Telegram
                bool1 = 1 # Assegnazione del valore 1 per assicurare che non ci siano funzionamenti
                          # scorretti del sistema di trasmissione

# Questo che segue è il controllo sui sensori posti sul bordo del contenitore in caso di corretto
# utilizzo del dispositivo. Per capire se un cestino è pieno al 100% viene effettuata ancora una
# volta, una valutazione del tempo trascorso : quando saranno passati altri 5 secondi sarà
# possibile affermare che il recipiente è effettivamente colmo

            if (s1() == 0 and s2() == 0) :
                chrono.start() # riparte il cronometro

# Attesa di altri 5 secondi prima di decretare la completa pienezza del cestino
                while x<5 :
                    t2 = chrono.read() # la variabile t2 è quella che si aggiorna
                                       # mentre t1 resta costante (avrà valore 5)
                    x = t2 - t1

                # come fatto in precedenza, la variabile booleana viene sfruttata per inviare un solo messaggio verso il server
                while bool2 == 0 :
                    clientsocket.send('Ces2') # Trasmissione della stringa "Ces2" che verrà riconosciuta
                                               # dal server ed avviera il processo di segnalazione
                                               # su cellulare mediante BOT Telegram. Diversamente
                                               # dalla prima segnalazione, ci si aspetta un risultato
                                               # differente sui dispositivi cellulari.
                    print("Cestino 100% ") # all'uscita dal ciclo, quando saranno trascorsi
                                           # i 5 secondi verrà stampato a video il messaggio
                                           # "Cestino 100% "
                    clientsocket.close()   # Il programma sta per terminare : chiudo il socket istanziato inizialmente
                    bool2 = 1 # Assegnazione  del valore 1 per assicurare che non ci siano funzionamenti
                              # scorretti del sistema di trasmissione

                chrono.stop() # stop del cronometro.
                pycom.heartbeat(False) # stop del led blu che lampeggia
                pycom.rgbled(0x990000) # Accensione del led che rimane costantemente acceso di ROSSO sul LoPy
                break # Il programma termina

# Con le seguenti righe si include il controllo che prevede il caso in cui il cestino fosse utilizzato in maniera inappropriata,
# ovvero il caso in cui un utilizzatore posizionasse una busta della spazzatura, otturandolo e rendendo impossibile il suo utilizzo.
# Lo smaltimento di non consentito di questo tipo di  rifiuti dovrebbe essere sanzionato. La rilevazione di tale stato è data dall'accensione
#d ei sensori posizionati sul bordo del recipiente mentre almeno uno dei due sensori posti a metà non rilevano alcun rifiuto.

        elif (s1() == 0 and s2() == 0) and (s3() == 1 or s4() == 1) :
            print("Cestino otturato") # stampa a video di una stringa
            pycom.heartbeat(False)  # spegnimento del led blu  che lampeggia sul LoPy
            pycom.rgbled(0x999900) # il led del LoPy resta costantemente GIALLO appena viene scoperto
                                   # che il cestino è stato otturato
            # utilizzo della variabile booleana per inviare un solo messaggio verso il server
            while bool3 == 0 :
                clientsocket.send('Ces3') # Trasmetto la stringa "Ces3" che verrà riconosciuta
                                           # dal server ed avviera il processo di segnalazione
                                           # su cellulare mediante BOT Telegram
                clientsocket.close()  # Il programma sta per terminare : chiusura del socket istanziato inizialmente
                bool3 = 1 # Assegnazione del valore 1 per assicurare che non ci siano funzionamenti
                          # scorretti del sistema di trasmissione
            break # Il programma termina

# Se nessuno dei sensori rileva la presenza di un oggetto all'interno di un cestino significa che è il dispositivo non sta essendo utilizzato
# e gli unici risultati saranno una stampa a video di una stringa di "-------" oltre che la segnalazione mediante accensione del led di colore verde
# che sta ad indicare il corretto stato del cestino.
    else:
        print("-------") # stampa a video del messaggio "-------"
        pycom.heartbeat(False) # # spegnimento del led blu  che lampeggia sul LoPy
        pycom.rgbled(0x001100)  # Accensione del led che rimane costantemente acceso di VERDE sul LoPy
        chrono.reset() # il cronometro deve essere resettato ogni volta che si entra in questo stato per avere un corretto
                       # conteggio del tempo di attivazione dei sensori: in caso non venisse resettato il cronometro,
                       # il contatore sarebbe cumulativo, restituendo un falso positivo una volta accumulati 5 secondi.
