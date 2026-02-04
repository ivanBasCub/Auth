from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time
RATE_LIMIT_THRESHOLD = 10       
RATE_LIMIT_SLEEP = 900

def esi_call(response):
    remaining = int(response.headers.get("X-Ratelimit-Remaining", 999))
    used = int(response.headers.get("X-Ratelimit-Used", 0))
    limit = response.headers.get("X-Ratelimit-Limit", "unknown")
    
    print(f"[RATE] Remaining={remaining} Used={used} Limit={limit}")
    
    if remaining < RATE_LIMIT_THRESHOLD:
        print(f"[RATE] Quedan pocos tokens ({remaining}). Pausando 15 minutos…")
        time.sleep(RATE_LIMIT_SLEEP)

    if response.status_code == 429:
        retry = int(response.headers.get("Retry-After", 10))
        print(f"[RATE] 429 recibido. Esperando {retry}s…")
        time.sleep(retry)
    
    if response.status_code == 420:
        print("[RATE] Error 420 recibido. Pausando 15 minutos…")
        time.sleep(RATE_LIMIT_SLEEP)

    if response.status_code == 401:
        print("[ERROR] Token inválido o sin permisos")

    return response

def handler(url, headers, page):
    params = {"page": page}
    response = requests.get(url, headers=headers, params=params)
    response = esi_call(response)
    
    return response


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
