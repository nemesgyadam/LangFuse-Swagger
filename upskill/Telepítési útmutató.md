# LangFuse-Swagger Telepítési Útmutató

## Áttekintés

A LangFuse-Swagger egy univerzális FastAPI szerver, amely automatikusan generál végpontokat Swagger UI-val bármely Langfuse projektből. Ha van egy Langfuse projekted prompt-okkal (szöveges vagy chat) és modell konfigurációkkal, ez az eszköz dinamikusan hoz létre FastAPI végpontokat az összes szükséges bemenettel, készen a Swagger használatára.

## Előfeltételek

- Python 3.7 vagy újabb
- Docker (opcionális)
- OpenAI API kulcs
- Langfuse fiók és projekt

## 1. Projekt letöltése

```bash
git clone <repository-url>
cd LangFuse-Swagger
```

## 2. Python környezet beállítása

### Virtuális környezet létrehozása (ajánlott)

```bash
python -m venv venv
```

### Virtuális környezet aktiválása

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Függőségek telepítése

```bash
pip install -r requirements.txt
```

## 3. Környezeti változók beállítása

### .env fájl létrehozása

Másold le a `.env.example` fájlt `.env` néven:

```bash
copy .env.example .env
```

### Környezeti változók konfigurálása

Szerkeszd a `.env` fájlt és add meg a következő értékeket:

```env
# Langfuse konfiguráció (kötelező)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com

# OpenAI API kulcs (kötelező)
OPENAI_API_KEY=your_openai_api_key

# API kulcs az endpoint hitelesítéshez (opcionális)
API_KEY=42

# Langfuse tag szűrés (opcionális)
LANGFUSE_TAGS=swagger,api,production

# Log szint (opcionális)
LOG_LEVEL=INFO
```

### Környezeti változók magyarázata

| Változó | Leírás | Alapértelmezett | Kötelező |
|---------|--------|----------------|----------|
| `LANGFUSE_PUBLIC_KEY` | Langfuse nyilvános kulcs | - | Igen |
| `LANGFUSE_SECRET_KEY` | Langfuse titkos kulcs | - | Igen |
| `LANGFUSE_HOST` | Langfuse host URL | https://cloud.langfuse.com | Nem |
| `OPENAI_API_KEY` | OpenAI API kulcs | - | Igen |
| `API_KEY` | API kulcs endpoint hitelesítéshez | "42" | Nem |
| `LANGFUSE_TAGS` | Vesszővel elválasztott tag lista | - | Nem |
| `LOG_LEVEL` | Log részletesség szintje | INFO | Nem |

## 4. Langfuse projekt beállítása

1. **Langfuse fiók létrehozása**: Regisztrálj a [Langfuse](https://langfuse.com/) oldalon
2. **Projekt létrehozása**: Hozz létre egy új projektet a Langfuse dashboardon
3. **Prompt-ok konfigurálása**: 
   - Definiálj prompt-okat a Langfuse projektben
   - A prompt változók automatikusan megjelennek a Swagger API bemenetként
4. **API kulcsok megszerzése**: Másold ki a projekt API kulcsait

## 5. Alkalmazás futtatása

### Módszer 1: Közvetlen Python futtatás

```bash
python main.py
```

### Módszer 2: Docker használata

#### Docker Compose-zal (ajánlott)

```bash
docker-compose up -d
```

#### Manuális Docker futtatás

```bash
docker run -d \
  -p 8000:8000 \
  -e LANGFUSE_PUBLIC_KEY=your_key \
  -e LANGFUSE_SECRET_KEY=your_secret \
  -e OPENAI_API_KEY=your_openai_key \
  nemesgyadam/langfuse-swagger:latest
```

## 6. API elérése

### Swagger UI

Nyisd meg a böngészőt és navigálj a következő címre:
[http://localhost:8000/docs](http://localhost:8000/docs)

### API hívások tesztelése

Az endpoint-okat tesztelheted:
- Swagger UI interaktív felületén
- HTTP kliensekkel (pl. Postman)
- Parancssori eszközökkel (pl. curl)

### Példa API hívás

```bash
curl -X POST "http://localhost:8000/your-endpoint" \
  -H "X-API-Key: 42" \
  -H "Content-Type: application/json" \
  -d '{"input": "your input data"}'
```

## 7. Strukturált válaszok konfigurálása

A Langfuse Config-ban használd az `output_structure` mezőt strukturált válaszok definiálásához:

```json
{
  "output_structure": {
    "title": "Answer",
    "description": "A válasz és összefoglaló nagybetűkkel",
    "type": "object",
    "properties": {
      "answer": {
        "type": "string",
        "description": "A felhasználó kérdésére adott válasz"
      },
      "summary": {
        "type": "string", 
        "description": "A válasz összefoglalása"
      }
    }
  }
}
```

## 8. Hibaelhárítás

### Gyakori problémák

1. **Port már használatban**: Változtasd meg a portot a `docker-compose.yaml`-ban
2. **API kulcs hibák**: Ellenőrizd a környezeti változók helyességét
3. **Langfuse kapcsolódási problémák**: Győződj meg róla, hogy a Langfuse kulcsok érvényesek

### Log-ok ellenőrzése

```bash
# Docker esetén
docker logs langfuse-swagger

# Közvetlen futtatás esetén
# A log-ok a konzolon jelennek meg
```

## 9. Fejlesztői környezet

### Kód módosítások után

```bash
# Újraindítás szükséges
python main.py
```

### Docker image újraépítése

```bash
docker-compose down
docker-compose up --build -d
```

## 10. Biztonsági megjegyzések

- Soha ne commitold az API kulcsokat a verziókezelőbe
- Használj erős API kulcsokat production környezetben
- Korlátozd a hálózati hozzáférést szükség szerint

## Támogatás

Problémák esetén:
1. Ellenőrizd a log-okat
2. Győződj meg róla, hogy minden környezeti változó be van állítva
3. Nyiss issue-t a GitHub repository-ban

## Következő lépések

Az alkalmazás sikeres telepítése után:
1. Teszteld az API végpontokat a Swagger UI-ban
2. Konfiguráld a Langfuse prompt-jaidat
3. Állítsd be a strukturált válasz formátumokat
4. Integráld az alkalmazást a saját rendszereidbe
