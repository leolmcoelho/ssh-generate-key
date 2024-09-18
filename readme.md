### README (English Version)

# SSH Key Generation and Public Key Transfer

This Python script allows the user to generate an SSH key pair (private and public keys), and automatically upload the public key to a remote server to enable passwordless SSH login. 

It uses the following Python libraries:
- `paramiko`: To establish an SSH connection.
- `scp`: To transfer files over SCP (Secure Copy).
- `subprocess`: To execute system commands for key generation.
- `dotenv`: To load environment variables.

## Prerequisites

Before running the script, ensure you have the following:
1. Python installed (>= 3.6).
2. Install the required Python packages by running:
   ```bash
   pip install paramiko scp python-dotenv
   ```

3. Create a `.env` file with the following environment variables:

   ```
   SERVER_IP=your_server_ip
   USER=your_username
   PASSWORD=your_password
   ```

## How to Use

1. **Generate SSH Key and Upload Public Key**:
   The function `configure_ssh_access` generates an SSH key pair and uploads the public key to the remote server's `~/.ssh/authorized_keys` file.

   **Example**:
   ```python
   configure_ssh_access(server_ip, username, password, key_name="custom_key_name")
   ```
   - `server_ip`: The IP address of your server.
   - `username`: Your username on the server.
   - `password`: Your login password on the server.
   - `key_name`: (Optional) The name of the key file (default is `id_rsa`).

2. **File and Directory Permissions**:
   The script ensures that the proper permissions are set on the `~/.ssh` directory and the `authorized_keys` file:
   - `~/.ssh`: `700`
   - `~/.ssh/authorized_keys`: `600`

3. **Testing**:
   After running the script, test the passwordless SSH login:
   ```bash
   ssh -i ~/.ssh/custom_key_name your_username@your_server_ip
   ```

## Error Handling

The script provides basic error handling and prints messages if an error occurs during SSH key generation or key transfer.

---

### README (Versão em Português)

# Geração de Chave SSH e Envio de Chave Pública

Este script em Python permite ao usuário gerar um par de chaves SSH (chave privada e pública) e enviar automaticamente a chave pública para um servidor remoto, habilitando o login SSH sem senha.

Ele utiliza as seguintes bibliotecas em Python:
- `paramiko`: Para estabelecer uma conexão SSH.
- `scp`: Para transferir arquivos via SCP (Secure Copy).
- `subprocess`: Para executar comandos do sistema para geração de chaves.
- `dotenv`: Para carregar variáveis de ambiente.

## Pré-requisitos

Antes de executar o script, certifique-se de ter o seguinte:
1. Python instalado (>= 3.6).
2. Instale os pacotes Python necessários executando:
   ```bash
   pip install paramiko scp python-dotenv
   ```

3. Crie um arquivo `.env` com as seguintes variáveis de ambiente:

   ```
   SERVER_IP=seu_ip_do_servidor
   USER=seu_nome_de_usuario
   PASSWORD=sua_senha
   ```

## Como Usar

1. **Gerar a Chave SSH e Enviar a Chave Pública**:
   A função `configure_ssh_access` gera um par de chaves SSH e envia a chave pública para o arquivo `~/.ssh/authorized_keys` no servidor remoto.

   **Exemplo**:
   ```python
   configure_ssh_access(server_ip, username, password, key_name="nome_personalizado_da_chave")
   ```
   - `server_ip`: O endereço IP do seu servidor.
   - `username`: O seu nome de usuário no servidor.
   - `password`: A sua senha de login no servidor.
   - `key_name`: (Opcional) O nome do arquivo da chave (o padrão é `id_rsa`).

2. **Permissões de Arquivos e Diretórios**:
   O script garante que as permissões corretas sejam definidas no diretório `~/.ssh` e no arquivo `authorized_keys`:
   - `~/.ssh`: `700`
   - `~/.ssh/authorized_keys`: `600`

3. **Testando**:
   Após executar o script, teste o login SSH sem senha:
   ```bash
   ssh -i ~/.ssh/nome_personalizado_da_chave seu_nome_de_usuario@seu_ip_do_servidor
   ```

## Tratamento de Erros

O script fornece tratamento básico de erros e exibe mensagens caso ocorra um erro durante a geração ou envio da chave SSH.

