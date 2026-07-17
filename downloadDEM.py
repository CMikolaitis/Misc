import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Handle pathing
here    = Path(".")
destDir = here / Path("DEM_W")
destDir.mkdir(parents=True, exist_ok=True)

# Func to download
def download(url):
    filename = Path(url).name
    outfile = destDir / filename

    if outfile.exists():
        print(f"Skipping {filename} (already exists)")
        return

    try:
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()

        with open(outfile, "wb") as out:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    out.write(chunk)

        print(f"Downloaded {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Failed {filename}: {e}")

# Read in file with all download urls, needs to be newline for each
with open("MobileCountyDEM2023.txt") as f:
    urls = [line.strip() for line in f if line.strip()]

# Download multiple at once
with ThreadPoolExecutor(max_workers=8) as pool:
    pool.map(download, urls)
