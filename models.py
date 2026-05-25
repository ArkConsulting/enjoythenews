from dataclasses import dataclass


@dataclass
class Article:
    title: str
    link: str
    source: str
    summary: str = ""
    published: str = ""
    author: str = ""
    category: str = ""
    score: float = 0.0
    positive: bool = False
