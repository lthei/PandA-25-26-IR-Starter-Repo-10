from __future__ import annotations
from typing import List, Dict, Any, Tuple


class Sonnet:
    def __init__(self, sonnet_data: Dict[str, Any]):
        self.title = sonnet_data["title"]
        self.lines = sonnet_data["lines"]

    @staticmethod
    def find_spans(text: str, pattern: str):
        """Return [(start, end), ...] for all (possibly overlapping) matches.
        Inputs should already be lowercased by the caller."""
        spans = []
        if not pattern:
            return spans

        for i in range(len(text) - len(pattern) + 1):
            if text[i:i + len(pattern)] == pattern:
                spans.append((i, i + len(pattern)))
        return spans

    def search_for(self: Sonnet, query: str) -> SearchResult:
        title_raw = str(self.title)
        lines_raw = self.lines

        q = query.lower()
        title_spans = self.find_spans(title_raw.lower(), q)

        line_matches = []
        for idx, line_raw in enumerate(lines_raw, start=1):  # 1-based line numbers
            spans = self.find_spans(line_raw.lower(), q)
            if spans:
                line_matches.append(LineMatch(idx, line_raw, spans))

        total = len(title_spans) + sum(len(lm.spans) for lm in line_matches)

        return SearchResult(title_raw, title_spans, line_matches, total)


class LineMatch:
    def __init__(self, line_no: int, text: str, spans: List[Tuple[int, int]]):
        self.line_no = line_no
        self.text = text
        self.spans = spans

    def copy(self):
        return LineMatch(self.line_no, self.text, self.spans)

class SearchResult:
    def __init__(self, title: str, title_spans: List[Tuple[int, int]], line_matches: List[LineMatch], matches: int) -> None:
        self.title = title
        self.title_spans = title_spans
        self.line_matches = line_matches
        self.matches = matches

    def copy(self):
        return SearchResult(self.title, self.title_spans, self.line_matches, self.matches)

    # ToDo 0 i (move and rename function)
    def combine_with(self, other: "SearchResult") -> "SearchResult":
        """Combine two search results."""

        combined = self.copy()  # shallow copy # instead of combined = result1.copy()

        combined.matches = self.matches + other.matches  # instead of: combined.matches = result1.matches + result2.matches
        combined.title_spans = sorted(
            self.title_spans + other.title_spans
        )

        # Merge line_matches by line number

        lines_by_no = {lm.line_no: lm.copy() for lm in self.line_matches}
        for lm in other.line_matches:
            ln = lm.line_no
            if ln in lines_by_no:
                # extend spans & keep original text
                lines_by_no[ln].spans.extend(lm.spans)
            else:
                lines_by_no[ln] = lm.copy()

        combined.line_matches = sorted(
            lines_by_no.values(), key=lambda lm: lm.line_no
        )

        return combined

    # ToDo 0 ii (add new highlight_mode)
    @staticmethod
    def ansi_highlight(text: str, spans, highlight_mode: str) -> str: # add parameter highlight_mode
        """Return text with ANSI highlight escape codes inserted."""
        if not spans:
            return text

        # add if/else statement to choose color setting
        if highlight_mode == "GREEN":
            start_code = "\033[1;92m"  # bold green text
        else:
            start_code = "\033[43m\033[30m"  # yellow background, black text

        spans = sorted(spans)
        merged = []

        # Merge overlapping spans
        current_start, current_end = spans[0]
        for s, e in spans[1:]:
            if s <= current_end:
                current_end = max(current_end, e)
            else:
                merged.append((current_start, current_end))
                current_start, current_end = s, e
        merged.append((current_start, current_end))

        # Build highlighted string
        out = []
        i = 0
        for s, e in merged:
            out.append(text[i:s])
            # ToDo 0 ii (adapt for new highlight_mode)
            out.append(start_code) # replace variable with start_code
            out.append(text[s:e])
            out.append("\033[0m")           # reset
            i = e
        out.append(text[i:])
        return "".join(out)

    def print(self, idx, highlight, total_docs, highlight_mode: str) -> None: # add parameter highlight_mode
        title_line = (
            # ToDo 0 iii (pass new highlight_mode)
            self.ansi_highlight(self.title, self.title_spans, highlight_mode) # add highlight_mode
            if highlight
            else self.title
        )
        print(f"\n[{idx}/{total_docs}] {title_line}")
        for lm in self.line_matches:
            line_out = (
                # ToDo 0 iii (pass new highlight_mode)
                self.ansi_highlight(lm.text, lm.spans, highlight_mode) # add highlight_mode
                if highlight
                else lm.text
            )
            print(f"  [{lm.line_no:2}] {line_out}")

# ToDo 2 (extract search behaviour into separate class)
# put into this module to keep all of the search logic together
class SearchEngine: # class name: represents search mechanism
    def __init__(self, sonnets: List[Sonnet]): # initialization with list of sonnets
        self.sonnets = sonnets

    def search(self, query: str, search_mode: str) -> List[SearchResult]: # pass query and search_mode, return list of search results
        words = query.split() # split query

        combined_results = []

        for word in words:
            results = [s.search_for(word) for s in self.sonnets] # dot notation

            if not combined_results:
                combined_results = results
            else:
                for i in range(len(combined_results)):
                    combined_result = combined_results[i]
                    result = results[i]

                    if search_mode == "AND": # remove dot notation
                        if combined_result.matches > 0 and result.matches > 0:
                            combined_results[i] = combined_result.combine_with(result)
                        else:
                            combined_result.matches = 0
                    elif search_mode == "OR": # remove dot notation
                        combined_results[i] = combined_result.combine_with(result)

        return combined_results

