import socket
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def parse_bridges(filename):
   
    bridges = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Ищем IP и порт в строке
                # Формат: obfs4 IP:PORT ...
                match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)', line)
                if match:
                    ip = match.group(1)
                    port = int(match.group(2))
                    bridges.append({
                        'line': line,
                        'ip': ip,
                        'port': port,
                        'line_num': line_num
                    })
                else:
                    print(f"⚠️  Не удалось распознать строку {line_num}: {line[:50]}...")
        
        print(f"📄 Прочитано {len(bridges)} мостов из файла")
        return bridges
    
    except FileNotFoundError:
        print(f"❌ Файл {filename} не найден")
        return []
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")
        return []

def check_port(host, port, timeout=3):
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0  # 0 означает успешное подключение
    
    except socket.timeout:
        return False
    except socket.gaierror:
        return False  # Ошибка разрешения имени
    except Exception as e:
        print(f"⚠️  Ошибка при проверке {host}:{port}: {e}")
        return False

def check_bridge(bridge, timeout=3):
    
    ip = bridge['ip']
    port = bridge['port']
    line = bridge['line']
    
    print(f"🔍 Проверяю {ip}:{port}...", end=' ', flush=True)
    
    start_time = time.time()
    is_alive = check_port(ip, port, timeout)
    elapsed = time.time() - start_time
    
    if is_alive:
        print(f"✅ Доступен ({elapsed:.2f} сек)")
        return line, elapsed, True
    else:
        print(f"❌ Недоступен ({elapsed:.2f} сек)")
        return line, elapsed, False

def save_working_bridges(bridges, filename="actual_bridges.txt"):
    """Сохранение рабочих мостов в файл"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for bridge_line in bridges:
                f.write(bridge_line + '\n')
        
        print(f"\n💾 Рабочие мосты сохранены в {filename}")
        print(f"📊 Сохранено {len(bridges)} из {len(all_bridges)} мостов")
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении файла: {e}")

def main():
    input_file = "bridges.txt"
    output_file = "actual_bridges.txt"
    
    print("=" * 50)
    print("🔧 ПРОВЕРКА OBFS4 МОСТОВ TOR")
    print("=" * 50)
    
    # Читаем мосты из файла
    all_bridges = parse_bridges(input_file)
    
    if not all_bridges:
        print("❌ Нет мостов для проверки")
        return
    
    print(f"\n🚀 Начинаю проверку {len(all_bridges)} мостов...")
    print("=" * 50)
    
    working_bridges = []
    dead_bridges = []
    total_time = 0
    
    # Используем многопоточность для ускорения проверки
    max_workers = min(20, len(all_bridges))  # Не более 20 потоков
    print(f"🧵 Использую {max_workers} потоков для проверки")
    
    start_total_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Запускаем проверку всех мостов
        future_to_bridge = {
            executor.submit(check_bridge, bridge, 3): bridge 
            for bridge in all_bridges
        }
        
        # Обрабатываем результаты по мере завершения
        for future in as_completed(future_to_bridge):
            bridge = future_to_bridge[future]
            try:
                line, elapsed, is_alive = future.result()
                total_time += elapsed
                
                if is_alive:
                    working_bridges.append(line)
                else:
                    dead_bridges.append(line)
                    
            except Exception as e:
                print(f"⚠️  Ошибка при проверке моста: {e}")
                dead_bridges.append(bridge['line'])
    
    elapsed_total = time.time() - start_total_time
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ")
    print("=" * 50)
    
    # Статистика
    total = len(all_bridges)
    working = len(working_bridges)
    dead = len(dead_bridges)
    
    print(f"✅ Рабочие мосты: {working}/{total} ({working/total*100:.1f}%)")
    print(f"❌ Недоступные: {dead}/{total} ({dead/total*100:.1f}%)")
    print(f"⏱️  Общее время проверки: {elapsed_total:.2f} сек")
    print(f"⏱️  Среднее время на мост: {elapsed_total/total:.2f} сек")
    
    if working_bridges:
        # Сохраняем рабочие мосты
        save_working_bridges(working_bridges, output_file)
        
        # Показываем первые 5 рабочих мостов
        print(f"\n📋 Первые 5 рабочих мостов:")
        for i, bridge in enumerate(working_bridges[:5], 1):
            print(f"  {i}. {bridge[:80]}...")
        
        if len(working_bridges) > 5:
            print(f"  ... и еще {len(working_bridges) - 5} мостов")
    
    else:
        print("\n⚠️  Нет рабочих мостов! actual_bridges.txt не будет создан")
    
    # Опционально: сохраняем список недоступных мостов
    if dead_bridges:
        try:
            with open("dead_bridges.txt", 'w', encoding='utf-8') as f:
                for bridge in dead_bridges:
                    f.write(bridge + '\n')
            print(f"\n📝 Список недоступных мостов сохранен в dead_bridges.txt")
        except:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Проверка прервана пользователем")
    except Exception as e:
        print(f"\n❌ Непредвиденная ошибка: {e}")