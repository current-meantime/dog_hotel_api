# Dog Hotel API

A RESTful API for managing a dog hotel, including dogs, owners, stays, payments, and bank transfers. Built with FastAPI and SQLAlchemy, featuring advanced search, validation, and scheduled background tasks.

## Features

- **Dog Management:** CRUD operations, advanced filtering (by owner, medication, food, notes).
- **Owner Management:** CRUD, search by contact info, unpaid/overdue status.
- **Stay Management:** CRUD, filter by date, status (upcoming/ongoing/ending soon), overlap validation.
- **Payments:** CRUD, filter by paid/overdue status, automatic calculation and update.
- **Bank Transfers:** CRUD, match transfers to payments, filter by sender/matched status.
- **Schedulers:**
    - Automatic annual update of dog ages.
    - Automatic matching of bank transfers to payments.
    - Manual trigger endpoint for bank transfer scheduler.
- **Logging:** File and console logging for operations and errors.
- **Environment:** Uses `.env` for configuration, supports SQLite and other databases.


## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/current-meantime/dog-hotel-api.git
cd dog_hotel_api
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
    - Create a `.env` file in the root directory.
    - Example:

```
DATABASE_URL=sqlite:///dog_hotel.db
```

5. **Start the API:**

```bash
uvicorn main:app --reload
```



## API Overview

| Resource | Path Prefix | Description |
| :-- | :-- | :-- |
| Dogs | `/dogs` | Manage dogs |
| Owners | `/owners` | Manage owners |
| Stays | `/stays` | Manage stays |
| Payments | `/payments` | Manage payments |
| Bank Transfers | `/bank_transfers` | Manage bank transfers |
| Scheduler | `/scheduler` | Trigger background tasks |

### Example Endpoints

- `GET /dogs/` - List/search dogs (by owner, name, medication, etc.)
- `POST /dogs/` - Add a new dog
- `PUT /dogs/{dog_id}` - Update dog info
- `DELETE /dogs/{dog_id}` - Remove a dog
- `GET /owners/` - List/search owners (by name, email, unpaid, overdue, etc.)
- `POST /owners/` - Add a new owner
- `GET /stays/` - List/search stays (by date, status, dog, owner)
- `POST /stays/` - Add a new stay (validates overlap, auto-creates payment)
- `GET /payments/` - List/search payments (by paid/overdue status, owner, stay)
- `POST /payments/` - Add a payment
- `GET /bank_transfers/` - List/search bank transfers (by sender, matched status)
- `POST /bank_transfers/` - Add a bank transfer
- `POST /scheduler/run-bank-transfer-scheduler` - Trigger bank transfer matching


## Background Tasks

- **Dog Age Update:** Increases dog ages yearly for dogs added over a year ago.
- **Bank Transfer Matching:** Matches incoming bank transfers to payments by parsing transfer titles as stay IDs; marks payments as paid/overdue based on amounts.
- **Scheduler:** Runs both tasks periodically (configured in `main.py`).


