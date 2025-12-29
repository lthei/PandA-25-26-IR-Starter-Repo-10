#!/usr/bin/env python3
"""
Part 10 starter.

WHAT'S NEW IN PART 10
You will write two classes without detailed instructions! This is a refactoring, we are not adding new functionality 🙄.
"""

# ToDo 0 (adapting imports)
from typing import List
import time

from .constants import BANNER, HELP
from .models import SearchResult, SearchEngine # import new class SearchEngine
from .file_utilities import load_config, load_sonnets


# ToDo 0 ii (pass highlight_mode)
def print_results(
    query: str,
    results: List[SearchResult],
    highlight: bool,
    highlight_mode: str, # add highlight_mode
    query_time_ms: float | None = None,
) -> None:
    total_docs = len(results)
    matched = [r for r in results if r.matches > 0]

    line = f'{len(matched)} out of {total_docs} sonnets contain "{query}".'
    if query_time_ms is not None:
        line += f" Your query took {query_time_ms:.2f}ms."
    print(line)

    for idx, r in enumerate(matched, start=1):
        r.print(idx, highlight, total_docs, highlight_mode) # add highlight_mode


# ---------- CLI loop ----------

def main() -> None:
    print(BANNER)
    config = load_config()

    # Load sonnets (from cache or API)
    start = time.perf_counter()
    sonnets = load_sonnets()

    elapsed = (time.perf_counter() - start) * 1000
    print(f"Loading sonnets took: {elapsed:.3f} [ms]")

    print(f"Loaded {len(sonnets)} sonnets.")

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not raw:
            continue

        # commands
        if raw.startswith(":"):
            if raw == ":quit":
                print("Bye.")
                break

            if raw == ":help":
                print(HELP)
                continue

            # ToDo 2: You realize that the three settings 'highlight', 'search-mode', and 'hl-mode' have a lot
            #  in common. Wrap the common behavior in a class and use this class three times.

            if raw.startswith(":highlight"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].lower() in ("on", "off"):
                    config.highlight = parts[1].lower() == "on"
                    print("Highlighting", "ON" if config.highlight else "OFF")
                    # ToDo 0 iii (adapt call)
                    config.save()
                else:
                    print("Usage: :highlight on|off")
                continue

            if raw.startswith(":search-mode"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].upper() in ("AND", "OR"):
                    config.search_mode = parts[1].upper()
                    print("Search mode set to", config.search_mode)
                    # ToDo 0 iii (adapt call)
                    config.save()
                else:
                    print("Usage: :search-mode AND|OR")
                continue

            # ToDo 0 iii (add new highlight_mode)
            if raw.startswith(":hl-mode"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].upper() in ("DEFAULT", "GREEN"):
                    config.highlight_mode = parts[1].upper()
                    print("Highlight mode set to", config.highlight_mode)
                    config.save()
                else:
                    print("Usage: :hl-mode DEFAULT|GREEN")
                continue

            print("Unknown command. Type :help for commands.")
            continue

        # ---------- Query evaluation ----------
        words = raw.split()
        if not words:
            continue

        start = time.perf_counter()

        # ToDo 1: Extract the search - basically everything until the end of the time measurement in a new class.
        # search logic extracted and moved to models.py
        combined_results = SearchEngine(sonnets).search(raw, config.search_mode) # use the new class method to get combined_results

        elapsed_ms = (time.perf_counter() - start) * 1000

        # ToDo 0 iii (pass highlight_mode)
        print_results(raw, combined_results, config.highlight, config.highlight_mode, elapsed_ms) # add highlight_mode

if __name__ == "__main__":
    main()
