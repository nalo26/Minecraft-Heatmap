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


def tuple_type(strings: str):
    strings = strings.replace("(", "").replace(")", "")
    int_tuple = tuple(map(int, strings.split(",")))
    assert len(int_tuple) == 2, "Invalid tuple length."
    return int_tuple


def query_database(cursor, center: tuple[int], size: int, world: str):
    coordinates = {}
    query = "SELECT x, z FROM actions WHERE action_id IN (1, 2, 3)"
    query += " AND source = 5 AND world_id ="
    query += " (SELECT id FROM worlds WHERE identifier = 'minecraft:%s')"
    query += " AND x BETWEEN %d AND %d AND z BETWEEN %d AND %d"

    cursor.execute(
        query
        % (
            world,
            center[0] - size,
            center[0] + size,
            center[1] - size,
            center[1] + size,
        )
    )

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


def generate_image(data: dict[tuple, int], center: tuple[int], size: int, name: str):
    colors = get_palette(name)
    big_values = sorted(data.values(), reverse=True)[:50]
    max_val = sum(big_values) // len(big_values)
    image = Image.new("RGB", (size * 2, size * 2), colors[0])

    for (x, z), value in tqdm(data.items()):
        value = min(value, max_val)
        color = colors[int((len(colors) - 1) * value / max_val)]
        (of_x, of_z) = (x - center[0] + size - 1, z - center[1] + size - 1)
        try:
            image.putpixel((of_x, of_z), color)
        except IndexError:
            print(x, z, "->", of_x, of_z)
            raise

    return image


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--center",
        type=tuple_type,
        default="0,0",
        help="Coordinate of the center of the heatmap.",
    )
    parser.add_argument(
        "-s",
        "--size",
        type=int,
        default=2000,
        help="Map radius. /!\\ Generated image will be 2x this size.",
    )
    parser.add_argument(
        "-w",
        "--world",
        type=str,
        default="overworld",
        help="The world to make the map from.",
    )
    parser.add_argument(
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
    data = query_database(cursor, args.center, args.size, args.world)

    print("Generating image...")
    image = generate_image(data, args.center, args.size, args.palette)
    image.save(
        f"results/heatmap_{','.join(str(n) for n in args.center)}"
        f"_x{args.size}_{args.world}_{args.palette}.png"
    )

    cursor.close()
    connection.close()
