import subprocess
import os
import threading
import datetime
import shutil
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

results = {}

# ANSI color codes for random banner color
COLORS = [
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[93m",  # Yellow
    "\033[94m",  # Blue
    "\033[95m",  # Magenta
    "\033[96m",  # Cyan
    "\033[97m",  # White
]
RESET = "\033[0m"

def get_banner():
    BANNER = r"""
    ___   ________ _______  _____  _____  _   _   ___  
   / _ \ |__  /_ _|__  / _ \|_   _||_   _|| | | | / _ \ 
  / /_\/   / / | |  / / | | | | |    | |  | |_| |/ /_\/ 
 / /_\\   / /_ | | / /| |_| | | |    | |  |  _  ||  _  | 
/____/  /____||_|/____\___/  |_|    |_|  |_| |_||_| |_| 
                                                        
         AZTRINO — Automated Subdomain Enumerator 🚀
"""
    color = random.choice(COLORS)
    return color + BANNER + RESET

# Tools configuration
TOOLS = {
    "subfinder": {"cmd": "subfinder -d {domain} -silent", "check": "subfinder"},
    "sublist3r": {"cmd": "sublist3r -d {domain} -o temp_sublist3r.txt", "check": "sublist3r", "outfile": "temp_sublist3r.txt"},
    "assetfinder": {"cmd": "assetfinder --subs-only {domain}", "check": "assetfinder"},
    "subbrute": {"cmd": "python subbrute.py {domain}", "check": "subbrute.py"}  # assumes local script
}

def run_tool(name, command, output_file=None):
    try:
        if output_file:
            subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(output_file):
                with open(output_file, "r") as f:
                    results[name] = f.read().splitlines()
                os.remove(output_file)
        else:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL)
            results[name] = result.decode().splitlines()
    except subprocess.CalledProcessError:
        results[name] = []
    except FileNotFoundError:
        results[name] = []

def is_tool_installed(tool_name):
    """Check if tool is installed or accessible"""
    if tool_name.endswith(".py"):
        return os.path.exists(tool_name)
    return shutil.which(tool_name) is not None

def check_single_subdomain(sub):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AZTRINO/1.0)"}
    urls = [f"https://{sub}", f"http://{sub}"]
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=3, verify=False)
            if r.status_code < 500:
                return (sub, "LIVE")
        except:
            continue
    return (sub, "DEAD")

def check_live_dead(subdomains, threads=50):
    results_status = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_sub = {executor.submit(check_single_subdomain, sub): sub for sub in subdomains}
        for future in as_completed(future_to_sub):
            sub, status = future.result()
            results_status.append((sub, status))
    return results_status

def main():
    print(get_banner())
    start_time = datetime.datetime.now()
    print(f"[+] Scan started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    domain = input("Enter the target domain: ").strip()

    threads = []
    print("[+] Checking available tools...\n")

    for tool, info in TOOLS.items():
        if is_tool_installed(info["check"]):
            print(f"    ✔ {tool} found, running...")
            cmd = info["cmd"].format(domain=domain)
            t = threading.Thread(target=run_tool, args=(tool, cmd, info.get("outfile")))
            threads.append(t)
        else:
            print(f"    ✘ {tool} not found, skipping.")
            results[tool] = []

    print("\n[+] Launching enumeration...\n")

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Merge results
    all_subs = set()
    print("\n[+] Results Summary:")
    for tool, subs in results.items():
        print(f"    - {tool:<10} found {len(subs)} subdomains")
        all_subs.update(subs)

    print(f"\n[+] Total unique subdomains: {len(all_subs)}\n")

    if not all_subs:
        print("[-] No subdomains found. Exiting.")
        return

    # Check live/dead
    print("[+] Checking which subdomains are live (multi-threaded)...")
    results_status = check_live_dead(sorted(all_subs), threads=50)

    live = [s for s, st in results_status if st == "LIVE"]
    dead = [s for s, st in results_status if st == "DEAD"]

    print(f"\n[+] Live subdomains ({len(live)}):")
    for sub in live:
        print("   ", sub)

    print(f"\n[+] Dead subdomains ({len(dead)}):")
    for sub in dead:
        print("   ", sub)

    # Ask to save with custom filename
    choice = input("\nDo you want to save results to a single file? (y/n): ").lower()
    if choice == "y":
        filename = input("Enter filename to save results (e.g. results.txt): ").strip()
        if not filename.endswith(".txt"):
            filename += ".txt"
        with open(filename, "w") as f:
            f.write("=== LIVE Subdomains ===\n")
            for sub in sorted(live):
                f.write(f"{sub}\n")
            f.write("\n=== DEAD Subdomains ===\n")
            for sub in sorted(dead):
                f.write(f"{sub}\n")
        print(f"[+] Results saved to {filename}")
    else:
        print("[+] Results not saved.")

    end_time = datetime.datetime.now()
    print(f"\n[+] Scan finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[+] Duration: {end_time - start_time}")

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    main()
