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

def send_public_key_to_server(server_ip, port, username, password, public_key_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(server_ip, port, username=username, password=password)

        # Criar o diretório .ssh se não existir
        stdin, stdout, stderr = ssh.exec_command("mkdir -p ~/.ssh && chmod 700 ~/.ssh")
        stdout.channel.recv_exit_status()  # Aguarda o comando finalizar
        
        # Transferir a chave pública usando SCP
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(public_key_path, f"/home/{username}/.ssh/temp_key.pub")

        # Adicionar a chave ao authorized_keys
        ssh.exec_command("cat ~/.ssh/temp_key.pub >> ~/.ssh/authorized_keys && rm ~/.ssh/temp_key.pub")
        ssh.exec_command("chmod 600 ~/.ssh/authorized_keys")

        print(f"Chave pública anexada com sucesso ao arquivo authorized_keys no servidor {server_ip}")
    except Exception as e:
        print(f"Erro ao enviar chave para o servidor: {e}")
    finally:
        ssh.close()

def configure_ssh_access(server_ip, port, username, password, key_name=None, passphrase=None):
    # Passo 1: Criar chave SSH
    if passphrase is None:
        passphrase = ""
    if key_name is None:
        key_name = input("Informe o nome da chave SSH: ")
    key_path, pub_key_path = create_ssh_key(key_name=key_name, passphrase=passphrase)
    
    if pub_key_path:
        # Passo 2: Enviar a chave pública para o servidor
        send_public_key_to_server(server_ip, port, username, password, pub_key_path)
    else:
        print("Falha na criação da chave, não foi possível prosseguir.")


use_env = input("Deseja usar o arquivo .env para configurar o acesso SSH? (s/n): ")

if use_env.lower() not in ["s", "n"]:
    print("Opção inválida. Encerrando o programa.")
    exit(1)

if use_env.lower() == "s":
    # Exemplo de uso
    server_ip = os.getenv('SERVER_IP')  # IP do servidor remoto
    username = os.getenv("USER")        # Nome de usuário no servidor remoto
    password = os.getenv("PASSWORD")    # Senha do usuário no servidor remoto
    port = os.getenv("PORT")              # Porta SSH do servidor remoto
    
else:
    server_ip = input("Informe o IP do servidor remoto: ")
    username = input("Informe o nome de usuário no servidor remoto: ")
    password = input("Informe a senha do usuário no servidor remoto: ")
    port = input("Informe a porta SSH do servidor remoto: ")


configure_ssh_access(server_ip, port,  username, password)
