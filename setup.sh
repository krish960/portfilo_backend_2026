#!/usr/bin/env bash
# ============================================================
#  PortfolioAI Backend — One-Click Setup Script
#  Usage:  cd backend && bash setup.sh
# ============================================================

set -e
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC}  $1"; }
success() { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}   PortfolioAI Backend Setup${NC}"
echo -e "${CYAN}   Database: SQLite (zero config)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ── 1. Python version check ──────────────────────────────────
info "Checking Python version..."
PY=$(python3 --version 2>&1)
if [[ $PY != *"3."* ]]; then
    error "Python 3.9+ required. Got: $PY"
fi
success "$PY found"

# ── 2. Virtual environment ───────────────────────────────────
if [ ! -d "venv" ]; then
    info "Creating virtual environment..."
    python3 -m venv venv
    success "venv created"
else
    success "venv already exists"
fi

info "Activating virtual environment..."
source venv/bin/activate

# ── 3. Install dependencies ──────────────────────────────────
info "Installing Python packages..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
success "All packages installed"

# ── 4. Environment file ──────────────────────────────────────
if [ ! -f ".env" ]; then
    info "Creating .env from .env.example..."
    cp .env.example .env
    warn ".env created. Edit it to add OAuth credentials if needed."
else
    success ".env already exists"
fi

# ── 5. Media & static dirs ───────────────────────────────────
mkdir -p media staticfiles
success "media/ and staticfiles/ directories ready"

# ── 6. Run migrations (creates db.sqlite3 automatically) ────
info "Running database migrations..."
python manage.py migrate --run-syncdb
success "db.sqlite3 created and all tables migrated"

# ── 7. Collect static files ──────────────────────────────────
info "Collecting static files..."
python manage.py collectstatic --noinput -v 0
success "Static files collected"

# ── 8. Create superuser ──────────────────────────────────────
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  Create Admin Superuser${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
read -p "Create a superuser now? (y/n): " CREATE_SU
if [[ "$CREATE_SU" == "y" || "$CREATE_SU" == "Y" ]]; then
    python manage.py createsuperuser
    success "Superuser created"
else
    warn "Skipped. Run 'python manage.py createsuperuser' later."
fi

# ── 9. Load sample data (optional) ───────────────────────────
if [ -f "fixtures/sample_data.json" ]; then
    read -p "Load sample data? (y/n): " LOAD_DATA
    if [[ "$LOAD_DATA" == "y" ]]; then
        python manage.py loaddata fixtures/sample_data.json
        success "Sample data loaded"
    fi
fi

# ── Done ─────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Start server:  ${CYAN}source venv/bin/activate && python manage.py runserver${NC}"
echo -e "  API base URL:  ${CYAN}http://localhost:8000/api/v1/${NC}"
echo -e "  Admin panel:   ${CYAN}http://localhost:8000/admin/${NC}"
echo -e "  SQLite DB:     ${CYAN}backend/db.sqlite3${NC}"
echo ""
