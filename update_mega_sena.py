import requests
import time
import os

FILE_PATH = r"c:\Bruno\pessoal_codes\mega_sena_EDA\mega_sena_history.txt"
BASE_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_last_contest_id():
    if not os.path.exists(FILE_PATH):
        return 0
    with open(FILE_PATH, 'r') as f:
        lines = f.readlines()
        return len(lines)

def fetch_contest(contest_id):
    try:
        response = requests.get(f"{BASE_URL}{contest_id}", headers=HEADERS, verify=False, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching {contest_id}: {e}")
    return None

def update_file():
    last_id = get_last_contest_id()
    print(f"Last contest in file: {last_id}")
    
    # Check latest available contest
    latest_data = fetch_contest("")
    if not latest_data:
        print("Could not fetch latest contest info.")
        return

    latest_id = latest_data['numero']
    print(f"Latest available contest: {latest_id}")
    
    if last_id >= latest_id:
        print("File is up to date.")
        return

    new_data = []
    
    print(f"Fetching from {last_id + 1} to {latest_id}...")
    
    for i in range(last_id + 1, latest_id + 1):
        data = fetch_contest(i)
        if data:
            dezenas = data['listaDezenas']
            # Format: "D1 D2 D3 D4 D5 D6" (no brackets, space separated)
            # The API returns strings like "01", "02". The file seems to use integers or strings.
            # File sample: "1 6 24 47 55 58" (no leading zeros for single digits? let's check)
            # Sample read earlier: "1 6 24 47 55 58". So single digits have no leading zero.
            
            # Let's convert to int and back to string to remove leading zeros if necessary
            # or just keep as is if the file has mixed format.
            # The file sample "1→41 05 04..." had leading zeros "05", "04".
            # The END of file sample "1 6 24..." had NO leading zeros for "1", "6".
            # It seems inconsistent. I will use integer conversion to be safe/standard, 
            # or check what the user prefers. The notebook probably handles both.
            # Let's write as integers to save space and match the end of file style.
            
            line_numbers = [str(int(x)) for x in dezenas]
            line_str = " ".join(line_numbers)
            new_data.append(line_str)
            print(f"Fetched {i}: {line_str}")
        else:
            print(f"Failed to fetch {i}")
        
        time.sleep(0.2)
        
    if new_data:
        with open(FILE_PATH, 'a') as f:
            # Ensure we start on a new line if the file doesn't end with one
            # Actually readlines() usually keeps \n. Let's check if last char is \n.
            pass # simpler to just append "\n" + line if needed.
            
            # Re-read last char to be sure
            f_read = open(FILE_PATH, 'rb')
            try:
                f_read.seek(-1, 2)
                last_char = f_read.read(1)
            except IOError:
                last_char = b'\n'
            f_read.close()
            
            prefix = ""
            if last_char != b'\n':
                prefix = "\n"
                
            f.write(prefix + "\n".join(new_data) + "\n")
            print(f"Added {len(new_data)} contests to {FILE_PATH}")

if __name__ == "__main__":
    update_file()
