#!/bin/bash

# Exit on error
set -e

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running database migrations..."
# Create tables if they don't exist
python -c "from src.infrastructure.database import Base, engine; Base.metadata.create_all(bind=engine)"

echo "Build completed successfully!"
