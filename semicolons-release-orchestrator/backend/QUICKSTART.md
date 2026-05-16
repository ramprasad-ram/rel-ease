# 🚀 Quick Start Guide

Get the Release Orchestration Platform up and running in 5 minutes!

## Prerequisites

- Python 3.10+
- pip
- Git (optional)

## Step 1: Setup Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Application

```bash
# Copy example environment file
cp .env.example .env

# Edit .env if needed (optional for quick start)
# The defaults work out of the box!
```

## Step 3: Run the Application

```bash
# Start the server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload
```

## Step 4: Explore the API

Open your browser and visit:

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000

## 🎯 Try It Out!

### Using the Interactive Docs (Swagger UI)

1. Go to http://localhost:8000/docs
2. Explore the available endpoints
3. Click "Try it out" on any endpoint
4. Fill in the parameters
5. Click "Execute"
6. See the response!

### Example API Calls

#### 1. Check Health

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

#### 2. Get API Info

```bash
curl http://localhost:8000/api/v1/
```

#### 3. Create a Deployment (Once routes are implemented)

```bash
curl -X POST http://localhost:8000/api/v1/deployments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-api-service",
    "version": "1.0.0",
    "target_environment": "production",
    "target_platform": "kubernetes",
    "description": "Deploy new API version"
  }'
```

## 📊 Understanding the System

### Deployment Lifecycle

```
Create → Validate → Approve → Deploy → Monitor
```

### Workflow Types

1. **Sequential**: Steps run one after another
2. **Parallel**: Steps run simultaneously
3. **Conditional**: Steps run based on conditions
4. **Rollback**: Reverse deployment process

### AI Agents

1. **Deployment Decision Agent**: Analyzes if deployment is ready
2. **Anomaly Detection Agent**: Monitors for issues

## 🔧 Configuration Options

Edit `.env` to customize:

```env
# Enable/disable mock CI/CD
MOCK_CICD_ENABLED=true

# Adjust simulation delays (seconds)
MOCK_CICD_DELAY_MIN=2
MOCK_CICD_DELAY_MAX=5

# Set failure rate (0.0 to 1.0)
MOCK_CICD_FAILURE_RATE=0.1

# Enable/disable AI agents
AI_AGENT_ENABLED=true
```

## 📝 Next Steps

### For Development

1. **Explore the Code**
   - Check out `models/` for data structures
   - Look at `services/` for business logic
   - Review `workflows/` for orchestration

2. **Add Custom Features**
   - Create new workflow templates
   - Add custom AI agents
   - Extend the state machine

3. **Implement Routes**
   - Add deployment API handlers
   - Create workflow endpoints
   - Build agent integration APIs

### For Production

1. **Switch to PostgreSQL**
   ```env
   DATABASE_URL_PROD=postgresql://user:pass@localhost/db
   ```

2. **Disable Debug Mode**
   ```env
   DEBUG=false
   LOG_LEVEL=WARNING
   ```

3. **Add Authentication**
   - Implement JWT tokens
   - Add user management
   - Set up RBAC

4. **Deploy**
   - Use Docker
   - Set up CI/CD
   - Configure monitoring

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Use a different port
uvicorn main:app --port 8001
```

### Module Not Found

```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Issues

```bash
# Remove and recreate database
rm release_orchestrator.db
python main.py
```

## 📚 Learn More

- Read the full [README.md](README.md)
- Check the [API Documentation](http://localhost:8000/docs)
- Explore the code structure
- Review workflow templates in `workflows/templates.py`

## 💡 Tips

- Use the `/docs` endpoint for interactive API testing
- Check logs for detailed information
- Start with mock data to understand the system
- Customize workflow templates for your needs

## 🎉 You're Ready!

The platform is now running and ready for development. Start building your deployment automation system!

---

**Need Help?** Check the main README.md for detailed documentation.