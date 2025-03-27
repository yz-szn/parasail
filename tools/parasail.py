import json
import time
import requests
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from utils.logger import log

API_BASE_URL = "https://www.parasail.network/api"
TOKENS_FILE = "data/tokens.txt"
CHECK_IN_INTERVAL = 86400
DELAY_BETWEEN_CYCLES = 3600  

def create_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1)
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def load_tokens():
    try:
        with open(TOKENS_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        log("Parasail BOT", f"Gagal memuat file tokens.txt: {str(e)}", "ERROR")
        return []

def onboard_node(session, token, address):
    url = f"{API_BASE_URL}/v1/node/onboard"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {"address": address}
    
    try:
        response = session.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        if data.get('success'):
            log("Parasail BOT", f"Onboard node berhasil untuk {address[:6]}...{address[-4:]}", "SUCCESS")
            return True
        else:
            log("Parasail BOT", f"Onboard gagal: {data.get('error', 'Unknown error')}", "ERROR")
    except Exception as e:
        log("Parasail BOT", f"Onboard error: {str(e)}", "ERROR")
    
    return False

def check_in_node(session, token, address):
    url = f"{API_BASE_URL}/v1/node/check_in"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {"address": address}
    
    try:
        response = session.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        if data.get('success'):
            log("Parasail BOT", f"Check-in berhasil untuk {address[:6]}...{address[-4:]}", "SUCCESS")
            return True
        else:
            log("Parasail BOT", f"Check-in gagal: {data.get('error', 'Unknown error')}", "ERROR")
    except Exception as e:
        log("Parasail BOT", f"Check-in error: {str(e)}", "ERROR")
    
    return False

def get_node_stats(session, token, address):
    url = f"{API_BASE_URL}/v1/node/node_stats?address={address}"
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = session.get(url, headers=headers, timeout=30)
        return response.json()
    except Exception as e:
        log("Parasail BOT", f"Gagal get stats: {str(e)}", "ERROR")
        return None

def print_wallet_header(address):
    log("Parasail BOT", "=" * 61, "INFO")
    log("Parasail BOT", f"Processing wallet: {address}", "INFO")

def process_wallet(session, token):
    try:
        payload = token.split('.')[1] + '=='
        import base64
        decoded = json.loads(base64.b64decode(payload).decode('utf-8'))
        address = decoded.get('address')
        
        if not address:
            log("Parasail BOT", "Token tidak valid", "ERROR")
            return False

        print_wallet_header(address)
        stats = get_node_stats(session, token, address)
        if not stats or not stats.get('success'):
            log("Parasail BOT", "Gagal mendapatkan statistik", "ERROR")
            return False
            
        node_data = stats['data']
        if not node_data.get('has_node', False):
            log("Parasail BOT", "Node belum aktif, melakukan onboard...", "WARN")
            if not onboard_node(session, token, address):
                return False
            time.sleep(5)
            stats = get_node_stats(session, token, address)
            if not stats or not stats.get('success'):
                return False
            node_data = stats['data']
            log("Parasail BOT", "Status: Aktif", "SUCCESS")
        else:
            log("Parasail BOT", "Status: Sudah aktif", "INFO")
        last_checkin = node_data.get('last_checkin_time', 0)
        if last_checkin > 0:
            last_str = datetime.fromtimestamp(last_checkin).strftime('%Y-%m-%d %H:%M:%S')
            log("Parasail BOT", f"Terakhir Check-in: {last_str}", "INFO")
        else:
            log("Parasail BOT", "Belum pernah check-in", "WARN")
        
        log("Parasail BOT", f"Points: {node_data.get('points', 0)}", "INFO")
        current_time = time.time()
        if last_checkin > 0 and (current_time - last_checkin) < CHECK_IN_INTERVAL:
            next_checkin = last_checkin + CHECK_IN_INTERVAL
            remaining = str(timedelta(seconds=int(next_checkin - current_time)))
            log("Parasail BOT", f"Bisa check-in lagi dalam: {remaining}", "INFO")
        else:
            log("Parasail BOT", "Melakukan check-in...", "INFO")
            if check_in_node(session, token, address):
                time.sleep(5)
                updated_stats = get_node_stats(session, token, address)
                if updated_stats and updated_stats.get('success'):
                    log("Parasail BOT", f"Points terbaru: {updated_stats['data'].get('points', 0)}", "SUCCESS")
        
        return True
        
    except Exception as e:
        log("Parasail BOT", f"Process wallet error: {str(e)}", "ERROR")
        return False

def run():
    while True: 
        session = create_session()
        tokens = load_tokens()
        
        if not tokens:
            log("Parasail BOT", "Tidak ada token yang ditemukan", "ERROR")
            time.sleep(DELAY_BETWEEN_CYCLES)  
            continue

        log("Parasail BOT", f"Memulai proses untuk {len(tokens)} wallet...", "INFO")
        
        success_count = 0
        for idx, token in enumerate(tokens, 1):
            if process_wallet(session, token):
                success_count += 1
            if idx < len(tokens):
                time.sleep(2)

        log("Parasail BOT", f"Ringkasan: {success_count} dari {len(tokens)} wallet berhasil diproses", "INFO")
        log("Parasail BOT", f"Menunggu {DELAY_BETWEEN_CYCLES//3600} jam sebelum memulai lagi...", "INFO")
        for remaining in range(DELAY_BETWEEN_CYCLES, 0, -1):
            hours, remainder = divmod(remaining, 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"Menunggu {hours:02d}:{minutes:02d}:{seconds:02d} sebelum memulai lagi...", end="\r")
            time.sleep(1)
        print("\n")

if __name__ == "__main__":
    run()