import os
import re
import sys
import subprocess


def slugify(name):
    name = re.sub(r'([a-z])([A-Z])', r'\1-\2', name)
    name = name.replace('.', '')
    name = name.replace(' ', '-')
    return name.lower()


def create_city(city_name):
    folder_name = slugify(city_name)

    # Base locations directory
    base_path = os.path.join(os.getcwd(), "locations")
    os.makedirs(base_path, exist_ok=True)

    # City folder
    final_path = os.path.join(base_path, folder_name)
    os.makedirs(final_path, exist_ok=True)

    # index.html path
    index_path = os.path.join(final_path, "index.html")

    # Create file if not exists
    if not os.path.exists(index_path):
        open(index_path, "w").close()

    print(f"Created: {final_path}")

    return index_path


cities = []

# If city passed as argument
if len(sys.argv) > 1:
    cities.append(" ".join(sys.argv[1:]))

# If multiple cities passed via STDIN
if not sys.stdin.isatty():
    for line in sys.stdin:
        line = line.strip()
        if line:
            cities.append(line)

if not cities:
    print("Usage:")
    print("python3 script.py Tuscaloosa")
    print("OR")
    print("python3 script.py <<EOF")
    print("City1")
    print("City2")
    print("EOF")
    sys.exit(1)


created_files = []

for city in cities:
    index_path = create_city(city)
    created_files.append(index_path)


# Open each file
for file in created_files:
    subprocess.run(["code", file])
    subprocess.run(["open", "-a", "Google Chrome", file])