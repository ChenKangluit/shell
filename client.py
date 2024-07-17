import socket
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox


class ClientApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Client")

        self.host = '127.0.0.1'
        self.port = 9999

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
        except Exception as e:
            messagebox.showerror("Error", f"Unable to connect to server: {e}")
            self.master.quit()
            return

        self.create_widgets()

    def create_widgets(self):
        self.command_label = tk.Label(self.master, text="Command:")
        self.command_label.grid(row=0, column=0, padx=10, pady=10)

        self.command_entry = tk.Entry(self.master, width=50)
        self.command_entry.grid(row=0, column=1, padx=10, pady=10)

        self.send_command_button = tk.Button(self.master, text="Send Command", command=self.send_command)
        self.send_command_button.grid(row=0, column=2, padx=10, pady=10)

        self.upload_button = tk.Button(self.master, text="Upload File", command=self.upload_file)
        self.upload_button.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.browse_button = tk.Button(self.master, text="Browse Filesystem", command=self.browse_filesystem)
        self.browse_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        self.output_text = scrolledtext.ScrolledText(self.master, width=70, height=20)
        self.output_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def send_command(self):
        command = self.command_entry.get()
        if command.lower() == 'exit':
            self.client_socket.close()
            self.master.quit()
            return

        try:
            self.client_socket.sendall(command.encode('utf-8'))
            output = self.client_socket.recv(4096).decode('utf-8')
            self.output_text.insert(tk.END, f"Command Output:\n{output}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error sending command: {e}")

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                filename = os.path.basename(file_path)
                self.client_socket.sendall(f"upload {filename}".encode('utf-8'))
                with open(file_path, 'rb') as f:
                    while (chunk := f.read(1024)):
                        self.client_socket.sendall(chunk)
                self.client_socket.sendall(b'DONE')
                messagebox.showinfo("Upload", f"File {filename} uploaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Error uploading file: {e}")

    def browse_filesystem(self):
        directory = filedialog.askdirectory()
        if directory:
            try:
                self.client_socket.sendall(f"browse {directory}".encode('utf-8'))
                output = self.client_socket.recv(4096).decode('utf-8')
                self.output_text.insert(tk.END, f"Filesystem at {directory}:\n{output}\n")
            except Exception as e:
                messagebox.showerror("Error", f"Error browsing filesystem: {e}")

    def on_closing(self):
        self.client_socket.close()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
