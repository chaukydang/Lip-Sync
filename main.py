from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import base64
import json
import tempfile
import os
import uuid
import asyncio

app = FastAPI()

# Serve static files for video URLs
os.makedirs("static/videos", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


class LipSyncAPI:
    def __init__(self):
        print("Initializing Lip Sync API...")
        # Simulate model loading
        self.model_loaded = True

    async def generate_video(self, audio_base64: str, image_base64: str, output_format="base64"):
        """
        Generate lip-synced video from audio bytes and person image

        Args:
            audio_base64: base64-encoded audio bytes
            image_base64: base64-encoded person image
            output_format: "base64" or "url"

        Returns:
            dict with video in base64 or URL format
        """
        try:
            # Decode input data
            audio_bytes = base64.b64decode(audio_base64)
            image_bytes = base64.b64decode(image_base64)

            # Save temp files
            audio_path = f"/tmp/audio_{uuid.uuid4().hex}.wav"
            image_path = f"/tmp/image_{uuid.uuid4().hex}.jpg"

            with open(audio_path, 'wb') as f:
                f.write(audio_bytes)
            with open(image_path, 'wb') as f:
                f.write(image_bytes)

            # TODO: Replace with actual MuseTalk inference
            # For now, create a simple demo video
            output_video_path = await self.create_demo_video(audio_path, image_path)

            # Return based on requested format
            if output_format == "url":
                # Move to static folder and return URL
                video_filename = f"output_{uuid.uuid4().hex}.mp4"
                static_path = f"static/videos/{video_filename}"

                os.rename(output_video_path, static_path)
                video_url = f"/static/videos/{video_filename}"

                result = {"video_url": video_url}
            else:
                # Return as base64
                with open(output_video_path, 'rb') as f:
                    video_bytes = f.read()
                    video_base64 = base64.b64encode(video_bytes).decode('utf-8')

                result = {"video_base64": video_base64}
                os.unlink(output_video_path)

            # Cleanup temp files
            os.unlink(audio_path)
            os.unlink(image_path)

            return result

        except Exception as e:
            raise Exception(f"Video generation failed: {str(e)}")

    async def create_demo_video(self, audio_path, image_path):
        """
        Create demo video - Replace this with actual MuseTalk inference
        """
        output_path = f"/tmp/output_{uuid.uuid4().hex}.mp4"

        try:
            # Use ffmpeg to create video from image + audio
            import subprocess

            cmd = [
                'ffmpeg', '-y',
                '-loop', '1', '-i', image_path,  # Loop image
                '-i', audio_path,  # Audio input
                '-c:v', 'libx264',  # Video codec
                '-c:a', 'aac',  # Audio codec
                '-shortest',  # Stop when audio ends
                '-pix_fmt', 'yuv420p',  # Pixel format
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise Exception(f"FFmpeg failed: {result.stderr}")

            return output_path

        except FileNotFoundError:
            # FFmpeg not available, create dummy video
            return await self.create_dummy_video(image_path, audio_path)

    async def create_dummy_video(self, image_path, audio_path):
        """
        Fallback: Create simple video with static image
        """
        import cv2

        output_path = f"/tmp/dummy_{uuid.uuid4().hex}.mp4"

        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise Exception("Cannot read image")

        height, width = img.shape[:2]

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 25
        duration = 3  # 3 seconds

        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Write frames (static image)
        for _ in range(fps * duration):
            out.write(img)

        out.release()
        return output_path


# Initialize processor
processor = LipSyncAPI()


@app.websocket("/ws/lip-sync")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Validate required fields
            if 'audio' not in message or 'image' not in message:
                await websocket.send_text(json.dumps({
                    "status": "error",
                    "message": "Missing required fields: 'audio' and 'image'"
                }))
                continue

            # Get output format preference (default: base64)
            output_format = message.get('output_format', 'base64')

            try:
                # Generate lip-synced video
                result = await processor.generate_video(
                    audio_base64=message['audio'],
                    image_base64=message['image'],
                    output_format=output_format
                )

                # Send successful response
                response = {
                    "status": "success",
                    **result  # video_base64 or video_url
                }

                await websocket.send_text(json.dumps(response))

            except Exception as e:
                # Send error response
                await websocket.send_text(json.dumps({
                    "status": "error",
                    "message": str(e)
                }))

    except WebSocketDisconnect:
        print("WebSocket client disconnected")


@app.get("/")
async def root():
    return {
        "message": "Lip Sync WebSocket API",
        "version": "1.0",
        "endpoints": {
            "websocket": "/ws/lip-sync",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": processor.model_loaded
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")