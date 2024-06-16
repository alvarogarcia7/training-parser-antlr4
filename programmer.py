from pprint import pprint
import argparse


def compute_programming(from_: float, to: float, days: int) -> list[float]:
    result = [0.0 for _ in range(days)]
    increase = (to - from_) / ((days - 1) / 2)

    from_top = to
    from_base = from_

    for i in range(len(result)):
        if i % 2 == 0:
            result[i] = from_base
            from_base += increase
        else:
            result[i] = from_top
            from_top -= increase

    return result


def percentage_of_volume(programming: list[float], max_volume: int) -> list[float]:
    return list(map(lambda percentage: (percentage * max_volume) / 100, programming))


def parse_range_string(val: str) -> range:
    to_value: str
    from_value: str
    from_: int
    to: int
    [from_value, to_value] = val.split('..')
    if '=' in to_value:
        to_value = to_value.removeprefix('=')
        to = int(to_value) + 1
    else:
        to = int(to_value)

    from_ = int(from_value)

    return range(from_ - 1, to - 1)


if __name__ == '__main__':
    programming = compute_programming(60.0, 100.0, 30)
    max_volume = 16000
    volumes = percentage_of_volume(programming, max_volume)

    parser = argparse.ArgumentParser(prog="programmer")

    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands')
    sb = subparsers.add_parser('print_all')
    sb.add_argument('print_all', default="true", help="Insert something. Discarded")

    sb1 = subparsers.add_parser('volume')
    sb1.add_argument('selection')

    matched_args = parser.parse_args()
    pprint(matched_args)

    if 'print_all' in matched_args:
        print(f"max volume: {max_volume} kg (100%)")
        print("day: percentage - volume ")
        for i in range(len(programming)):
            day_number = i + 1
            print("%2d: %5.1f%% - %5.0d kg" % (day_number, programming[i], volumes[i]))

    if 'selection' in matched_args:
        if '..' in matched_args.selection:
            rangex = parse_range_string(matched_args.selection)
        else:
            day = int(matched_args.selection)
            rangex = range(day, day + 1)

        print(f"max volume: {max_volume} kg (100%)")
        print("day: percentage - volume ")
        total_volume : float = 0
        for i in rangex:
            day_number = i + 1
            total_volume += volumes[i]
            print("%2d: %5.1f%% - %5.0d kg" % (day_number, programming[i], volumes[i]))
        print("total: %5.0d kg" % total_volume)
