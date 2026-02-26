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
    PDFPath: str

    def __init__(self, authors: list[str], title: str, venue: str, year: int, doi: str, keywords: list[str], pdfPath: str):
        self.Authors = authors
        self.Title = title
        self.Venue = venue
        self.Year = year
        self.DOI = doi
        self.Keywords = keywords
        self.PDFPath = pdfPath

class Library:
    """
    The Library class represents the full database object countaining all your entries plus additional data.
    """
    
    DatabasePath: str
    ArticlesList: list[Article]

    def __init__(self, databasePath: str):
        # raise exception if file does not exists
        if not os.path.exists(databasePath):
            raise FileNotFoundError()
    
        # load database from provided file
        with open(databasePath, "r", encoding = "utf-8") as db:
            dataPayload = json.load(db)

        # populate articles list
        articlesList = []
        for article in dataPayload["articles_list"]:
            articlesList.append(Article(
                    authors = article["authors"],
                    title = article["title"],
                    venue = article["venue"],
                    year = article["year"],
                    doi = article["doi"],
                    keywords = article["keywords"],
                    pdfPath = article["pdf"]
            ))
        
        # set class attributes
        self.DatabasePath = databasePath
        self.ArticlesList = articlesList
