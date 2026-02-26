import json
import os

# The Article class represent a single bibliography entry in the library.
class Article:
    def __init__(self, authors: list[str], title: str, venue: str, year: int, doi: str, keywords: list[str], pdf: str):
        self.Authors = authors
        self.Title = title
        self.Venue = venue
        self.Year = year
        self.DOI = doi
        self.Keywords = keywords
        self.PDF = pdf

# The Library class represents the full database object countaining all your entries plus additional data.
class Library:
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
                    pdf = article["pdf"]
            ))
        
        # set class attributes
        self.DatabasePath = databasePath
        self.ArticlesList = articlesList
