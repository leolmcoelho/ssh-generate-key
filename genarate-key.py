import os
import subprocess

import paramiko
from dotenv import load_dotenv
from scp import SCPClient

load_dotenv(override=True)

def create_ssh_key(key_name="id_rsa", key_path=None, passphrase=""):
    if key_path is None:
        key_path = os.path.expanduser("~/.ssh/")

    if not os.path.exists(key_path):
        os.makedirs(key_path)

    private_key = os.path.join(key_path, key_name)
    
    # Verificar se a chave já existe
    if os.path.exists(private_key):
        overwrite = input(f"A chave {private_key} já existe. Deseja sobrescrever? (s/n): ")
        if overwrite.lower() != 's':
            print("Operação cancelada.")
            return None, None
        else:
            # Remover as chaves existentes antes de criar novas
            try:
                os.remove(private_key)
                if os.path.exists(f"{private_key}.pub"):
                    os.remove(f"{private_key}.pub")
            except Exception as e:
                print(f"Erro ao remover chaves existentes: {e}")
                return None, None
    
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
        return None, None

    return private_key, f"{private_key}.pub"

def send_public_key_to_server(server_ip, port, username, password, public_key_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Conectando ao servidor {server_ip}:{port} com usuário '{username}'...")
        ssh.connect(server_ip, port, username=username, password=password, timeout=10)
        print("Conexão estabelecida com sucesso!")

        # Obter o diretório home do usuário
        stdin, stdout, stderr = ssh.exec_command("echo $HOME")
        home_dir = stdout.read().decode().strip()

        # Criar o diretório .ssh se não existir
        stdin, stdout, stderr = ssh.exec_command("mkdir -p ~/.ssh && chmod 700 ~/.ssh")
        stdout.channel.recv_exit_status()  # Aguarda o comando finalizar
        
        # Transferir a chave pública usando SCP
        remote_path = f"{home_dir}/.ssh/temp_key.pub"
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(public_key_path, remote_path)
        print(f"Chave pública transferida para {remote_path}")

        # Adicionar a chave ao authorized_keys
        ssh.exec_command("cat ~/.ssh/temp_key.pub >> ~/.ssh/authorized_keys && rm ~/.ssh/temp_key.pub")
        ssh.exec_command("chmod 600 ~/.ssh/authorized_keys")

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
    key_path, pub_key_path = create_ssh_key(key_name=key_name, passphrase=passphrase)
    
    if key_path is None:
        print("Falha na criação da chave, não foi possível prosseguir.")
        return
    
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
    if port:
        port = int(port)
    else:
        port = 22
    
else:
    server_ip = input("Informe o IP do servidor remoto: ")
    username = input("Informe o nome de usuário no servidor remoto: ")
    password = input("Informe a senha do usuário no servidor remoto: ")
    port_str = input("Informe a porta SSH do servidor remoto: ")
    port = int(port_str) if port_str else 22


configure_ssh_access(server_ip, port,  username, password)
