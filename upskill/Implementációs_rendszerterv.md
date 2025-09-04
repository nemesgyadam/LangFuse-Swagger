# Implementációs Rendszerterv - LangFuse-Swagger API

## 1. Áttekintés

A LangFuse-Swagger egy FastAPI alapú univerzális szerver, amely automatikusan generál API végpontokat Swagger UI-val bármely LangFuse projektből. A rendszer dinamikusan hoz létre végpontokat a LangFuse projektben található promptok alapján.

## 2. Architektúra

### 2.1 Rendszerarchitektúra

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Swagger UI    │    │   External APIs │
│                 │    │                 │    │   (OpenAI, etc) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   FastAPI App   │
                    │   (main.py)     │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │PromptEndpoint   │
                    │   Generator     │
                    │(app_generator.py)│
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ PromptHandler   │    │   API Models    │    │ LangFuse Utils  │
│(prompt_handler  │    │(api_models.py)  │    │(langfuse_utils  │
│     .py)        │    │                 │    │     .py)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
┌─────────────────┐
│  LLM Factory    │
│(llm_factory.py) │
└─────────────────┘
         │
┌─────────────────┐
│   LangFuse      │
│   Platform      │
└─────────────────┘
```

### 2.2 Komponens Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│ │ Authentication  │  │   Logging       │  │   CORS       │ │
│ │   Middleware    │  │   Middleware    │  │  Middleware  │ │
│ └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│ │ Request Models  │  │Response Models  │  │   Endpoint   │ │
│ │   (Pydantic)    │  │   (Pydantic)    │  │  Handlers    │ │
│ └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│ │ PromptHandler   │  │   LLM Factory   │  │   Tracing    │ │
│ │    Service      │  │    Service      │  │   Service    │ │
│ └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────┐                   │
│ │   LangFuse      │  │   LangChain     │                   │
│ │    Client       │  │   Integration   │                   │
│ └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## 3. Implementációs Részletek

### 3.1 Fő Komponensek

#### 3.1.1 PromptEndpointGenerator (app_generator.py)

**Felelősség:**
- FastAPI alkalmazás inicializálása
- LangFuse kliens beállítása
- Dinamikus végpontok generálása
- Logging konfiguráció

**Implementációs részletek:**
```python
class PromptEndpointGenerator:
    def __init__(self):
        # Logging inicializálás
        # LangFuse kliens inicializálás
        # FastAPI app létrehozás
        # Prompt konfigurációk betöltése
        # Végpontok generálása
```

**Kulcs metódusok:**
- `_generate_endpoints()`: Végpontok dinamikus generálása
- `_generate_endpoint_handler()`: Egyedi végpont handler létrehozása
- `get_app()`: FastAPI alkalmazás visszaadása

#### 3.1.2 PromptHandler (prompt_handler.py)

**Felelősség:**
- Prompt végrehajtás kezelése
- LangChain integráció
- Tracing és logging
- Hibakezelés

**Implementációs részletek:**
```python
class PromptHandler:
    def __init__(self, langfuse_client, prompt_config, logger):
        # Inicializálás
    
    async def handle_prompt(self, prompt_name, input_data, variables):
        # Prompt végrehajtás és tracing
    
    def _create_chain(self, prompt_name, is_chat):
        # LangChain chain létrehozása
```

#### 3.1.3 API Models (api_models.py)

**Felelősség:**
- Dinamikus Pydantic modellek létrehozása
- Request/Response validáció
- Swagger dokumentáció generálás

**Implementációs részletek:**
```python
class RequestModelGenerator:
    @staticmethod
    def create_request_model(prompt_name, variables):
        # Dinamikus request model létrehozása
        
class ResponseModelGenerator:
    @staticmethod
    def create_response_model(prompt_name, output_structure):
        # Dinamikus response model létrehozása
```

### 3.2 Adatfolyam

#### 3.2.1 Alkalmazás Indítás

1. **Logging Setup** (`setup_logging()`)
   - File és console handler beállítása
   - Log level konfigurálás környezeti változóból
   - Rotating file handler (10MB, 5 backup)

2. **LangFuse Inicializálás**
   - API kulcsok betöltése környezeti változókból
   - LangFuse kliens létrehozása
   - Projekt név lekérése

3. **Prompt Konfigurációk Betöltése**
   - Tag alapú szűrés
   - Prompt változók kinyerése
   - Metaadatok gyűjtése

4. **Végpontok Generálása**
   - Aszinkron leírás generálás
   - Dinamikus endpoint regisztráció
   - Swagger dokumentáció frissítése

#### 3.2.2 Request Feldolgozás

```
Client Request → API Key Validation → Request Validation → 
Prompt Handler → LangChain Execution → LLM API Call → 
Response Processing → Tracing → Client Response
```

### 3.3 Konfigurációs Rendszer

#### 3.3.1 Környezeti Változók

| Változó | Leírás | Alapértelmezett | Kötelező |
|---------|--------|----------------|----------|
| `LANGFUSE_PUBLIC_KEY` | LangFuse publikus kulcs | - | Igen |
| `LANGFUSE_SECRET_KEY` | LangFuse titkos kulcs | - | Igen |
| `LANGFUSE_HOST` | LangFuse szerver URL | https://cloud.langfuse.com | Nem |
| `OPENAI_API_KEY` | OpenAI API kulcs | - | Igen |
| `API_KEY` | Endpoint hitelesítési kulcs | "42" | Nem |
| `LANGFUSE_TAGS` | Prompt szűrő tagek | - | Nem |
| `LOG_LEVEL` | Logging szint | INFO | Nem |

#### 3.3.2 LangFuse Konfiguráció

```json
{
  "model_name": "gpt-4o-mini",
  "temperature": 0.7,
  "output_structure": {
    "title": "Response",
    "type": "object",
    "properties": {
      "answer": {"type": "string"},
      "confidence": {"type": "number"}
    }
  }
}
```

### 3.4 Hibakezelés és Logging

#### 3.4.1 Logging Stratégia

- **Structured Logging**: JSON formátumú logok
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **File Rotation**: Napi fájlok, 10MB limit
- **Console Output**: Fejlesztési környezetben

#### 3.4.2 Hibakezelési Szintek

1. **Inicializálási Hibák**
   - LangFuse kapcsolat hiba
   - Környezeti változók hiánya
   - Prompt konfigurációs hibák

2. **Runtime Hibák**
   - LLM API hibák
   - Prompt végrehajtási hibák
   - Validációs hibák

3. **HTTP Hibák**
   - 401: Unauthorized (hibás API kulcs)
   - 422: Validation Error (hibás input)
   - 500: Internal Server Error (rendszerhiba)

### 3.5 Teljesítmény Optimalizálás

#### 3.5.1 Aszinkron Feldolgozás

- **Async/Await**: Minden I/O művelet aszinkron
- **Concurrent Description Generation**: Párhuzamos leírás generálás
- **Connection Pooling**: HTTP kliens újrafelhasználás

#### 3.5.2 Caching Stratégia

- **Prompt Cache**: LangFuse prompt cache
- **Model Cache**: LLM model instance cache
- **Configuration Cache**: Környezeti változók cache

## 4. Deployment Architektúra

### 4.1 Docker Konfiguráció

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### 4.2 Docker Compose

```yaml
version: '3.8'
services:
  langfuse-swagger:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./logs:/app/logs
