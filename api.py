from fastapi import FastAPI, HTTPException, Query
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
