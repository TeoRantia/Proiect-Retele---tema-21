import socket
import json
import sys

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 9000

# Codul task-ului ce va fi salvat și executat de client

with open("task_sample.py", "r") as f:
    cod_binar = f.read()

# Argumentele pe care le trimitem
argumente = sys.argv[1:]  # restul argumentelor

def trimite_task():
    mesaj = {
        "tip": "task",
        "task_code": cod_binar,
        "args": argumente
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))
        s.send(json.dumps(mesaj).encode())
        rezultat = s.recv(4096).decode()
        print(f"[INVOCATOR] Răspuns de la server/client: {rezultat}")


if __name__ == "__main__":
    trimite_task()
