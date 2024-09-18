
import os
import subprocess
import paramiko
from scp import SCPClient
from dotenv import load_dotenv

load_dotenv()

def create_ssh_key(key_name="id_rsa", key_path=None, passphrase=""):
    if key_path is None:
        key_path = os.path.expanduser("~/.ssh/")

    if not os.path.exists(key_path):
        os.makedirs(key_path)

    private_key = os.path.join(key_path, key_name)
    
    # Gerar a chave SSH
    command = [
        "ssh-keygen",
        "-t", "rsa",
        "-b", "4096",
        "-f", private_key,
        "-N", passphrase
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Chave SSH criada em {private_key}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar chave SSH: {e}")
        return None

    return private_key, f"{private_key}.pub"


def send_public_key_to_server(server_ip, username, password, public_key_path):
    # Conectar ao servidor remoto via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(server_ip, username=username, password=password)

        # Ler o conteúdo da chave pública
        with open(public_key_path, "r") as f:
            public_key = f.read().strip()

        # Comando para adicionar a chave pública ao arquivo `authorized_keys`
        command = f'echo "{public_key}" >> ~/.ssh/authorized_keys'
        ssh.exec_command(command)

        # Ajustar permissões
        ssh.exec_command("chmod 700 ~/.ssh")
        ssh.exec_command("chmod 600 ~/.ssh/authorized_keys")
        
        print(f"Chave pública anexada com sucesso ao arquivo authorized_keys no servidor {server_ip}")
    except Exception as e:
        print(f"Erro ao enviar chave para o servidor: {e}")
    finally:
        ssh.close()



def configure_ssh_access(server_ip, username, password, key_name="id_rsa", passphrase=""):
    # Passo 1: Criar chave SSH
    key_path, pub_key_path = create_ssh_key(key_name=key_name, passphrase=passphrase)
    
    if pub_key_path:
        # Passo 2: Enviar a chave pública para o servidor
        send_public_key_to_server(server_ip, username, password, pub_key_path)
    else:
        print("Falha na criação da chave, não foi possível prosseguir.")

# Exemplo de uso
server_ip = os.getenv('SERVER_IP')  # IP do servidor remoto
username = os.getenv("USER")            # Nome de usuário no servidor remoto
password = os.getenv("PASSWORD")        # Senha do usuário no servidor remoto

# print(server_ip, username, password)
configure_ssh_access(server_ip, username, password, key_name="timesaver_key")
