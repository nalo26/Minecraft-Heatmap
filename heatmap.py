import math
import os

from dotenv import load_dotenv
import mysql.connector
from PIL import Image
from tqdm import tqdm

load_dotenv(".env")
if os.path.exists(".env.dev"):
    load_dotenv(".env.dev", override=True)

BORDER_DIST = 2000
QUERY = "SELECT x, z FROM actions WHERE action_id IN (1, 2, 3) AND world_id = 1 AND source = 5"
QUERY += " AND x BETWEEN %d AND %d AND z BETWEEN %d AND %d" % (
    -BORDER_DIST,
    BORDER_DIST,
    -BORDER_DIST,
    BORDER_DIST,
)
COLORS = 256**3 - 1


def int_to_hex(i):
    return hex(i)[2:].zfill(6)


def hex_to_int_tuple(hex):
    return tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))


print("Connecting to database...")
mydb = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=str(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME"),
)
mycursor = mydb.cursor()
print("Connected.")

coordinates = {}

print("Querying database...")
mycursor.execute(QUERY)
for row in mycursor.fetchall():
    if row not in coordinates:
        coordinates[row] = 1
    else:
        coordinates[row] += 1
print(f"Successfuly fetched {sum(coordinates.values())} lines.")


# coordinates = {k: math.log(v, 2) for k, v in coordinates.items()}
max_val = max(coordinates.values())

print("Generating image...")
image = Image.new("RGB", (BORDER_DIST * 2, BORDER_DIST * 2), (0, 0, 0))

for (x, z), count in tqdm(coordinates.items()):
    color = hex_to_int_tuple(int_to_hex(int(COLORS * count / max_val)))
    image.putpixel((x + BORDER_DIST - 1, z + BORDER_DIST - 1), color)
print("Generated.")

image.save(f"heatmap_{BORDER_DIST}.png")
