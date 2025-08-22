#!/bin/bash

# Docker Startup Script for Lovable Backend
# This script builds and starts the backend services with database

set -e

echo "🚀 Starting Lovable Backend with Database Setup..."

# Create necessary directories
mkdir -p docker/postgres/init
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/pgadmin

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build backend image
echo "🔨 Building backend Docker image..."
docker-compose -f docker-compose.backend.yml build backend

# Start services
echo "🐘 Starting PostgreSQL database..."
docker-compose -f docker-compose.backend.yml up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker-compose -f docker-compose.backend.yml exec postgres pg_isready -U lovable -d lovable_db; do
    echo "PostgreSQL is not ready yet. Waiting..."
    sleep 2
done

echo "✅ PostgreSQL is ready!"

# Start Redis
echo "🔴 Starting Redis cache..."
docker-compose -f docker-compose.backend.yml up -d redis

# Start PGAdmin
echo "🔧 Starting PGAdmin..."
docker-compose -f docker-compose.backend.yml up -d pgadmin

# Start backend service
echo "🚀 Starting backend API..."
docker-compose -f docker-compose.backend.yml up -d backend

# Show status
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.backend.yml ps

echo ""
echo "🎉 Lovable Backend is now running!"
echo ""
echo "📱 Available Services:"
echo "   • Backend API:      http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • PostgreSQL:       localhost:5432"
echo "   • Redis:            localhost:6379"
echo "   • PGAdmin:          http://localhost:8080"
echo ""
echo "🔑 Default Credentials:"
echo "   • Database: lovable / lovable123"
echo "   • PGAdmin:  admin@lovable.com / admin123"
echo "   • Admin User: admin / admin123"
echo ""
echo "🛠️  Useful Commands:"
echo "   • Stop all services:    docker-compose -f docker-compose.backend.yml down"
echo "   • View logs:           docker-compose -f docker-compose.backend.yml logs -f"
echo "   • Restart backend:     docker-compose -f docker-compose.backend.yml restart backend"
echo "   • Database shell:      docker-compose -f docker-compose.backend.yml exec postgres psql -U lovable -d lovable_db"
echo ""
