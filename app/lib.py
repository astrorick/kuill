import json
import os

class Article:
    """
    The Article class represent a single bibliography entry in the library.
    """

    Authors: list[str]
    Title: str
    Venue: str
    Year: int
    DOI: str
    Keywords: list[str]
    PDF: str

    def __init__(self, authors: list[str], title: str, venue: str, year: int, doi: str, keywords: list[str], pdf: str):
        self.Authors = authors
        self.Title = title
        self.Venue = venue
        self.Year = year
        self.DOI = doi
        self.Keywords = keywords
        self.PDF = pdf

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
        for article in libData["articles_list"]:
            articlesList.append(Article(
                authors = article["authors"],
                title = article["title"],
                venue = article["venue"],
                year = article["year"],
                doi = article["doi"],
                keywords = article["keywords"],
                pdf = article["pdf"]
            ))
        
        # set class attributes
        self.LibraryFilePath = libraryFilePath
        self.LibraryFolderPath = os.path.dirname(libraryFilePath)
        self.ArticlesList = articlesList
