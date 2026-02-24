from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings
import requests
import time
import csv
import os

RATE_LIMIT_THRESHOLD = 10       
RATE_LIMIT_SLEEP = 900

# Function to handle ESI responses and rate limits
def esi_call(response):
    remaining = int(response.headers.get("X-Ratelimit-Remaining", 999))

    if remaining < RATE_LIMIT_THRESHOLD:
        print(f"[RATE] Quedan pocos tokens ({remaining}). Pausando 15 minutos…")
        time.sleep(RATE_LIMIT_SLEEP)
        
    if response.status_code == 429:
        retry = int(response.headers.get("Retry-After", 10))
        print(f"[RATE] 429 recibido. Esperando {retry}s…")
        time.sleep(retry)
    
    if response.status_code == 420:
        print(f"[WARNING] remaing tokens {remaining}")
        print("[RATE] Error 420 recibido. Pausando 15 minutos…")
        time.sleep(RATE_LIMIT_SLEEP)
        print("[RATE] Descanso terminado, continuando…")

    if response.status_code == 401:
        print("[ERROR] Token inválido o sin permisos")

    return response

# Function to handle paginated ESI calls
def handler(url, headers, page):
    params = {"page": page}
    response = requests.get(url, headers=headers, params=params)
    response = esi_call(response)
    return response

# Function to handle paginated ESI calls with rate limit handling
def update_pages(max_retries, handler, url, headers):
    all_values = []

    first_response = handler(url, headers, 1)
    data = first_response.json()

    if data:
        all_values.extend(data)

    pages = int(first_response.headers.get("x-pages", 1))

    if pages <= 1:
        return all_values
    
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(handler, url, headers, page)
            for page in range(2, pages + 1)
        ]

        for future in as_completed(futures):
            try:
                resp = future.result()
                data = resp.json()
                if data:
                    all_values.extend(data)
            except Exception as e:
                raise RuntimeError(f"Error descargando página: {e}")

    return all_values



def format_number(n):
    sufijos = [(1_000_000_000_000, "T"), (1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")]
    
    for divisor, sufijo in sufijos:
        if abs(n) >= divisor:
            return f"{n / divisor:.2f} {sufijo}"

    return str(n)

def check_skill(pj_skill, skillplan):
        for skill, nivel in skillplan.items():
            if skill not in pj_skill or pj_skill[skill] < nivel:
                return False
        return True

def formater(text, items):
        for item in items:
            if item.get("flag").startswith("HiSlot") or item.get("flag").startswith("MedSlot") or item.get("flag").startswith("LoSlot") or item.get("flag").startswith("RigSlot") or item.get("flag").startswith("SubSystemSlot"):
                text.append(f"{item['itemName']}\n")
            else:
                text.append(f"{item['itemName']} x{item['quantity']}\n")

        text.append("\n")

        return text

def create_csv(data, filename):
    path = os.path.join(settings.BASE_DIR, "static", "csv", filename)
    with open(path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    return path