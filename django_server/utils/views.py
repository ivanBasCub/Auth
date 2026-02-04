from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

def handler(url, headers, page):
    params = {"page":page}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status() 
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
