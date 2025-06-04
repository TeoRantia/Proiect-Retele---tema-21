import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 9000

# Lista clienților activi: {id_client: (ip, port_de_executie)}
clienti_activi = {}
lock = threading.Lock()


def handle_client(conn, addr):
    try:
        data = conn.recv(4096).decode()
        mesaj = json.loads(data)

        tip = mesaj.get("tip")
        id_client = mesaj.get("id")

        if tip == "register":
            port_exec = mesaj.get("port_exec")
            with lock:
                clienti_activi[id_client] = (addr[0], port_exec)
            print(f"[REGISTER] Client {id_client} adăugat: {addr[0]}:{port_exec}")

        elif tip == "unregister":
            with lock:
                if id_client in clienti_activi:
                    del clienti_activi[id_client]
            print(f"[UNREGISTER] Client {id_client} eliminat")

        elif tip == "task":
            cod_binar = mesaj.get("task_code")
            args = mesaj.get("args", [])
            client_exec = select_client()
            if client_exec:
                trimitere_task(client_exec, cod_binar, args, conn)
            else:
                conn.send("NO_CLIENT_AVAILABLE".encode())

    except Exception as e:
        print(f"[EROARE] {e}")
    finally:
        conn.close()

index_curent = 0

def select_client():
    global index_curent
    with lock:
        # round-robin, alegem urmatorul client la rand
        clienti = list(clienti_activi.items())
        if not clienti:
            return None

        # daca indexul curent e prea mare dupa ce lista s-a micsorat, il resetam la 0
        if index_curent >= len(clienti):
            index_curent = 0
            
        client =  clienti[index_curent]
        index_curent = (index_curent + 1) % len(clienti)
        return client


def trimitere_task(client_exec_info, cod_binar, args, conn_original):
    id_client, (ip, port) = client_exec_info
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            mesaj = {
                "cod_binar": cod_binar,
                "args": args
            }
            s.send(json.dumps(mesaj).encode())
            rezultat = s.recv(4096)
            conn_original.send(rezultat)
    except Exception as e:
        print(f"[EROARE TASK] {e}")
        conn_original.send(f"EROARE: {str(e)}".encode())


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"[SERVER START] Ascult pe {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()


if __name__ == "__main__":
    start_server()
