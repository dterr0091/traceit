from typing import List, Dict, Any, Optional, Union
import openai
from config import settings
from pydantic import BaseModel
import base64
from pathlib import Path
import asyncio
from services.video_processor import VideoProcessor

class SourceAnalysis(BaseModel):
    original_source: str
    viral_points: List[str]
    explanation: str
    confidence_score: float
    content_type: str  # "text", "image", or "video"
    extracted_text: Optional[str] = None
    visual_analysis: Optional[str] = None

class OpenAIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.vision_model = "gpt-4-vision-preview"
        self.video_processor = VideoProcessor()

    def _encode_image(self, image_path: Union[str, Path]) -> str:
        """Encode image to base64 for OpenAI Vision API."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    async def analyze_text(self, content: str, platform: str, metadata: Dict[str, Any]) -> SourceAnalysis:
        """Analyze text content using GPT-4."""
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
            parts = analysis_text.split("\n\n")
            
            return SourceAnalysis(
                original_source=parts[0].split(": ")[1],
                viral_points=[point.strip() for point in parts[1].split("\n")[1:4]],
                explanation=parts[2],
                confidence_score=float(parts[3].split(": ")[1]),
                content_type="text",
                extracted_text=content
            )
            
        except Exception as e:
            print(f"Error in text analysis: {str(e)}")
            return self._create_default_analysis("text")

    async def analyze_image(self, image_path: Union[str, Path], platform: str, metadata: Dict[str, Any]) -> SourceAnalysis:
        """Analyze image content using GPT-4 Vision."""
        try:
            base64_image = self._encode_image(image_path)
            
            response = await openai.ChatCompletion.acreate(
                model=self.vision_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in analyzing images for content source and viral spread tracking."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""
                                Analyze this image to determine its original source and viral spread:
                                
                                Platform: {platform}
                                Metadata: {metadata}
                                
                                Please provide:
                                1. The most likely original source
                                2. Top 3 viral points where the content spread
                                3. A detailed explanation of your analysis
                                4. A confidence score (0-1) for your assessment
                                5. Any text content visible in the image
                                """
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content
            parts = analysis_text.split("\n\n")
            
            return SourceAnalysis(
                original_source=parts[0].split(": ")[1],
                viral_points=[point.strip() for point in parts[1].split("\n")[1:4]],
                explanation=parts[2],
                confidence_score=float(parts[3].split(": ")[1]),
                content_type="image",
                extracted_text=parts[4].split(": ")[1] if len(parts) > 4 else None,
                visual_analysis=analysis_text
            )
            
        except Exception as e:
            print(f"Error in image analysis: {str(e)}")
            return self._create_default_analysis("image")

    async def analyze_video(self, video_path: Union[str, Path], platform: str, metadata: Dict[str, Any]) -> SourceAnalysis:
        """Analyze video content by extracting key frames and using GPT-4 Vision."""
        try:
            # Extract key frames from video
            frames = await self.video_processor.extract_key_frames(video_path)
            
            # Analyze each frame
            frame_analyses = []
            for frame_path in frames:
                frame_analysis = await self.analyze_image(frame_path, platform, metadata)
                frame_analyses.append(frame_analysis)
            
            # Combine analyses
            combined_analysis = self._combine_frame_analyses(frame_analyses)
            
            return SourceAnalysis(
                original_source=combined_analysis["original_source"],
                viral_points=combined_analysis["viral_points"],
                explanation=combined_analysis["explanation"],
                confidence_score=combined_analysis["confidence_score"],
                content_type="video",
                extracted_text=combined_analysis["extracted_text"],
                visual_analysis=combined_analysis["visual_analysis"]
            )
            
        except Exception as e:
            print(f"Error in video analysis: {str(e)}")
            return self._create_default_analysis("video")

    def _combine_frame_analyses(self, frame_analyses: List[SourceAnalysis]) -> Dict[str, Any]:
        """Combine analyses from multiple video frames into a single coherent analysis."""
        # This is a simplified combination - you might want to make it more sophisticated
        return {
            "original_source": frame_analyses[0].original_source,
            "viral_points": frame_analyses[0].viral_points,
            "explanation": "\n".join([f"Frame {i+1}: {analysis.explanation}" for i, analysis in enumerate(frame_analyses)]),
            "confidence_score": sum(analysis.confidence_score for analysis in frame_analyses) / len(frame_analyses),
            "extracted_text": "\n".join(filter(None, [analysis.extracted_text for analysis in frame_analyses])),
            "visual_analysis": "\n".join(filter(None, [analysis.visual_analysis for analysis in frame_analyses]))
        }

    def _create_default_analysis(self, content_type: str) -> SourceAnalysis:
        """Create a default analysis when an error occurs."""
        return SourceAnalysis(
            original_source="Unknown",
            viral_points=[],
            explanation=f"Analysis failed for {content_type} content",
            confidence_score=0.0,
            content_type=content_type
        )

    async def analyze_source(self, content: Union[str, Path], platform: str, metadata: Dict[str, Any]) -> SourceAnalysis:
        """
        Analyze content to determine its origin and viral spread.
        Automatically detects content type and uses appropriate analysis method.
        
        Args:
            content: The content to analyze (text, image path, or video path)
            platform: The platform where the content was found
            metadata: Additional metadata about the content
            
        Returns:
            SourceAnalysis object containing the analysis results
        """
        if isinstance(content, str) and not Path(content).exists():
            # Text content
            return await self.analyze_text(content, platform, metadata)
        else:
            # File content
            content_path = Path(content)
            if not content_path.exists():
                raise ValueError(f"Content file not found: {content}")
                
            if content_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                return await self.analyze_image(content_path, platform, metadata)
            elif content_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
                return await self.analyze_video(content_path, platform, metadata)
            else:
                raise ValueError(f"Unsupported content type: {content_path.suffix}")

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