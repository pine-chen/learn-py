import re


def extract_view_routes(paths: list[str]) -> list[str]:
    routes: list[str] = []

    for path in paths:
        path = path.strip()

        if not path:
            continue

        match = re.search(r"src/views(.*?)/index\.vue$", path)

        if match:
            routes.append(match.group(1))

    return routes

def extract_js_routes(paths: list[str]) -> list[str]:
    routes: list[str] = []

    for path in paths:
        path = path.strip()

        if not path:
            continue

        match = re.search(r"src/views(.*?)/index\.js$", path)

        if match:
            routes.append(match.group(1))

    return routes