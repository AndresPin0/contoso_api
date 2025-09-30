from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
import asyncio
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="Contoso Banking API",
    description="API demo para Copilot Studio (User Profile y Balance Information)",
    version="2.0.0"
)

# -------------------------------
# MODELOS
# -------------------------------
class Account(BaseModel):
    id: str
    type: str
    currency: str

class UserProfile(BaseModel):
    userId: str
    name: str
    email: str
    accounts: List[Account]

class BalanceRequest(BaseModel):
    accountId: str

class BalanceResponse(BaseModel):
    accountId: str
    balance: float
    currency: str

# -------------------------------
# DATOS MOCK
# -------------------------------
users_db = {
    "user123": UserProfile(
        userId="user123",
        name="Pepito Pérez",
        email="pepito.perez@contoso.com",
        accounts=[
            Account(id="acc001", type="Checking", currency="COP"),
            Account(id="acc002", type="Savings", currency="COP"),
            Account(id="acc003", type="Credit", currency="COP"),
        ]
    ),
    "user456": UserProfile(
        userId="user456",
        name="María López",
        email="maria.lopez@contoso.com",
        accounts=[
            Account(id="acc004", type="Checking", currency="USD"),
            Account(id="acc005", type="Savings", currency="USD"),
            Account(id="acc006", type="Credit", currency="USD"),
        ]
    ),
    "user789": UserProfile(
        userId="user789",
        name="Carlos Torres",
        email="carlos.torres@contoso.com",
        accounts=[
            Account(id="acc007", type="Checking", currency="EUR"),
            Account(id="acc008", type="Savings", currency="EUR"),
            Account(id="acc009", type="Credit", currency="EUR"),
        ]
    )
}

balances_db = {
    # Pepito
    "acc001": {"balance": 1250000.50, "currency": "COP"},
    "acc002": {"balance": 3450000.00, "currency": "COP"},
    "acc003": {"balance": -150000.00, "currency": "COP"},
    # María
    "acc004": {"balance": 2500.75, "currency": "USD"},
    "acc005": {"balance": 8600.00, "currency": "USD"},
    "acc006": {"balance": -1200.00, "currency": "USD"},
    # Carlos
    "acc007": {"balance": 980.30, "currency": "EUR"},
    "acc008": {"balance": 15000.00, "currency": "EUR"},
    "acc009": {"balance": -500.00, "currency": "EUR"},
}

# -------------------------------
# ENDPOINTS
# -------------------------------

@app.get("/users", response_model=List[UserProfile])
def list_users():
    """
    Lista todos los usuarios registrados.
    """
    return list(users_db.values())

@app.get("/user/profile", response_model=UserProfile)
def get_user_profile(
    userId: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    name: Optional[str] = Query(None)
):
    """
    Devuelve el perfil de usuario según userId, email o name.
    """
    for u in users_db.values():
        if userId and u.userId == userId:
            return u
        if email and u.email.lower() == email.lower():
            return u
        if name and u.name.lower() == name.lower():
            return u
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


@app.post("/account/balance", response_model=BalanceResponse)
def get_balance(req: BalanceRequest):
    """
    Devuelve el saldo de una cuenta específica.
    """
    if req.accountId not in balances_db:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    data = balances_db[req.accountId]
    return BalanceResponse(
        accountId=req.accountId,
        balance=data["balance"],
        currency=data["currency"]
    )


@app.get("/stream")
async def stream_llm(
    message: Optional[str] = Query(
        "Hola, soy un LLM de ejemplo. Estoy transmitiendo este mensaje palabra por palabra.",
        description="Mensaje a transmitir palabra por palabra"
    ),
    delay_ms: int = Query(150, ge=0, le=5000, description="Retraso entre palabras en milisegundos")
):
    """
    Emite un stream de texto plano simulando la escritura de un LLM, palabra por palabra
    en una sola línea.

    - message: texto a emitir
    - delay_ms: retardo entre palabras (ms)
    """

    async def word_stream():
        for word in message.split():
            yield f"{word} "
            await asyncio.sleep(delay_ms / 1000)
        yield "."

    return StreamingResponse(
        word_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/generate_stream")
async def generate_stream(
    prompt: Optional[str] = Query(
        "Dame una respuesta breve simulada por un LLM.",
        description="Prompt de entrada para la simulación"
    )
):
    """
    Endpoint alterno inspirado en tu ejemplo: stream de texto plano palabra a palabra
    usando un generador asíncrono (no bloquea el event loop).
    """

    async def fake_llm_stream_async(text_prompt: str):
        text = "Esta es una respuesta simulada como si fuera un LLM."
        for word in text.split():
            yield word + " "
            await asyncio.sleep(0.3)

    return StreamingResponse(
        fake_llm_stream_async(prompt),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )