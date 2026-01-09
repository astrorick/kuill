import json
import os

class Article:
    def __init__(self, authors: list[str], title: str, venue: str, year: int, doi: str, keywords: list[str], pdf: str):
        self.Authors = authors
        self.Title = title
        self.Venue = venue
        self.Year = year
        self.DOI = doi
        self.Keywords = keywords
        self.PDF = pdf

class Database:
    def __init__(self, owner: str, version: str, articlesList: list[Article]):
        self.Owner = owner
        self.Version = version
        self.ArticlesList = articlesList

def LoadJSON(dbPath: str) -> Database:
    # raise exception if file does not exists
    if not os.path.exists(dbPath):
        raise FileNotFoundError()
    
    # load database from JSON file
    with open(dbPath, "r", encoding = "utf-8") as db:
        dataPayload = json.load(db)
    
    articlesList = []
    for article in dataPayload["articles_list"]:
        articlesList.append(
            Article(
                authors = article["authors"],
                title = article["title"],
                venue = article["venue"],
                year = article["year"],
                doi = article["doi"],
                keywords = article["keywords"],
                pdf = article["pdf"]
            )
        )

    return Database(
        owner = dataPayload["database_owner"],
        version = dataPayload["database_version"],
        articlesList = articlesList
    )
