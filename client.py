import socket
import threading
import json
import subprocess
import uuid
import sys

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 9000
CLIENT_EXEC_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9001 # portul pe care acest client ascultă pentru task-uri
ID_CLIENT = str(uuid.uuid4())[:8]  # identificator unic scurt


def inregistrare():
    mesaj = {
        "tip": "register",
        "id": ID_CLIENT,
        "port_exec": CLIENT_EXEC_PORT
    }
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))
        s.send(json.dumps(mesaj).encode())
        print(f"[CLIENT] Înregistrat ca {ID_CLIENT}")


def dezregistrare():
    mesaj = {
        "tip": "unregister",
        "id": ID_CLIENT
    }
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))
        s.send(json.dumps(mesaj).encode())
        print(f"[CLIENT] Dezînregistrat")


def asculta_taskuri():
    def handler(conn, addr):
        try:
            data = conn.recv(4096).decode()
            task = json.loads(data)
            cod_binar = task.get("cod_binar")
            args = task.get("args", [])

            # Salvăm fișierul binar primit
            with open("task_temp.py", "w") as f:
                f.write(cod_binar)

            print(f"[TASK] Execut task-ul primit cu args: {args}")
            rezultat = subprocess.run(["python", "task_temp.py"] + args, capture_output=True)
            cod = rezultat.returncode
            conn.send(str(cod).encode())
        except Exception as e:
            conn.send(f"EROARE_CLIENT: {e}".encode())
        finally:
            conn.close()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", CLIENT_EXEC_PORT))
    server.listen()
    print(f"[CLIENT] Ascultă task-uri pe portul {CLIENT_EXEC_PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handler, args=(conn, addr)).start()


if __name__ == "__main__":
    try:
        inregistrare()
        threading.Thread(target=asculta_taskuri, daemon=True).start()
        input("[CLIENT] Apasă ENTER pentru a ieși...\n")
    finally:
        dezregistrare()
