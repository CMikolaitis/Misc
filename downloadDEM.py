import requests
from pathlib import Path

here = Path(".")

with open("MobileCountyDEM2023.txt") as f:
    for line in f:
        url = line.strip()
        if not url:
            continue

        filename = Path(url).name
        outfile = here / filename
        
        if outfile.exists():
            print(f"Skipping {filename} (already exists)")
            continue
        
        try:
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()

            with open(outfile, "wb") as out:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive chunks
                        out.write(chunk)

            print(f"Downloaded {filename}")

        except requests.exceptions.RequestException as e:
            print(f"Failed {filename}: {e}")