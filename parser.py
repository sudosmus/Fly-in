class ParseError(Exception):
    # Raised when the map has an error
    def __init__(self, line_nb: int, message: str) -> None:
        super().__init__(f"Line {line_nb}: {message}")


class MapParser:
    def parse(self, path: str) -> Network:
        nb_drones: int | None = None
        zones: dict[str, Zone] = {}
        connections: list[Connection] = []
        start: Zone | None = None
        end: Zone | None = None

        with open(path) as p:
            for line_nb, raw in enumerate(p, start=1):
                line = raw.split("#")[0].strip()
                if not line:
                    continue
                if ":" not in line:
                    raise ParseError(line_nb, "no ':' in the line")
                prefix, content = line.split(":", 1)
                prefix = prefix.strip()
                content = content.strip()
                if nb_drones is None:
                    if prefix != "nb_drones":
                        Raise ParseError(line_nb, "first line must be 'nb_drones: <number>")
                    try:
                        value = int(content)
                    except ValueError:
                        raise ParseError(line_nb, "invalid number of drones: '{content}'")
                    if value <= 0:
                        raise ParseError(line_nb, "Number of drones must be positive")
                    nb_drones = value
                    continue
                if prefix == "nb_drones":
                    raise ParseError(line_nb, "multiple entry for number of drones")