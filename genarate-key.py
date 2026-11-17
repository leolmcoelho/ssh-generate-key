import os
import shlex
import subprocess

import paramiko
from dotenv import load_dotenv

load_dotenv(override=True)

def create_ssh_key(key_name="id_rsa", key_path=None, passphrase=""):
    if key_path is None:
        key_path = os.path.expanduser("~/.ssh/")

    if not os.path.exists(key_path):
        os.makedirs(key_path)

    private_key = os.path.join(key_path, key_name)
    public_key = f"{private_key}.pub"

    # Se a chave já existe, perguntar se deve sobrescrever; senão, reutilizar
    if os.path.exists(private_key):
        overwrite = input(f"{private_key} já existe. Sobrescrever? (s/n): ").strip().lower()
        if overwrite != "s":
            if not os.path.exists(public_key):
                print(f"Chave pública {public_key} não encontrada, não é possível reutilizar.")
                return None
            print(f"Reutilizando a chave existente em {private_key}")
            return private_key, public_key
        os.remove(private_key)
        if os.path.exists(public_key):
            os.remove(public_key)

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

    return private_key, public_key

def send_public_key_to_server(server_ip, port, username, password, public_key_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Conectando ao servidor {server_ip}:{port} com usuário '{username}'...")
        ssh.connect(server_ip, port, username=username, password=password, timeout=10)
        print("Conexão estabelecida com sucesso!")

        with open(public_key_path) as f:
            pub_key = f.read().strip()

        # Um único comando: cria .ssh, anexa a chave e ajusta permissões.
        # Precisa aguardar recv_exit_status(), senão ssh.close() mata o comando.
        command = (
            "mkdir -p ~/.ssh && chmod 700 ~/.ssh && "
            f"printf '%s\\n' {shlex.quote(pub_key)} >> ~/.ssh/authorized_keys && "
            "chmod 600 ~/.ssh/authorized_keys"
        )
        _, stdout, stderr = ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            print(f"Erro ao anexar chave (exit {exit_status}): {stderr.read().decode().strip()}")
            return

        print(f"Chave pública anexada com sucesso ao arquivo authorized_keys no servidor {server_ip}")
    except paramiko.AuthenticationException:
        print(f"Erro de autenticação: Verifique o usuário, senha ou permissões no servidor.")
        print(f"  - IP: {server_ip}")
        print(f"  - Porta: {port}")
        print(f"  - Usuário: {username}")
    except paramiko.SSHException as e:
        print(f"Erro SSH: {e}")
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
    result = create_ssh_key(key_name=key_name, passphrase=passphrase)

    if result:
        _, pub_key_path = result
        # Passo 2: Enviar a chave pública para o servidor
        send_public_key_to_server(server_ip, port, username, password, pub_key_path)
    else:
        print("Falha na criação da chave (ou sobrescrita recusada), não foi possível prosseguir.")


use_env = input("Deseja usar o arquivo .env para configurar o acesso SSH? (S/n): ")

if use_env.lower() not in ["s", "n", ""]:
    print("Opção inválida. Encerrando o programa.")
    exit(1)

if use_env.lower() == "s" or use_env.lower() == "":
    # Exemplo de uso
    server_ip = os.getenv('SERVER_IP')  # IP do servidor remoto
    username = os.getenv("USERNAME")        # Nome de usuário no servidor remoto
    password = os.getenv("PASSWORD")    # Senha do usuário no servidor remoto
    port = os.getenv("PORT")              # Porta SSH do servidor remoto
    if port:
        port = int(port)
    else:
        port = 22
    
    print(f"Usando as configurações do arquivo .env: SERVER_IP={server_ip}, USERNAME={username}, PORT={port}, PASSWORD={password}")
else:
    server_ip = input("Informe o IP do servidor remoto: ")
    username = input("Informe o nome de usuário no servidor remoto: ")
    password = input("Informe a senha do usuário no servidor remoto: ")
    port_str = input("Informe a porta SSH do servidor remoto: ")
    port = int(port_str) if port_str else 22


configure_ssh_access(server_ip, port,  username, password)
