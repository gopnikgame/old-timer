import base64
import time
import uuid
import httpx
import logging

from app.config import Config

logger = logging.getLogger(__name__)

class GigaChatAPI:
    def __init__(self):
        self.client_id = Config.GIGACHAT_CLIENT_ID
        self.client_secret = Config.GIGACHAT_CLIENT_SECRET
        self.base_url = Config.GIGACHAT_BASE_URL
        self.auth_url = Config.GIGACHAT_AUTH_URL
        self.scope = Config.GIGACHAT_SCOPE
        self.token = None
        self.token_expires_at = 0
        
    async def _get_auth_token(self):
        """Получение токена авторизации для GigaChat API"""
        if self.token and time.time() < self.token_expires_at - 60:  # Обновляем токен за минуту до истечения
            return self.token
            
        try:
            # Кодирование client_id и client_secret в формате Base64
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_base64 = base64.b64encode(auth_bytes)
            auth_header = auth_base64.decode('ascii')
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": str(uuid.uuid4()),  # Генерируем уникальный ID запроса
                "Authorization": f"Basic {auth_header}"
            }
            
            data = {"scope": self.scope}
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.auth_url,
                    headers=headers,
                    data=data
                )
                
            if response.status_code != 200:
                logger.error(f"GigaChat Auth error: {response.status_code} - {response.text}")
                raise ConnectionError(f"Ошибка авторизации GigaChat API: {response.status_code}")
                
            result = response.json()
            self.token = result["access_token"]
            self.token_expires_at = result["expires_at"]
            
            return self.token
            
        except httpx.RequestError as e:
            logger.error(f"GigaChat Auth connection error: {e}")
            raise ConnectionError("Ошибка подключения к API авторизации") from e
        except Exception as e:
            logger.exception(f"GigaChat Auth error: {e}")
            raise
            
    async def generate_prediction(self, prompt: str) -> str:
        """Генерирует предсказание с помощью GigaChat API"""
        token = await self._get_auth_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "GigaChat",
            "messages": [{
                "role": "user",
                "content": f"Придумай креативное предсказание для чата на тему: {prompt}. "
                          "Используй эмодзи и сделай текст живым. Не используй markdown."
            }],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                
            if response.status_code != 200:
                logger.error(f"GigaChat API error: {response.status_code} - {response.text}")
                raise ConnectionError(f"Ошибка подключения к API: {response.status_code}")
                
            return response.json()["choices"][0]["message"]["content"]
            
        except httpx.RequestError as e:
            logger.error(f"GigaChat API connection error: {e}")
            raise ConnectionError("Ошибка подключения к API") from e
        except Exception as e:
            logger.exception(f"GigaChat API error: {e}")
            raise
