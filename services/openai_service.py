from typing import List, Dict, Any
import openai
from config import settings
from pydantic import BaseModel

class SourceAnalysis(BaseModel):
    original_source: str
    viral_points: List[str]
    explanation: str
    confidence_score: float

class OpenAIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL

    async def analyze_source(self, content: str, platform: str, metadata: Dict[str, Any]) -> SourceAnalysis:
        """
        Analyze a content source to determine its origin and viral spread.
        
        Args:
            content: The content text to analyze
            platform: The platform where the content was found
            metadata: Additional metadata about the content
            
        Returns:
            SourceAnalysis object containing the analysis results
        """
        prompt = f"""
        Analyze the following content to determine its original source and viral spread:
        
        Content: {content}
        Platform: {platform}
        Metadata: {metadata}
        
        Please provide:
        1. The most likely original source
        2. Top 3 viral points where the content spread
        3. A detailed explanation of your analysis
        4. A confidence score (0-1) for your assessment
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in content source analysis and viral spread tracking."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the response into structured data
            # This is a simplified parsing - you might want to make it more robust
            parts = analysis_text.split("\n\n")
            original_source = parts[0].split(": ")[1]
            viral_points = [point.strip() for point in parts[1].split("\n")[1:4]]
            explanation = parts[2]
            confidence_score = float(parts[3].split(": ")[1])
            
            return SourceAnalysis(
                original_source=original_source,
                viral_points=viral_points,
                explanation=explanation,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            # Log the error and return a default analysis
            print(f"Error in OpenAI analysis: {str(e)}")
            return SourceAnalysis(
                original_source="Unknown",
                viral_points=[],
                explanation="Analysis failed due to an error",
                confidence_score=0.0
            )

    async def evaluate_source_credibility(self, source_url: str, content: str) -> Dict[str, Any]:
        """
        Evaluate the credibility of a source using OpenAI.
        
        Args:
            source_url: The URL of the source
            content: The content to evaluate
            
        Returns:
            Dictionary containing credibility metrics
        """
        prompt = f"""
        Evaluate the credibility of this source:
        
        URL: {source_url}
        Content: {content}
        
        Please provide:
        1. Credibility score (0-1)
        2. Key factors affecting credibility
        3. Potential biases or concerns
        4. Recommendations for verification
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in source credibility evaluation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse the response into structured data
            analysis = response.choices[0].message.content
            parts = analysis.split("\n\n")
            
            return {
                "credibility_score": float(parts[0].split(": ")[1]),
                "key_factors": [factor.strip() for factor in parts[1].split("\n")[1:]],
                "biases": [bias.strip() for bias in parts[2].split("\n")[1:]],
                "verification_recommendations": [rec.strip() for rec in parts[3].split("\n")[1:]]
            }
            
        except Exception as e:
            print(f"Error in credibility evaluation: {str(e)}")
            return {
                "credibility_score": 0.0,
                "key_factors": [],
                "biases": [],
                "verification_recommendations": []
            } 