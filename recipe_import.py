"""Read public Recipe JSON-LD and return a review draft for Family Fuel."""
import http.client
import ipaddress
import json
import os
import re
import socket
import ssl
import threading
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urljoin, urlsplit, urlunsplit

SITE_ORIGIN = "https://family-fuel.onrender.com"
MAX_PAGE = 3 * 1024 * 1024
REDIRECTS = {301, 302, 303, 307, 308}
PIN_HOSTS = {"pinterest.com", "www.pinterest.com"}
FETCH_SLOTS = threading.BoundedSemaphore(4)


class ImportErrorForUser(ValueError):
    pass


def public_url(value):
    if not isinstance(value, str) or len(value) > 2048 or re.search(r"[\\\x00-\x20\x7f]", value):
        raise ImportErrorForUser("Enter a public HTTPS Pin or recipe link.")
    url = urlsplit(value)
    if (url.scheme != "https" or not url.hostname or url.port not in (None, 443)
            or url.username is not None or "." not in url.hostname):
        raise ImportErrorForUser("Enter a public HTTPS Pin or recipe link.")
    host = url.hostname.rstrip(".").encode("idna").decode("ascii")
    if not re.fullmatch(r"[a-z0-9.-]+", host):
        raise ImportErrorForUser("Enter a public HTTPS Pin or recipe link.")
    path = url.path or "/"
    query = url.query
    if host in PIN_HOSTS:
        pin = re.match(r"^/pin/(\d+)(?:/|$)", path)
        if pin:
            path, query = f"/pin/{pin.group(1)}/", ""
    return urlunsplit(("https", host, path, query, ""))


class PublicConnection(http.client.HTTPSConnection):
    def connect(self):
        addresses = socket.getaddrinfo(self.host, 443, type=socket.SOCK_STREAM)
        if not addresses or any(
            not ipaddress.ip_address(entry[4][0]).is_global or ipaddress.ip_address(entry[4][0]).is_multicast
            for entry in addresses
        ):
            raise ImportErrorForUser("The recipe link must point to a public website.")
        last_error = None
        for family, kind, protocol, _, address in addresses[:4]:
            connection = socket.socket(family, kind, protocol)
            try:
                connection.settimeout(5)
                connection.connect(address)
                self.sock = self._context.wrap_socket(connection, server_hostname=self.host)
                return
            except OSError as error:
                connection.close()
                last_error = error
        raise last_error


def fetch_page(value):
    for _ in range(5):
        url = public_url(value)
        parsed = urlsplit(url)
        connection = PublicConnection(parsed.hostname, timeout=5, context=ssl.create_default_context())
        try:
            target = urlunsplit(("", "", parsed.path, parsed.query, ""))
            connection.request("GET", target, headers={
                "User-Agent": "FamilyFuelRecipeImporter/1.0",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Encoding": "identity",
            })
            response = connection.getresponse()
            if response.status in REDIRECTS and response.getheader("Location"):
                value = urljoin(url, response.getheader("Location"))
                continue
            if response.status != 200:
                raise ImportErrorForUser("This site did not return a public recipe page. Try the original recipe link.")
            if "html" not in (response.getheader("Content-Type") or "").lower():
                raise ImportErrorForUser("The link must open an HTML recipe page.")
            data = response.read(MAX_PAGE + 1)
            if len(data) > MAX_PAGE:
                raise ImportErrorForUser("The recipe page is too large to import.")
            return url, data.decode("utf-8", errors="replace")
        finally:
            connection.close()
    raise ImportErrorForUser("The link redirected too many times. Try the original recipe link.")


class RecipeMarkup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks = []
        self.script = None
        self.source = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.script = []
        if tag == "meta" and attrs.get("property") in {"pinterestapp:source", "og:see_also"}:
            self.source = self.source or attrs.get("content")

    def handle_data(self, data):
        if self.script is not None:
            self.script.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.script is not None:
            self.blocks.append("".join(self.script))
            self.script = None


def find_recipe(node):
    if isinstance(node, dict):
        kind = node.get("@type", [])
        if kind == "Recipe" or isinstance(kind, list) and "Recipe" in kind:
            yield node
        for value in node.values():
            if isinstance(value, (dict, list)):
                yield from find_recipe(value)
    elif isinstance(node, list):
        for value in node:
            yield from find_recipe(value)


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def text(value, limit):
    if not isinstance(value, str):
        return ""
    parser = PlainText()
    parser.feed(value)
    return " ".join("".join(parser.parts).split())[:limit]


def recipe_draft(url):
    for _ in range(2):
        url, html = fetch_page(url)
        page = RecipeMarkup()
        page.feed(html)
        if urlsplit(url).hostname in PIN_HOSTS and page.source:
            url = page.source
            continue
        for block in page.blocks:
            try:
                recipes = list(find_recipe(json.loads(block)))
            except (ValueError, RecursionError):
                continue
            for recipe in recipes:
                entries = recipe.get("recipeIngredient")
                if not isinstance(entries, list):
                    continue
                ingredients = [line for entry in entries[:80] if (line := text(entry, 300))]
                name = text(recipe.get("name"), 150)
                if name and ingredients:
                    food_label = recipe.get("nutrition")
                    nutrition = {}
                    if isinstance(food_label, dict) and re.fullmatch(
                        r"1 (?:serving|portion)", text(food_label.get("servingSize"), 40), re.I
                    ):
                        for key, unit in {"proteinContent": "g", "fiberContent": "g"}.items():
                            amount = re.fullmatch(r"(\d+(?:\.\d+)?)\s*" + unit, text(food_label.get(key), 24))
                            if amount:
                                nutrition[key] = float(amount.group(1))
                    return {
                        "name": name, "ingredients": ingredients, "url": url, "nutrition": nutrition,
                        "servings": text(str(recipe.get("recipeYield") or ""), 80),
                        "time": text(recipe.get("totalTime"), 40),
                    }
        break
    raise ImportErrorForUser("No structured ingredient list was found. Try the original recipe page or add it by hand.")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Submitted URLs are never placed in request logs.
        return

    def reply(self, status, body=None):
        data = json.dumps(body).encode() if body is not None else b""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if self.headers.get("Origin") == SITE_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", SITE_ORIGIN)
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.reply(200, {"status": "ok"}) if self.path == "/health" else self.reply(404, {"error": "Not found."})

    def do_OPTIONS(self):
        self.reply(204 if self.path == "/import" and self.headers.get("Origin") == SITE_ORIGIN else 403)

    def do_POST(self):
        if self.path != "/import" or self.headers.get("Origin") != SITE_ORIGIN:
            self.reply(403, {"error": "Open Family Fuel to import a recipe."})
            return
        if not FETCH_SLOTS.acquire(blocking=False):
            self.reply(429, {"error": "The importer is busy. Try again in a moment."})
            return
        try:
            self.connection.settimeout(5)
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 4096:
                raise ImportErrorForUser("Enter one public recipe URL.")
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ImportErrorForUser("Enter one public recipe URL.")
            self.reply(200, recipe_draft(payload.get("url")))
        except ImportErrorForUser as error:
            self.reply(422, {"error": str(error)})
        except (ValueError, UnicodeError):
            self.reply(422, {"error": "Enter a valid public HTTPS link."})
        except (OSError, http.client.HTTPException):
            self.reply(422, {"error": "The recipe site could not be reached. Try the original recipe link."})
        finally:
            FETCH_SLOTS.release()


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "10000"))), Handler).serve_forever()