```

### 4.3 Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langfuse-swagger
spec:
  replicas: 3
  selector:
    matchLabels:
      app: langfuse-swagger
  template:
    metadata:
      labels:
        app: langfuse-swagger
    spec:
      containers:
      - name: langfuse-swagger
        image: nemesgyadam/langfuse-swagger:latest
        ports:
        - containerPort: 8000
        env:
        - name: LANGFUSE_PUBLIC_KEY
          valueFrom:
            secretKeyRef:
              name: langfuse-secrets
              key: public-key
```

## 5. Biztonsági Implementáció

### 5.1 Hitelesítés

- **API Key Authentication**: X-API-Key header
- **Environment-based Configuration**: Titkos kulcsok környezeti változókban
- **Rate Limiting**: FastAPI middleware-rel

### 5.2 Adatvédelem

- **Input Sanitization**: Pydantic validáció
- **Output Filtering**: Strukturált válaszok
- **Logging Masking**: Érzékeny adatok maszkolása

## 6. Monitorozás és Observability

### 6.1 Metrics

- **Request Count**: Végpont használati statisztikák
- **Response Time**: Átlagos válaszidő
- **Error Rate**: Hibaarány
- **LLM Usage**: Token felhasználás

### 6.2 Tracing

- **LangFuse Integration**: Automatikus trace generálás
- **Request Correlation**: Egyedi request ID-k
- **Performance Tracking**: Lépésenkénti időmérés

## 7. Tesztelési Stratégia

### 7.1 Unit Tesztek

```python
# test_prompt_handler.py
async def test_handle_prompt_success():
    # Mock LangFuse client
    # Test prompt execution
    # Assert response format

async def test_handle_prompt_error():
    # Mock LLM error
    # Test error handling
    # Assert HTTP exception
```

### 7.2 Integrációs Tesztek

```python
# test_api_integration.py
async def test_endpoint_generation():
    # Test dynamic endpoint creation
    # Verify Swagger documentation
    # Test API key authentication
```

### 7.3 End-to-End Tesztek

- **Docker Container Testing**: Teljes alkalmazás tesztelése
- **API Endpoint Testing**: Swagger UI tesztelés
- **Load Testing**: Teljesítmény tesztelés

## 8. Karbantartás és Frissítések

### 8.1 Verziókezelés

- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Docker Tags**: Verzió alapú tagek
- **API Versioning**: URL path alapú verziókezelés

### 8.2 Frissítési Folyamat

1. **Development**: Fejlesztési környezetben tesztelés
2. **Staging**: Staging környezetben validálás
3. **Production**: Rolling update deployment
4. **Rollback**: Automatikus visszaállítás hiba esetén

## 9. Jövőbeli Fejlesztések

### 9.1 Tervezett Funkciók

- [ ] **Custom Handlers**: További LLM integráció
- [ ] **Async Response**: Aszinkron válaszkezelés
- [ ] **Multi-LLM Support**: Több LLM provider támogatás
- [ ] **Auto-sync**: LangFuse prompt szinkronizálás
- [ ] **Advanced Caching**: Redis-based caching

### 9.2 Teljesítmény Javítások

- [ ] **Connection Pooling**: Optimalizált kapcsolatkezelés
- [ ] **Request Batching**: Kérések csoportosítása
- [ ] **Background Tasks**: Háttér feladatok
- [ ] **Health Checks**: Rendszer állapot monitorozás

## 10. Összefoglalás

A LangFuse-Swagger implementációs terve egy robusztus, skálázható és karbantartható rendszert ír le, amely:

- **Moduláris architektúra** alkalmazásával biztosítja a kód újrafelhasználhatóságát
- **Aszinkron feldolgozás** révén optimális teljesítményt nyújt
- **Comprehensive logging és tracing** segítségével átlátható működést biztosít
- **Docker-based deployment** révén egyszerű telepítést és skálázást tesz lehetővé
- **Biztonsági best practices** alkalmazásával védett működést garantál

A rendszer készen áll a production környezetben való használatra, és könnyen bővíthető további funkciókkal.
