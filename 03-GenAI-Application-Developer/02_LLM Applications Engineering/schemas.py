from pydantic import BaseModel, Field
from typing import Literal

class ReviewAnalysis(BaseModel):
    sentiment: Literal['positive', 'negative', 'neutral']  

    category: str = Field(
        description = "Main topic of the customer review"
    )

    explanation: str = Field(
        description = "A brief explanation of the sentiment"
    )

    recommended_action: str = Field(
        description = "A practical action the business should consider"
        
    )