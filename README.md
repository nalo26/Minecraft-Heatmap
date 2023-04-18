# Minecraft Heatmap Generator
Create a heatmap of your server based on block interaction (block breaking and placing).

It uses the logs of the [Ledger mods](https://github.com/QuiltServerTools/Ledger), and the MySQL configuration of the [Ledger Database](https://github.com/QuiltServerTools/Ledger-Databases) mod extension.

## Configuration

Open the `.env` file, and put your database credentials in it.

## Usage

```
python3 heatmap.py [OPTIONS]

Options:
    -h, --help              Show this message and exit. Defaults values are in []
    -c, --center COORD      Coordinate of the center of the heatmap. Use "--center='x,z'" for negative values. [0,0]
    -s, --size SIZE         Map radius. /!\ Generated image will be 2x this size. [2000]
    -w, --world WORLD       The world to make the map from. Defaults choices are {[overworld], the_nether, the_end}
    -u, --players PLAYERS   The players to track, splited by a comma (","). [everyone]
    -p, --palette FILE      Heatmap palette. Should be a filename in the 'palettes' folder. [rgb]

Example:
    python3 heatmap.py --center="-400,600" -s 200 -w the_nether -u Notch,Jeb -p nether
```

## Custom palettes

You can add your own custom palette by adding them in the `palettes` folder.
For a better result, the image should have a **width of at least 256px**.
You can generate gradients image easily using a [website maker](https://angrytools.com/gradient/image/), or any tool that you want.

## Result examples

> Those examples are taken from the Survival Multiplayer (SMP) between Twitch Subscribers of [MathoX](https://twitch.tv/MathoX)

`python3 heatmap.py` (equivalent to `python3 heatmap.py -c 0,0 -s 2000 -w overworld -p rgb`)  
<img src="results/heatmap_0,0_x2000_overworld_rgb.png">

`python3 heatmap.py --center="-1460,430" -s 150`  
<img src="results/heatmap_-1460,430_x150_overworld_rgb.png" width="300">

`python3 heatmap.py -s 100 -w the_nether -p nether`  
<img src="results/heatmap_0,0_x100_the_nether_nether.png" widht="300">
