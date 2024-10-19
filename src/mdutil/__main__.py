import argparse

from tilemap import MapImageBuilder


def main(args):

    try:
        builder = MapImageBuilder(
            args.json_path, args.tileset_path, args.lo_layer_name, args.hi_layer_name
        )
        builder.save(args.output_path)

    except Exception as e:
        print(f"{e}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Build a map image from a tiled json file."
    )
    parser.add_argument("json_path", type=str, help="Path to the tiled json file.")
    parser.add_argument(
        "tileset_path", type=str, help="Path to the tileset image in 8bpp format."
    )
    parser.add_argument("output_path", type=str, help="Path to the output map image.")
    parser.add_argument(
        "--lo-layer-name",
        type=str,
        help="Name of the low priority layer. Defaults to 'LO'.",
        default="LO",
    )
    parser.add_argument(
        "--hi-layer-name",
        type=str,
        help="Name of the hi priority layer. Defaults to 'HI",
        default="HI",
    )

    main(parser.parse_args())
