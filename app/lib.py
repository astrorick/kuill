import json
import os
import re

class Article:
    """
    The Article class represent a single bibliography entry in the library.
    """

    ID: int
    Authors: list[str]
    Title: str
    Venue: str
    Year: int
    DOI: str
    Keywords: list[str]
    Added: str
    PDF: str
    Notes: str

    def __init__(self, id: int, authors: list[str], title: str, venue: str, year: int, doi: str, keywords: list[str], added: str, pdf: str, notes: str):
        self.ID = id
        self.Authors = authors
        self.Title = title
        self.Venue = venue
        self.Year = year
        self.DOI = doi
        self.Keywords = keywords
        self.Added = added
        self.PDF = pdf
        self.Notes = notes

class Library:
    """
    The Library class represents the full database object countaining all your entries plus additional data.
    """
    
    LibraryFilePath: str # path to library file
    LibraryFolderPath: str # path to library folder
    ArticlesList: list[Article] # list of articles in library

    def __init__(self, libraryFilePath: str):
        # verify the library file exists
        if not os.path.exists(libraryFilePath):
            raise FileNotFoundError(f"File not found '{libraryFilePath}'")

        # load data from library file
        with open(libraryFilePath, "r", encoding = "utf-8") as libFile:
            libData = json.load(libFile)

        # ensure articles list key exists and is correct type
        if "articles_list" not in libData or not isinstance(libData["articles_list"], list):
            raise ValueError(f"Invalid library file '{libraryFilePath}'")
        
        # TODO: add checks for each article entry structure

        # populate articles list with data
        articlesList = []
        for id, article in enumerate(libData["articles_list"]):
            articlesList.append(Article(
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
            ))
        
        # set class attributes
        self.LibraryFilePath = libraryFilePath
        self.LibraryFolderPath = os.path.dirname(libraryFilePath)
        self.ArticlesList = articlesList

    def FilteredArticlesList(self, pattern: re.Pattern) -> list[Article]:
        """
        Return a list of :class:`Article` instances where at least one of the selected fields matches the provided pattern.

        The fields examined are ``authors`` (each author name), ``title``, ``venue``, ``year`` and ``keywords`` (each keyword evaluated separately).
        
        The pattern can appear anywhere in the fields and matching is case-insensitive.
        """

        # helper function that returns true if article contains a match in any of the fields
        def matches(article: Article) -> bool:
            for author in article.Authors:
                if pattern.search(author):
                    return True

            if pattern.search(article.Title):
                return True

            if pattern.search(article.Venue):
                return True

            if pattern.search(str(article.Year)):
                return True

            for keyword in article.Keywords:
                if pattern.search(keyword):
                    return True

            return False

        # build and return filtered list
        return [a for a in self.ArticlesList if matches(a)]
