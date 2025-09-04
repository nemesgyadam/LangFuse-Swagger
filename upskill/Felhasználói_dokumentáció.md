# LangFuse-Swagger Felhasználói Dokumentáció

## Áttekintés

A LangFuse-Swagger egy univerzális FastAPI szerver, amely automatikusan generál API végpontokat Swagger UI-val bármely Langfuse projektből. Ha van egy Langfuse projektje promptokkal (szöveges vagy chat) és modell konfigurációkkal, ez az eszköz dinamikusan hoz létre FastAPI végpontokat az összes szükséges bemenettel, amelyek készen állnak a használatra a Swaggerben.

## Főbb Funkciók

- **Dinamikus Végpont Generálás**: Automatikusan hoz létre végpontokat a Langfuse projekt promptjaiból
- **Chat és Szöveges Sablonok Támogatása**: Rugalmas kezelés különböző prompt típusokhoz
- **LangChain Integráció**: Zökkenőmentes kapcsolat a LangChain-nel a továbbfejlesztett nyelvi modell funkcionalitásért
- **Konfigurálható Paraméterek**: Modell típus, hőmérséklet és egyéb változók konfigurálása közvetlenül a Langfuse-on keresztül
- **Nyomkövetési Naplózás**: Részletes naplókat rögzít az interakciókról és nyomkövetésekről a Langfuse-szal
- **Strukturált Válaszok**: API válasz formátum meghatározása JSON Schema segítségével

## Rendszerkövetelmények

- Python 3.7+
- FastAPI
- Langfuse fiók és projekt
- OpenAI API kulcs (vagy más támogatott LLM szolgáltató)

## Telepítés és Beállítás

### 1. Környezeti Változók Beállítása

Hozzon létre egy `.env` fájlt a projekt gyökérkönyvtárában a következő változókkal:

```env
# Kötelező változók
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
OPENAI_API_KEY=your_openai_api_key

# Opcionális változók
LANGFUSE_HOST=https://cloud.langfuse.com
API_KEY=42
LANGFUSE_TAGS=swagger,api,production
LOG_LEVEL=INFO
```

### 2. Függőségek Telepítése

```bash
pip install -r requirements.txt
```

### 3. Langfuse Projekt Beállítása

1. Hozzon létre egy Langfuse projektet
2. Definiáljon promptokat a projektben
3. Állítsa be a modell konfigurációkat (opcionális)
4. Adjon hozzá tageket a promptokhoz szűréshez (opcionális)

## Használat

### Indítási Módok

#### 1. Közvetlen Python Futtatás
```bash
python main.py
```

#### 2. Docker Konténer
```bash
docker-compose up -d
```

### API Elérése

