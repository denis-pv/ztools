#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import re
import sys
import time
import locale
import subprocess
import tempfile

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



def main_simple():
    # Устанавливаем локаль для корректного вывода
    #locale.setlocale(locale.LC_ALL, '')
    print("=" * 50)
    print("- check bridges")
    print("=" * 50)
    
    try:
        with open('/etc/tor/torrc', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("- file /etc/tor/torrc not found")
        sys.exit(1)
    except PermissionError:
        print("- no rights, use sudo.")
        sys.exit(1)
    
    # Поиск мостов
    bridge_pattern = r'Bridge\s+obfs4\s+(\d+\.\d+\.\d+\.\d+):(\d+)\s+([A-F0-9]+)\s+cert=([^\s]+)\s+iat-mode=\d'
    matches = re.findall(bridge_pattern, content)
    
    if not matches:
        print("- bridges not found in torrc")
        sys.exit(1)
    
    print(f"- founded: {len(matches)}")
    print("\n- check availabe...\n")
    
    working_bridges = []
    
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
           print(f" VERIFIED ({elapsed:.1f}s)")
           working_bridges.append(bridge_line)
       elif tor_check is None:
           print(f" PORT OPEN ({elapsed:.1f}s) [tor not installed]")
       else:
           print(f" PORT OPEN BUT FAILED ({elapsed:.1f}s)")

    
    # Вывод результатов - только ASCII символы!
    print("\n" + "=" * 50)
    print("RESULTS:")
    print(f"   total checked : {len(matches)}")
    print(f"   works         : {len(working_bridges)}")
    print(f"   n/a           : {len(matches) - len(working_bridges)}")
    
    if len(matches) > 0:
        percent = (len(working_bridges) / len(matches)) * 100
        print(f"   - percent:      {percent:.1f}%")
    
    print("\n- working bridges:")
    print("-" * 50)
    
    if working_bridges:
        for i, bridge in enumerate(working_bridges, 1):
            print(f"{i:2d}. {bridge[:70]}..." if len(bridge) > 70 else f"{i:2d}. {bridge}")
    else:
        print("   no working bridges")
    
    print("=" * 50)  # ЗАМЕНИЛИ "═" на обычный "="

if __name__ == "__main__":
    try:
        main_simple()
    except KeyboardInterrupt:
        print("\n\nuser terminated")
    except Exception as e:
        # Фильтруем не-ASCII символы в сообщении об ошибке
        error_msg = str(e)
        error_msg = ''.join(c if ord(c) < 128 else '?' for c in error_msg)
        print(f"\n Error: {error_msg}")