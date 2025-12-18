#!/usr/bin/env python3
"""
Упрощенная версия проверки мостов Tor
"""

import socket
import re
import sys
import time

def main_simple():
    print("═" * 50)
    print("🔧 ПРОВЕРКА МОСТОВ TOR")
    print("═" * 50)
    
    # Чтение файла torrc
    try:
        with open('/etc/tor/torrc', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Файл /etc/tor/torrc не найден")
        sys.exit(1)
    except PermissionError:
        print("❌ Нет прав на чтение файла. Используйте sudo.")
        sys.exit(1)
    
    # Поиск мостов
    bridge_pattern = r'Bridge\s+obfs4\s+(\d+\.\d+\.\d+\.\d+):(\d+)\s+([A-F0-9]+)\s+cert=([^\s]+)\s+iat-mode=\d'
    matches = re.findall(bridge_pattern, content)
    
    if not matches:
        print("❌ Мосты не найдены в файле torrc")
        sys.exit(1)
    
    print(f"📊 Найдено мостов: {len(matches)}")
    print("\n🔍 Проверка доступности...\n")
    
    working_bridges = []
    
    for i, match in enumerate(matches, 1):
        ip = match[0]
        port = int(match[1])
        fingerprint = match[2]
        cert = match[3]
        
        # Формируем оригинальную строку
        bridge_line = f"Bridge obfs4 {ip}:{port} {fingerprint} cert={cert} iat-mode=0"
        
        # Проверка порта
        print(f"[{i}/{len(matches)}] {ip}:{port}", end=' - ')
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            
            start = time.time()
            result = sock.connect_ex((ip, port))
            elapsed = time.time() - start
            
            sock.close()
            
            if result == 0:
                print(f"✅ РАБОТАЕТ ({elapsed:.2f}с)")
                working_bridges.append(bridge_line)
            else:
                print(f"❌ НЕДОСТУПЕН ({elapsed:.2f}с)")
                
        except socket.timeout:
            print("⏱️  ТАЙМАУТ")
        except Exception as e:
            print(f"⚠️  ОШИБКА: {str(e)[:20]}")
    
    # Вывод результатов
    print("\n" + "═" * 50)
    print("📊 ИТОГИ:")
    print(f"   Всего проверено: {len(matches)}")
    print(f"   ✅ Рабочих:      {len(working_bridges)}")
    print(f"   ❌ Недоступных:  {len(matches) - len(working_bridges)}")
    
    if len(matches) > 0:
        percent = (len(working_bridges) / len(matches)) * 100
        print(f"   📊 Процент:      {percent:.1f}%")
    
    print("\n✅ РАБОЧИЕ МОСТЫ:")
    print("-" * 50)
    
    if working_bridges:
        for i, bridge in enumerate(working_bridges, 1):
            print(f"{i:2d}. {bridge[:70]}..." if len(bridge) > 70 else f"{i:2d}. {bridge}")
    else:
        print("   Нет рабочих мостов")
    
    print("═" * 50)

if __name__ == "__main__":
    try:
        main_simple()
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")