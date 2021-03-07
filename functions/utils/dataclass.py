import dataclasses


def map_as_dict(xs):
    return list(map(lambda x: dataclasses.asdict(x), xs))
