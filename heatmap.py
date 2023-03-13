import argparse
import math
import os

from dotenv import load_dotenv
import mysql.connector
from PIL import Image
from tqdm import tqdm

load_dotenv(".env")
if os.path.exists(".env.dev"):
    load_dotenv(".env.dev", override=True)


def query_database(cursor, size: int, world_id: int):
    coordinates = {}
    query = "SELECT x, z FROM actions WHERE action_id IN (1, 2, 3)"
    query += " AND world_id = %d AND source = 5"
    query += " AND x BETWEEN %d AND %d AND z BETWEEN %d AND %d"

    cursor.execute(query % (world_id, -size, size, -size, size))
    for row in cursor.fetchall():
        coordinates[row] = coordinates.get(row, 0) + 1
    print(f"Successfuly fetched {sum(coordinates.values())} lines.")

    # Logarithmic scale
    coordinates = {k: math.log(v) for k, v in coordinates.items()}
    return coordinates


def get_palette(name: str):
    print(f"Loading '{name}' color palette...")
    with Image.open(f"palettes/{name}.png") as image:
        image = image.resize((256, 1))
        return [image.getpixel((i, 0)) for i in range(image.width)]


def generate_image(data: dict[tuple, int], size: int, name: str):
    colors = get_palette(name)
    max_val = max(data.values())
    image = Image.new("RGB", (size * 2, size * 2), colors[0])

    for (x, z), count in tqdm(data.items()):
        color = colors[int((len(colors) - 1) * count / max_val)]
        image.putpixel((x + size - 1, z + size - 1), color)

    image.save(f"results/heatmap_x{size}_{name}.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--size",
        type=int,
        default=2000,
        help="Map radius. /!\\ Generated image will be 2x this size.",
    )
    parser.add_argument("-w", "--world_id", type=int, default=1, help="World ID.")
    parser.add_argument(
        "-c",
        "--color",
        "--colors",
        "-p",
        "--palette",
        type=str,
        choices=[f.split(".")[0] for f in os.listdir("palettes")],
        default="rgb",
        help="Heatmap palette. Should be a filename in the 'palettes' folder.",
    )
    args = parser.parse_args()

    print("Connecting to database...")
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=str(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
    )
    cursor = connection.cursor()

    print("Querying database...")
    data = query_database(cursor, args.size, args.world_id)

    print("Generating image...")
    generate_image(data, args.size, args.color)

    cursor.close()
    connection.close()
