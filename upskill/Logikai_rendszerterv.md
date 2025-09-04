# Logikai Rendszerterv - LangFuse-Swagger API Generátor

## 1. Rendszer Áttekintés

A LangFuse-Swagger egy univerzális FastAPI szerver, amely automatikusan generál API végpontokat Swagger UI-val bármely LangFuse projektből. A rendszer dinamikusan hoz létre FastAPI végpontokat a LangFuse projektben található promptok alapján.

## 2. Moduláris Architektúra

### 2.1 Főbb Komponensek

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRY POINT                             │
│                        main.py                                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                            │
│                  app_generator.py                              │
│              PromptEndpointGenerator                           │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                               │
│                 prompt_handler.py                              │
│                  PromptHandler                                 │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MODEL LAYER                                │
│                  api_models.py                                 │
│         RequestModelGenerator, ResponseModelGenerator          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Támogató Modulok

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UTILS LAYER   │    │   LLM FACTORY   │    │  EXTERNAL APIs  │
│                 │    │                 │    │                 │
│ langfuse_utils  │    │  llm_factory    │    │   LangFuse      │
│   api_key       │    │                 │    │   OpenAI        │
│                 │    │                 │    │   Anthropic     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 3. Komponens Leírások

### 3.1 Entry Point (main.py)
**Felelősség:** Alkalmazás inicializálása és indítása
- FastAPI alkalmazás létrehozása
- Uvicorn szerver indítása
- Konfigurációs paraméterek beállítása

### 3.2 Application Layer (app_generator.py)
**Felelősség:** Központi alkalmazás logika és végpont generálás
- **PromptEndpointGenerator osztály:**
  - LangFuse kliens inicializálása
  - FastAPI alkalmazás konfigurálása
  - Dinamikus végpont generálás
  - Logging rendszer beállítása
  - Aszinkron leírás generálás

### 3.3 Service Layer (prompt_handler.py)
**Felelősség:** Prompt feldolgozás és LLM interakció
- **PromptHandler osztály:**
  - LangChain chain létrehozása
  - Chat és text promptok kezelése
  - LLM modell konfigurálás
  - Trace létrehozása és nyomon követés
  - Strukturált kimenet kezelése

### 3.4 Model Layer (api_models.py)
**Felelősség:** API séma definíciók és validáció
- **RequestModelGenerator:**
  - Dinamikus request modellek létrehozása
  - Pydantic validáció
  - Swagger dokumentáció generálás
- **ResponseModelGenerator:**
  - Strukturált válasz modellek
  - JSON Schema alapú típus mapping
  - Dinamikus response séma

### 3.5 Utils Layer
**Felelősség:** Segédeszközök és közös funkciók

#### 3.5.1 langfuse_utils.py
- Prompt változók kinyerése
- Projekt név lekérése
- Chat/text prompt típus detektálás
- Tag alapú szűrés

#### 3.5.2 api_key.py
- API kulcs validáció
- Biztonsági middleware
- Header alapú autentikáció

### 3.6 LLM Factory (llm_factory.py)
**Felelősség:** LLM provider absztrakció
- **LLMFactory osztály:**
  - Provider detektálás model név alapján
  - Multi-provider támogatás (OpenAI, Anthropic, Google)
  - Strukturált kimenet kezelése
  - Konfigurációs paraméterek kezelése

## 4. Adatfolyam Architektúra

### 4.1 Inicializálási Folyamat
```
main.py → PromptEndpointGenerator → LangFuse kapcsolat → 
Prompt konfigurációk lekérése → Végpontok generálása → 
FastAPI alkalmazás konfigurálása
```

### 4.2 Request Feldolgozási Folyamat
```
API Request → Autentikáció (api_key) → Request validáció → 
PromptHandler → LLM Factory → LangChain execution → 
Trace logging → Response generálás → JSON Response
```

### 4.3 Prompt Feldolgozási Folyamat
```
LangFuse Prompt → Változó kinyerés → Request Model generálás → 
Response Model generálás → Endpoint regisztrálás → 
Swagger dokumentáció frissítése
```

## 5. Külső Függőségek

### 5.1 Közvetlen Integrációk
- **LangFuse:** Prompt management és trace logging
- **FastAPI:** Web framework és API dokumentáció
- **LangChain:** LLM orchestration és chain management
- **Pydantic:** Adatvalidáció és séma generálás

### 5.2 LLM Providers
- **OpenAI:** GPT modellek
- **Anthropic:** Claude modellek  
- **Google:** Gemini modellek

### 5.3 Infrastrukturális Függőségek
- **Uvicorn:** ASGI szerver
- **Docker:** Konténerizáció
- **Environment Variables:** Konfigurációs management

## 6. Konfigurációs Réteg

### 6.1 Környezeti Változók
```
LANGFUSE_PUBLIC_KEY    → LangFuse autentikáció
LANGFUSE_SECRET_KEY    → LangFuse autentikáció  
LANGFUSE_HOST          → LangFuse szerver URL
OPENAI_API_KEY         → OpenAI API hozzáférés
API_KEY                → Endpoint autentikáció
LANGFUSE_TAGS          → Prompt szűrés
LOG_LEVEL              → Logging konfiguráció
```

### 6.2 Dinamikus Konfigurációk
- LangFuse projekt beállítások
- Prompt specifikus konfigurációk
- Model paraméterek (temperature, max_tokens)
- Strukturált kimenet sémák

## 7. Biztonsági Architektúra

### 7.1 Autentikáció Rétegek
- API kulcs alapú endpoint védelem
- LangFuse API kulcs management
- Provider specifikus API kulcsok

### 7.2 Validációs Mechanizmusok
- Pydantic alapú input validáció
- JSON Schema alapú output validáció
- Environment variable validáció

## 8. Monitorozás és Nyomon Követés

### 8.1 Logging Architektúra
- Strukturált logging (file + console)
- Rotating file handlers
- Konfigurálható log szintek
- Request/response trace logging

### 8.2 LangFuse Integráció
- Automatikus trace generálás
- Generation metadata rögzítése
- Performance monitoring
- Error tracking

## 9. Skálázhatósági Megfontolások

### 9.1 Horizontális Skálázás
- Stateless alkalmazás design
- Environment variable alapú konfiguráció
- Docker konténer támogatás

### 9.2 Vertikális Optimalizáció
- Aszinkron request handling
- Lazy loading mechanizmusok
- Memória hatékony model management

## 10. Bővíthetőségi Pontok

### 10.1 Új LLM Providers
- LLMFactory pattern bővítése
- Provider specifikus konfigurációk
- Model detection logic kiterjesztése

### 10.2 Új Funkciók
- Custom handlers implementálása
- Aszinkron response támogatás
- Batch processing képességek
- Webhook integráció lehetőségek
