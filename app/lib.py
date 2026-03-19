import json
import os
import re
from dataclasses import dataclass


@dataclass
class Article:
    """
    The :class:`Article` class represent a single bibliography entry in the library.
    """

    id: int
    authors: list[str]
    title: str
    venue: str
    year: int
    doi: str
    keywords: list[str]
    added: str
    pdf: str
    notes: str

class Library:
    """
    The :class:`Library` class represents the full database object countaining all your entries, plus additional data.
    """
    
    library_file_path: str # path to library file
    articles_list: list[Article] # list of articles in library

    def __init__(self, library_file_path: str):
        # verify that the provided library file exists
        if not os.path.exists(library_file_path):
            raise FileNotFoundError(f"File not found '{library_file_path}'.")

        # load data from library file
        with open(library_file_path, "r", encoding = "utf-8") as lib_file:
            lib_data = json.load(lib_file)

        # ensure articles list key exists and is of correct type
        if "articles_list" not in lib_data or not isinstance(lib_data["articles_list"], list):
            raise ValueError(f"Library file '{library_file_path}' is missing a valid 'articles_list' field of type 'list'.")

        # populate articles list with data
        articles_list = []
        for id, article in enumerate(lib_data["articles_list"]):
            articles_list.append(
                Article(
                    id = id,
                    authors = article["authors"],
                    title = article["title"],
                    venue = article["venue"],
                    year = article["year"],
                    doi = article["doi"],
                    keywords = article["keywords"],
                    added = article["added"],
                    pdf = article["pdf"],
                    notes = article["notes"],
                )
            )
        
        # set class attributes
        self.library_file_path = library_file_path
        self.articles_list = articles_list

    def filtered_articles_list(self, query: str, use_regex: bool = False) -> tuple[bool, list[Article]]:
        """
        Filter articles by matching the provided query against selected fields.

        The fields examined are ``authors`` (each author name), ``title``, ``venue``, ``year`` and ``keywords`` (each keyword evaluated separately).
        The pattern can appear anywhere in a field and matching is case-insensitive.

        When ``use_regex`` is ``False`` (default), the query is split on whitespace and each token is matched literally.
        All tokens must match at least one field for the article to be included (AND logic).

        When ``use_regex`` is ``True``, the query is treated as a regular expression.

        Returns a tuple ``(valid, results)`` where ``valid`` is ``True`` if the query is valid
        and ``results`` is the list of matching :class:`Article` instances, or an empty list if the query is invalid.
        """

        # helper function that returns true if a pattern matches any of the article fields
        def matches_pattern(article: Article, pattern: re.Pattern) -> bool:
            for author in article.authors:
                if pattern.search(author):
                    return True

            if pattern.search(article.title):
                return True

            if pattern.search(article.venue):
                return True

            if pattern.search(str(article.year)):
                return True

            for keyword in article.keywords:
                if pattern.search(keyword):
                    return True

            return False

        if use_regex:
            # regex mode: compile as-is
            try:
                pattern = re.compile(query, re.IGNORECASE)
            except re.error:
                return (False, [])

            return (True, [a for a in self.articles_list if matches_pattern(a, pattern)])
        else:
            # plain text mode: split on whitespace, escape each token, require all to match (AND logic)
            tokens = query.split()
            patterns = [re.compile(re.escape(token), re.IGNORECASE) for token in tokens]

            def matches_all(article: Article) -> bool:
                return all(matches_pattern(article, p) for p in patterns)

            return (True, [a for a in self.articles_list if matches_all(a)])
