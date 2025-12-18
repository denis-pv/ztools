#!/usr/bin/env python3

import socket
import subprocess
import tempfile
import re
import sys
import time

def check_port(ip, port, timeout=3):
    """Базовая проверка TCP-порта"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def check_with_tor(bridge_line):
    """Проверка через tor --verify-config"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.torrc', delete=False) as f:
            f.write(f"SocksPort 0\nLog notice stdout\n{bridge_line}\n")
            f.flush()
            
            result = subprocess.run(
                ['tor', '-f', f.name, '--verify-config'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # Удаляем временный файл
            import os
            os.unlink(f.name)
            
            return result.returncode == 0
            
    except subprocess.TimeoutExpired:
        return False
    except FileNotFoundError:
        # tor не установлен
        return None
    except Exception:
        return False

def main():
    # ... ваш код чтения torrc ...
    
    for i, match in enumerate(matches, 1):
        ip = match[0]
        port = int(match[1])
        fingerprint = match[2]
        cert = match[3]
        
        bridge_line = f"Bridge obfs4 {ip}:{port} {fingerprint} cert={cert} iat-mode=0"
        
        print(f"[{i}/{len(matches)}] {ip}:{port}", end=' - ')
        
        # 1. Базовая проверка порта
        start = time.time()
        port_open = check_port(ip, port)
        elapsed = time.time() - start
        
        if not port_open:
            print(f"PORT CLOSED ({elapsed:.1f}s)")
            continue
        
        # 2. Продвинутая проверка через tor
        tor_check = check_with_tor(bridge_line)
        
        if tor_check is True:
            print(f"✓ VERIFIED ({elapsed:.1f}s)")
        elif tor_check is None:
            print(f"✓ PORT OPEN ({elapsed:.1f}s) [tor not installed]")
        else:
            print(f"✗ PORT OPEN BUT FAILED ({elapsed:.1f}s)")