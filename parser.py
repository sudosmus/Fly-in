from models import Zone, Connection, ZoneType, Network


class ParseError(Exception):
    """ Raised when the map has an error """
    def __init__(self, line_nb: int, message: str) -> None:
        super().__init__(f"Line {line_nb}: {message}")


class MapParser:
    """ Takes the file name as arg, returns a network object """
    def parse(self, path: str) -> Network:
        nb_drones: int | None = None
        zones: dict[str, Zone] = {}
        connections: list[Connection] = []
        start: Zone | None = None
        end: Zone | None = None
        seen_pairs: set[frozenset[str]] = set()

        with open(path) as p:
            for line_nb, raw in enumerate(p, start=1):
                line = raw.split("#")[0].strip()
                if not line:
                    continue
                if ":" not in line:
                    raise ParseError(line_nb, "no ':' in the line")
                prefix, content = line.split(": ", 1)
                prefix = prefix.strip()
                content = content.strip()
                if nb_drones is None:
                    if prefix != "nb_drones":
                        raise ParseError(line_nb, "first line must be 'nb_drones: <number>")
                    try:
                        value = int(content)
                    except ValueError:
                        raise ParseError(line_nb, f"invalid number of drones: '{content}'")
                    if value <= 0:
                        raise ParseError(line_nb, "Number of drones must be positive")
                    nb_drones = value
                    continue
                if prefix == "nb_drones":
                    raise ParseError(line_nb, "multiple entry for number of drones")
                elif prefix in ("start_hub", "end_hub", "hub"):
                    zone = self._parse_zone(content, line_nb)
                    if zone.name in zones:
                        raise ParseError(line_nb, f"multiple entry for zone name {zone.name}")
                    zones[zone.name] = zone

                    if prefix == "start_hub":
                        if start is not None:
                            raise ParseError(line_nb, "multiple start_hub")
                        start = zone
                    elif prefix == "end_hub":
                        if end is not None:
                            raise ParseError(line_nb, "multiple end hub")
                        end = zone
                elif prefix == "connection":
                    connection = self._parse_connection(line_nb, content, zones)
                    pair = frozenset({connection.a.name, connection.b.name})
                    if pair in seen_pairs:
                        raise ParseError(line_nb, f"duplicate connection{content}")
                    seen_pairs.add(pair)
                    connections.append(connection)
                else:
                    raise ParseError(line_nb, f"Unknown entry: '{prefix}'")
        if nb_drones is None:
            raise ParseError(0, "file is empty or has no nb_drones line")
        if start is None:
            raise ParseError(0, "missing start_hub")
        if end is None:
            raise ParseError(0, "missing end_hub")
        return Network(nb_drones, zones, connections, start, end
        )

    def _parse_connection(self, line_nb: int, content: str, zones: dict[str, Zone]) -> Connection:
        if "[" in content:
            index = content.index("[")
            main = content[:index].strip()
            meta_text = content[index:].strip()
        else:
            main = content
            meta_text = ""
        try:
            a_text, b_text = main.split("-")
        except ValueError:
            raise ParseError(line_nb, f"Invalid format in connection {main}")
        a_text = a_text.strip()
        b_text = b_text.strip()
        for name in (a_text, b_text):
            if name not in zones:
                raise ParseError(line_nb, f"unknown zone name: '{name}'")
        meta = self._parse_metadata(meta_text, line_nb)
        for key in meta:
            if key != "max_link_capacity":
                raise ParseError(line_nb, f"unknown metadata: '{key}'")
        cap_text = meta.get("max_link_capacity", "1")
        try:
            capacity = int(cap_text)
        except ValueError:
            raise ParseError(line_nb, f"capacity must be an integer: '{cap_text}'")
        if capacity <= 0:
            raise ParseError(line_nb, "max_link_capacity must be positive")
        return Connection(zones[a_text], zones[b_text], capacity)
      
        



    def _parse_zone(self, content: str, line_nb: int) -> Zone:
        if "[" in content:
            index = content.index("[")
            main = content[:index].strip()
            meta_text = content[index:].strip()
        else:
            main = content
            meta_text = ""
        
        try:
            name, x_text, y_text = main.split()
        except ValueError:
            raise ParseError(line_nb, "expected '<name> <x> <y>'")
        try:
            x = int(x_text)
            y = int(y_text)
        except ValueError:
            raise ParseError(line_nb, f"Coordinates must be integers: '{x_text} {y_text}'")
        if "-" in name:
            raise ParseError(line_nb, f"Found '-' in the zone name: {name}")
        meta = self._parse_metadata(meta_text, line_nb)
        allowed = {"color", "zone", "max_drones"}
        for key in meta:
            if key not in allowed:
                raise ParseError(line_nb, f"invalid meta data key: '{key}'")
        type_text = meta.get("zone", "normal")
        try:
            zone_type = ZoneType(type_text)
        except ValueError:
            raise ParseError(line_nb, f"invalid zone type: '{type_text}'")
        color = meta.get("color")
        max_dtext = meta.get("max_drones", "1")
        try:
            max_drones = int(max_dtext)
        except ValueError:
            raise ParseError(line_nb, f"max drones must be integer: '{max_dtext}'")
        if max_drones <= 0:
            raise ParseError(line_nb, "max drones must be positive")
        return Zone(name, x, y, zone_type, color, max_drones)


    def _parse_metadata(self, meta_text: str, line_nb: int) -> dict[str, str]:
        """Turn [key=value ...] into a dict of strings"""
        result: dict[str, str] = {}
        if not meta_text:
            return result
        if not meta_text.startswith("["):
            raise ParseError(line_nb, f"meta data in wrong format {meta_text}")
        if not meta_text.endswith("]"):
            raise ParseError(line_nb, f"meta data in wrong format {meta_text}")
        wo_brackets = meta_text[1:-1]
        for item in wo_brackets.split():
            try:
                key, value = item.split("=")
            except ValueError:
                raise ParseError(line_nb, f"Error in meta data format '{item}'")
            if not key or not value:
                raise ParseError(line_nb, f"Invalid meta data item '{item}'")
            if key in result:
                raise ParseError(line_nb, f"duplicate meta data key '{key}'")
            result[key] = value
        return result

           
    