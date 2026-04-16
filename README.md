# Store Management System

A web-based Store Management System built with **Python**, **SQLite**, and **Flask**. Manages inventory (Products), sales (Invoices/Customers), and restocking (Purchases/Dealers).

## Key Technologies

- **Python 3** — application logic
- **SQLite** — embedded relational database
- **Flask** — web application framework
- **Docker & Docker Compose** — containerization and orchestration

## Quick Start

### Docker (Recommended)

```bash
docker compose up --build
```

Open `http://localhost:5000`.

To reset the database:

```bash
docker compose down -v
docker compose up --build
```

### Local

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`. The SQLite database (`data/store.db`) is created and seeded automatically on first run.

## Database Schema

| Table | Key Columns |
|---|---|
| Product | PID, PName, Unit1, Unit2, ConversionFactor, Quantity, Price |
| Customer | CID, CName, Address, IDNumber, Phone |
| Dealer | DID, DName |
| Salesperson | SID, SName, Phone |
| Invoices | InvoiceID, CID, SalespersonID, InvoiceDate, CreatedAt, TotalAmt |
| InvoiceDetails | LineID, InvoiceID, PID, SelectedUnit, Quantity, Price |
| Purchases | PurchaseID, DID, PurchaseDate, CreatedAt, TotalAmt |
| PurchaseDetails | LineID, PurchaseID, PID, SelectedUnit, Quantity, Price |
