# subhunter

subhunter is a simple automated tool for finding subdomains of a target domain.  
It uses different tools like **Subfinder**, **Sublist3r**, **Assetfinder**, and **Subbrute** to collect subdomains.  
After collecting, it removes duplicates and checks which subdomains are **live** or **dead**.  

The results are shown in the terminal and can also be saved into a file in a clear format.

---

## ✨ Features
- Collects subdomains from multiple tools  
- Removes duplicate results  
- Checks which subdomains are live and dead  
- Shows results in the terminal  
- Saves results in a single file (live first, then dead)  
- Simple and beginner-friendly  

---

## ⚙️ Installation
Make sure you have **Python 3** and the required tools installed.

```bash
# Clone this repository

git clone git@github.com:akshaybarjun/subhunter.git

# Go into the folder

cd subhunter-main

# Install requirements

python subhunter.py
