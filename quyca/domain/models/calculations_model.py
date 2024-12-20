from pydantic import BaseModel, Field


class Node(BaseModel):
    degree: int = Field(default_factory=int)
    id: str = Field(default_factory=str)
    label: str = Field(default_factory=str)
    size: float = Field(default_factory=float)


class Edge(BaseModel):
    coauthorships: int = Field(default_factory=int)
    size: int | float = Field(default_factory=int)
    source: str = Field(default_factory=str)
    target: str = Field(default_factory=str)


class CoauthorshipNetwork(BaseModel):
    nodes: list[Node] | None = Field(default_factory=list)
    edges: list[Edge] | None = Field(default_factory=list)


class TopWord(BaseModel):
    name: str = Field(default_factory=str)
    value: int = Field(default_factory=int)


class Calculations(BaseModel):
    id: str = Field(default_factory=str, alias="_id")
    coauthorship_network: CoauthorshipNetwork = Field(default_factory=CoauthorshipNetwork)
    top_words: list[TopWord] = Field(default_factory=list)
