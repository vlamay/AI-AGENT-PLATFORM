"""
Digital Human Service

Provides AI-powered digital avatars with:
- Realistic facial animations
- Voice synthesis
- Lip sync
- Gesture control
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
import json
import logging
from typing import Optional
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Digital Human Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ElevenLabsVoice:
    """ElevenLabs voice synthesis integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
    
    async def text_to_speech(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Default voice
        model_id: str = "eleven_multilingual_v2"
    ) -> bytes:
        """Convert text to speech audio"""
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/text-to-speech/{voice_id}",
                    headers={
                        "xi-api-key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "model_id": model_id,
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.content
                else:
                    logger.error(f"ElevenLabs error: {response.status_code}")
                    return b""
                    
            except Exception as e:
                logger.error(f"TTS error: {str(e)}")
                return b""


class HeyGenAvatar:
    """HeyGen digital human avatar integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.heygen.com/v1"
    
    async def generate_avatar_video(
        self,
        text: str,
        avatar_id: str = "default",
        voice_id: str = "default"
    ) -> Optional[str]:
        """Generate avatar video with speech"""
        
        async with httpx.AsyncClient() as client:
            try:
                # Create video generation task
                response = await client.post(
                    f"{self.base_url}/video.generate",
                    headers={
                        "X-Api-Key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "video_inputs": [{
                            "character": {
                                "type": "avatar",
                                "avatar_id": avatar_id
                            },
                            "voice": {
                                "type": "text",
                                "voice_id": voice_id,
                                "input_text": text
                            }
                        }]
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    video_id = result.get("data", {}).get("video_id")
                    
                    # Poll for completion
                    video_url = await self._wait_for_video(video_id)
                    return video_url
                else:
                    logger.error(f"HeyGen error: {response.status_code}")
                    return None
                    
            except Exception as e:
                logger.error(f"Avatar generation error: {str(e)}")
                return None
    
    async def _wait_for_video(self, video_id: str, max_wait: int = 300) -> Optional[str]:
        """Wait for video generation to complete"""
        
        async with httpx.AsyncClient() as client:
            for _ in range(max_wait // 5):  # Check every 5 seconds
                try:
                    response = await client.get(
                        f"{self.base_url}/video_status.get",
                        headers={"X-Api-Key": self.api_key},
                        params={"video_id": video_id}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        status = result.get("data", {}).get("status")
                        
                        if status == "completed":
                            return result.get("data", {}).get("video_url")
                        elif status == "failed":
                            logger.error("Video generation failed")
                            return None
                    
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    logger.error(f"Status check error: {str(e)}")
                    return None
            
            return None


class DigitalHumanManager:
    """Manages digital human interactions"""
    
    def __init__(self, orchestrator_url: str):
        self.orchestrator_url = orchestrator_url
        self.voice_engine = None
        self.avatar_engine = None
    
    def initialize(self, elevenlabs_key: Optional[str], heygen_key: Optional[str]):
        """Initialize voice and avatar engines"""
        if elevenlabs_key:
            self.voice_engine = ElevenLabsVoice(elevenlabs_key)
        if heygen_key:
            self.avatar_engine = HeyGenAvatar(heygen_key)
    
    async def process_message(
        self,
        text: str,
        agent_id: str,
        output_format: str = "audio"  # audio, video, or text
    ) -> dict:
        """
        Process message and generate digital human response
        
        Args:
            text: User's input message
            agent_id: The AI agent to use
            output_format: Desired output (audio, video, text)
        
        Returns:
            Dict with response data
        """
        
        # Get AI response from orchestrator
        ai_response = await self._get_ai_response(text, agent_id)
        
        if not ai_response:
            return {"error": "Failed to get AI response"}
        
        response_data = {
            "text": ai_response,
            "format": output_format
        }
        
        # Generate audio
        if output_format in ["audio", "video"] and self.voice_engine:
            audio_data = await self.voice_engine.text_to_speech(ai_response)
            if audio_data:
                response_data["audio"] = base64.b64encode(audio_data).decode('utf-8')
        
        # Generate video (with avatar)
        if output_format == "video" and self.avatar_engine:
            video_url = await self.avatar_engine.generate_avatar_video(ai_response)
            if video_url:
                response_data["video_url"] = video_url
        
        return response_data
    
    async def _get_ai_response(self, message: str, agent_id: str) -> Optional[str]:
        """Get response from AI orchestrator"""
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.orchestrator_url}/api/v1/agents/{agent_id}/chat",
                    json={"message": message},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    logger.error(f"Orchestrator error: {response.status_code}")
                    return None
                    
            except Exception as e:
                logger.error(f"AI response error: {str(e)}")
                return None


# Initialize manager
import os
digital_human = DigitalHumanManager(
    orchestrator_url=os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8080")
)

digital_human.initialize(
    elevenlabs_key=os.getenv("ELEVENLABS_API_KEY"),
    heygen_key=os.getenv("HEYGEN_API_KEY")
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "voice_engine": digital_human.voice_engine is not None,
        "avatar_engine": digital_human.avatar_engine is not None
    }


@app.post("/api/v1/digital-human/generate")
async def generate_response(
    agent_id: str,
    message: str,
    output_format: str = "audio"
):
    """
    Generate digital human response
    
    Args:
        agent_id: Agent ID to use
        message: User message
        output_format: audio, video, or text
    """
    
    result = await digital_human.process_message(
        text=message,
        agent_id=agent_id,
        output_format=output_format
    )
    
    return result


@app.websocket("/ws/digital-human/{agent_id}")
async def websocket_digital_human(websocket: WebSocket, agent_id: str):
    """
    WebSocket endpoint for real-time digital human interaction
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")
            output_format = data.get("format", "audio")
            
            # Process and generate response
            response = await digital_human.process_message(
                text=message,
                agent_id=agent_id,
                output_format=output_format
            )
            
            # Send back to client
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for agent {agent_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({"error": str(e)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