1. **Swagger Dokumentáció**: [http://localhost:8000/docs](http://localhost:8000/docs)
2. **API Hívások**: HTTP kliensekkel (Postman, curl, stb.)

## Környezeti Változók Referencia

| Változó | Leírás | Alapértelmezett | Kötelező |
|---------|--------|----------------|----------|
| `LANGFUSE_PUBLIC_KEY` | Langfuse nyilvános kulcs | - | Igen |
| `LANGFUSE_SECRET_KEY` | Langfuse titkos kulcs | - | Igen |
| `LANGFUSE_HOST` | Langfuse szerver URL | https://cloud.langfuse.com | Nem |
| `OPENAI_API_KEY` | OpenAI API kulcs | - | Igen |
| `API_KEY` | API végpontok hitelesítési kulcsa | "42" | Nem |
| `LANGFUSE_TAGS` | Vesszővel elválasztott tag lista | - | Nem |
| `LOG_LEVEL` | Naplózási szint | INFO | Nem |

## Prompt Konfiguráció

### Alapvető Prompt Létrehozása

1. Lépjen be a Langfuse projektjébe
2. Hozzon létre új promptot
3. Definiálja a változókat `{{változó_név}}` formátumban
4. Állítsa be a modell paramétereket (opcionális)

### Strukturált Kimenet Beállítása

A `output_structure` mező segítségével JSON Schema formátumban definiálhatja a válasz struktúráját:

```json
{
  "output_structure": {
    "title": "Válasz",
    "description": "A válasz és az összefoglaló nagybetűs legyen.",
    "type": "object",
    "properties": {
      "valasz": {
        "type": "string",
        "description": "A felhasználó kérdésére adott válasz"
      },
      "osszefoglalo": {
        "type": "string",
        "description": "A válasz összefoglalója"
      }
    }
  }
}
```

## API Használat

### Hitelesítés

Minden API híváshoz szükséges az `X-API-Key` header megadása:

```bash
curl -X POST "http://localhost:8000/prompt/my_prompt" \
  -H "X-API-Key: 42" \
  -H "Content-Type: application/json" \
  -d '{"parameter1": "érték1", "parameter2": "érték2"}'
```

### Végpont Struktúra

- **URL**: `/prompt/{prompt_név}`
- **Metódus**: POST
- **Headers**: `X-API-Key`, `Content-Type: application/json`
- **Body**: JSON objektum a prompt változóival

### Példa API Hívás

```python
import requests

url = "http://localhost:8000/prompt/code_review"
headers = {
    "X-API-Key": "42",
    "Content-Type": "application/json"
}
data = {
    "code": "def hello(): print('Hello World')",
    "language": "python"
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

## Naplózás és Hibakeresés

### Naplófájlok

- Helye: `logs/app_YYYYMMDD.log`
- Rotáció: 10MB méretenként, 5 backup fájl
- Formátum: Időbélyeg, modul, szint, üzenet

### Naplózási Szintek

- `DEBUG`: Részletes hibakeresési információk
- `INFO`: Általános működési információk
- `WARNING`: Figyelmeztetések
- `ERROR`: Hibák

### Gyakori Hibák és Megoldások

#### 1. "Invalid API key" Hiba
- **Ok**: Hibás vagy hiányzó API kulcs
- **Megoldás**: Ellenőrizze az `X-API-Key` header értékét

#### 2. "Failed to initialize Langfuse client" Hiba
- **Ok**: Hibás Langfuse hitelesítési adatok
- **Megoldás**: Ellenőrizze a `LANGFUSE_PUBLIC_KEY` és `LANGFUSE_SECRET_KEY` értékeket

#### 3. "No prompts found" Hiba
- **Ok**: Nincsenek promptok a projektben vagy nem megfelelő tagek
- **Megoldás**: Ellenőrizze a Langfuse projektben a promptokat és a `LANGFUSE_TAGS` beállítást

## Fejlett Funkciók

### Tag-alapú Szűrés

A `LANGFUSE_TAGS` környezeti változó segítségével szűrheti, mely promptok alapján generálódnak végpontok:

```env
LANGFUSE_TAGS=production,api,v2
```

### Modell Konfiguráció

A Langfuse-ban minden prompthoz beállíthatja:
- Modell típusát (`model_name`)
- Hőmérsékletet (`temperature`)
- Kimeneti struktúrát (`output_structure`)

### Nyomkövetés

Minden API hívás automatikusan naplózásra kerül a Langfuse-ban:
- Bemeneti paraméterek
- Használt prompt
- Modell válasza
- Végrehajtási idő
- Hibák (ha vannak)

## Teljesítmény Optimalizálás

### Ajánlások

1. **Aszinkron Feldolgozás**: A szerver aszinkron módon dolgozza fel a kéréseket
2. **Naplózási Szint**: Éles környezetben használjon `INFO` vagy `WARNING` szintet
3. **Memória Kezelés**: A naplófájlok automatikusan rotálódnak
4. **Kapcsolat Pooling**: A Langfuse kliens újrafelhasználja a kapcsolatokat

## Biztonsági Megfontolások

1. **API Kulcs Védelem**: Soha ne tegye közzé az API kulcsokat
2. **Környezeti Változók**: Használjon `.env` fájlt vagy biztonságos környezeti változókat
3. **HTTPS**: Éles környezetben mindig használjon HTTPS-t
4. **Hozzáférés Korlátozás**: Korlátozza a hálózati hozzáférést szükség szerint

## Hibaelhárítás

### Diagnosztikai Lépések

1. Ellenőrizze a naplófájlokat
2. Tesztelje a Langfuse kapcsolatot
3. Ellenőrizze a környezeti változókat
4. Tesztelje az API kulcsokat

### Támogatás

- **GitHub Issues**: [Projekt repository](../../issues)
- **Dokumentáció**: Ez a dokumentum
- **Naplók**: Részletes hibainformációk a log fájlokban

## Példa Workflow

1. **Projekt Beállítás**: Langfuse projekt létrehozása
2. **Prompt Definiálás**: Promptok és változók meghatározása
3. **Környezet Konfigurálás**: `.env` fájl beállítása
4. **Szerver Indítás**: `python main.py` vagy Docker
5. **API Tesztelés**: Swagger UI használata
6. **Integráció**: Saját alkalmazásba beépítés

## Következő Lépések

- Ismerkedjen meg a Swagger UI-val
- Hozzon létre saját promptokat
- Tesztelje különböző modell konfigurációkat
- Integrálja saját alkalmazásaiba
- Monitorozza a teljesítményt és naplókat

---

*Ez a dokumentáció a LangFuse-Swagger v1.0.0 verzióhoz készült. A legfrissebb információkért látogassa meg a projekt GitHub repository-ját.*
