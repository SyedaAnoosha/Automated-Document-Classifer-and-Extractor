from typing import List, Literal
from pydantic import BaseModel, Field

class Entity(BaseModel):
    type: str = Field(..., description="Entity type, e.g., PERSON, ORG, DATE")
    text: str = Field(..., description="Surface text of the entity")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence 0-1")

class DocumentAnalysis(BaseModel):
    document_type: str = Field(..., description="Document type, e.g., invoice, legal_contract")
    sentiment: Literal["positive", "neutral", "negative"] = Field(..., description="Sentiment label")
    entities: List[Entity] = Field(..., description="List of up to 5 entities")
    summary: str = Field(..., description="~3 sentence summary of the document")
