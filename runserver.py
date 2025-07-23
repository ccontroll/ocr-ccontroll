"""Gunicorn *production* config file"""

import multiprocessing
import os

BASEDIR = os.path.dirname(os.path.abspath(__file__))

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "api.wsgi:application"
# The number of worker processes for handling requests
workers = multiprocessing.cpu_count() * 2 + 1
# The socket to bind
bind = "0.0.0.0:8020"
# Write access and error info to /var/log
accesslog = f"{BASEDIR}/gunicorn/access.log"
errorlog = f"{BASEDIR}/gunicorn/error.log"
# Redirect stdout/stderr to log file
capture_output = True
# Restart workers when code changes (development only!)
reload = True
# PID file so you can easily fetch process ID
pidfile = f"{BASEDIR}/gunicorn/prod.pid"
# Daemonize the Gunicorn process (detach & enter background)
daemon = True

import subprocess
import errno

# Caminho completo para o executável do rqworker
command = f"{BASEDIR}/env/bin/python3"
args = ["manage.py", "rqworker"] # Argumentos para o comando
PID_FILE = f"{BASEDIR}/gunicorn/rq.pid"

def is_pid_active(pid):
    try:
        os.kill(pid, 0)
    except OSError as e:
        if e.errno == errno.ESRCH:
            return False
        elif e.errno == errno.EPERM:
            return True
        else:
            return False
    else:
        return True
    
def run_worker():
    try:
        # Inicia o RQ Worker em background
        print("Iniciando o RQ Worker...")
        process = subprocess.Popen(
            [command] + args,
            cwd=f"{BASEDIR}/",
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid # Para evitar que o processo herde o grupo de processos do shell pai
        )

        # Pega o PID do processo filho
        pid = process.pid

        # Salva o PID em um arquivo
        pid_file_path = f"{BASEDIR}/gunicorn/rq.pid" # Caminho completo para salvar o PID
        with open(pid_file_path, 'w') as file:
            file.write(str(pid))
        print(f"RQ Worker iniciado com PID: {pid}. PID salvo em {pid_file_path}")

    except Exception as e:
        print(f"Ocorreu um erro ao iniciar o RQ Worker: {e}")

if os.path.exists(PID_FILE):
    try:
        with open(PID_FILE, 'r') as f:
            existing_pid = int(f.read().strip())
        if is_pid_active(existing_pid):
            pass
        else:
            run_worker()
    except Exception:
        # PID inválido: inicia o RQ Worker
        run_worker()