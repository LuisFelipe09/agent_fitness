#!/bin/bash

# Exit on error
set -e

# --- Frontend Build ---
echo "Building Frontend..."
if [ -d "frontend_src" ]; then
    cd frontend_src

    # Check if node is installed, if not, print warning (Render Python env usually has older node or none, but often recent images have it)
    node -v
    npm -v

    echo "Installing frontend dependencies..."
    npm install

    echo "Building React app..."
    npm run build

    cd ..
else
    echo "frontend_src directory not found!"
    exit 1
fi

# --- Backend Build ---
echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running database migrations..."
# Run authentication columns migration
python migrations/migrate_auth_columns.py

# Create tables if they don't exist
python -c "from src.infrastructure.database import Base, engine; Base.metadata.create_all(bind=engine)"

echo "Build completed successfully!"
