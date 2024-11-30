# process_info.py

import psutil
import time
from datetime import timedelta, datetime

def get_system_info():
    # Get system information
    threads = 0
    for p in psutil.process_iter():
        try:
            threads += p.num_threads()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, RuntimeError):
            continue

    uptime_seconds = int(time.time() - psutil.boot_time())
    uptime_str = str(timedelta(seconds=uptime_seconds))
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    battery = psutil.sensors_battery()
    if battery:
        battery_str = f"{battery.percent}% {'Charging' if battery.power_plugged else 'Discharging'}"
    else:
        battery_str = "No Battery"

    return {
        'threads': threads,
        'uptime': uptime_str,
        'ram_percent': mem.percent,
        'swap_percent': swap.percent,
        'battery': battery_str,
        'ram_used': mem.used,
        'ram_total': mem.total,
        'swap_used': swap.used,
        'swap_total': swap.total,
        'cpu_percent': psutil.cpu_percent(interval=None)
    }

def format_elapsed_time(seconds):
    # Format elapsed time as Hh:Mm:Ss
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}h:{minutes}m:{secs}s"

def get_process_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'username', 'cpu_percent', 'memory_percent', 'name', 'num_threads', 'create_time', 'exe', 'status', 'nice']):
        try:
            pid = proc.info['pid']
            username = proc.info.get('username', '')
            cpu_percent = proc.info.get('cpu_percent') or 0.0
            mem_percent = proc.info.get('memory_percent') or 0.0
            name = proc.info.get('name', '')
            num_threads = proc.info.get('num_threads', 0)
            status = proc.info.get('status', '')
            nice = proc.info.get('nice', 0)
            create_time = proc.info.get('create_time', None)
            if create_time:
                elapsed_time_seconds = time.time() - create_time
                time_str = format_elapsed_time(elapsed_time_seconds)
            else:
                time_str = ''
            exe = proc.info.get('exe', '') or ''
            processes.append({
                'pid': pid,
                'username': username,
                'cpu_percent': cpu_percent,
                'mem_percent': mem_percent,
                'name': name,
                'num_threads': num_threads,
                'status': status,
                'nice': nice,
                'time': time_str,
                'exe': exe
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, RuntimeError):
            continue
    return processes
