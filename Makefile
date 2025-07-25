.PHONY: help install test run-backend run-frontend build clean docker-up docker-down

# Default target
help:
	@echo "DermaMed Development Commands:"
	@echo "  make install        - Install all dependencies"
	@echo "  make test          - Run tests"
	@echo "  make run-backend   - Run backend development server"
	@echo "  make run-frontend  - Run frontend development server"
	@echo "  make build         - Build production images"
	@echo "  make docker-up     - Start all services with Docker"
	@echo "  make docker-down   - Stop all Docker services"
	@echo "  make clean         - Clean temporary files"

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && python -m venv venv && \
		. venv/bin/activate && \
		pip install -r requirements.txt
	@echo "Backend dependencies installed!"
	@echo "Note: Frontend dependencies will be installed when implemented"

# Run tests
test:
	@echo "Running backend tests..."
	cd backend && python test_setup.py

# Run backend server
run-backend:
	@echo "Starting backend server..."
	cd backend && python run_dev.py

# Run frontend server
run-frontend:
	@echo "Starting frontend server..."
	cd frontend && npm install && npm run dev

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start all services with Docker
docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d
	@echo "Services started!"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

# Stop Docker services
docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "Cleanup complete!"

# Database migrations (placeholder for future use)
migrate:
	@echo "Database migrations not yet implemented"

# Create superuser (placeholder for future use)
createsuperuser:
	@echo "Creating demo user..."
	@echo "Username: demo_doctor"
	@echo "Password: demo123"