# Google Gemini API Setup for JSSP Solver

Complete guide to enable Gemini LLM scheduling in your JSSP solver.

## 📋 Prerequisites

- Python 3.10+
- Google account (for Gemini API access)
- Internet connection

## 🔑 Step 1: Get Your Gemini API Key

### Option A: Free Tier (Recommended for testing)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Click **"Create API key"**
3. Select **"Create API key in new project"**
4. Copy the generated API key

### Option B: Google Cloud Console (for production)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the **Generative AI API**
4. Create credentials (API key)
5. Copy the API key

## 🚀 Step 2: Configure Your Environment

### Option A: Using .env file (Recommended)

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API key:
```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-pro
```

3. The script will automatically load this when you run it

### Option B: Export as environment variable (Windows PowerShell)

```powershell
$env:GEMINI_API_KEY="your_actual_api_key_here"
```

### Option C: Pass directly in code

```python
from src.ml_approaches import LLMScheduler

scheduler = LLMScheduler(api_key="your_actual_api_key_here")
```

## 📦 Step 3: Install Dependencies

```bash
# Activate virtual environment
.venvfabrek\Scripts\Activate.ps1

# Install/update packages
pip install -r requirements.txt

# Verify google-generativeai is installed
pip list | grep google-generativeai
```

## ✅ Step 4: Test the Setup

Run a quick test:

```bash
python -c "
from src.ml_approaches import LLMScheduler
from src.data import generate_random_jssp

# Create a small instance
instance = generate_random_jssp(3, 3, seed=42)

# Try LLM solver
scheduler = LLMScheduler()
schedule = scheduler.solve(instance, use_fallback=True)

print(f'✓ Gemini Available: {scheduler.gemini_available}')
print(f'✓ Solution Method: {schedule.metadata}')
print(f'✓ Makespan: {schedule.makespan}')
"
```

Expected output:
```
✓ Gemini Available: True
✓ Solution Method: {'method': 'Gemini LLM', 'model': 'gemini-pro', 'success': True}
✓ Makespan: XX
```

## 🎯 Step 5: Run Full Benchmark with Gemini

```bash
python main.py
```

You should see:
```
[6] Running LLM-augmented Scheduler...
    Gemini API call successful
    Makespan: XXX, Time: X.XXXs
```

## 📊 Available Gemini Models

```python
# Fast & cheaper
GEMINI_MODEL=gemini-pro

# More powerful (recommended for complex instances)
GEMINI_MODEL=gemini-1.5-pro

# Latest vision model
GEMINI_MODEL=gemini-1.5-pro-vision
```

## 🛠️ Troubleshooting

### ❌ "ImportError: No module named 'google.generativeai'"

```bash
pip install google-generativeai
```

### ❌ "GEMINI_API_KEY not found"

Check that:
1. `.env` file exists in project root
2. Contains: `GEMINI_API_KEY=sk-...`
3. Run: `pip install python-dotenv`

### ❌ "Invalid API Key"

1. Verify key at [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Check for extra spaces or newlines in `.env`
3. Regenerate key if needed

### ❌ "Resource exhausted: 429"

Gemini free tier has rate limits:
- 60 requests per minute
- 1500 requests per day

Wait a minute or use `use_fallback=True` (uses LPT heuristic).

### ❌ "Response didn't contain JSON"

Gemini sometimes returns reasoning before JSON. The code extracts JSON automatically, but if it fails:

1. Check that prompt is clear
2. Try with a smaller instance (3×3 instead of 10×10)
3. Verify API key has proper permissions

## 📈 Performance Tips

### Faster responses:
```python
scheduler = LLMScheduler(model="gemini-pro")  # Fastest
```

### Better quality (slower):
```python
scheduler = LLMScheduler(model="gemini-1.5-pro")  # Better reasoning
```

### Hybrid approach (recommended):
```python
# Use Gemini for initial solution, then refine with GA
from src.baselines import GeneticAlgorithmSolver

schedule_llm = scheduler.solve(instance)
# Could use this as seed for GA in future implementation
```

## 💰 Cost Estimation

### Free Tier:
- 1500 API calls/day
- Shared pool with other users
- Good for development/testing

### Paid Tier (pay-as-you-go):
- $0.075 per 1M input tokens (~1400 JSSP calls)
- $0.30 per 1M output tokens
- For 100 calls/day: ~$1-5/month

See [Gemini Pricing](https://ai.google.dev/pricing)

## 🔒 Security Best Practices

1. **Never commit .env file**
   - Already in `.gitignore`
   - Check before pushing: `git status`

2. **Use environment variables in CI/CD**
   ```bash
   # GitHub Actions example
   - name: Run tests
     env:
      GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    run: python main.py
   ```

3. **Rotate keys periodically**
   - Regenerate key if compromised
   - Archive old keys

## 📝 Example: Custom Prompting

If you want to modify how Gemini approaches JSSP:

```python
from src.ml_approaches import LLMScheduler
from src.data import generate_random_jssp

scheduler = LLMScheduler()
instance = generate_random_jssp(6, 6, seed=42)

# The LLMScheduler._create_prompt() method controls the prompt
# Edit it to change Gemini's strategy (e.g., "use critical path method")

schedule = scheduler.solve(instance)
print(f"Makespan: {schedule.makespan}")
print(f"Method: {schedule.metadata}")
```

## 🚀 Production Deployment

For production use:

1. **Set up Cloud SQL** for caching results
2. **Implement request queuing** to avoid rate limits
3. **Add monitoring** (cost, latency, success rate)
4. **Use service account** instead of API key
5. **Enable audit logging**

Example production wrapper:

```python
class ProductionGeminiScheduler(LLMScheduler):
    def __init__(self, cache_dir="./cache"):
        super().__init__()
        self.cache_dir = cache_dir
    
    def solve(self, instance):
        # Check cache first
        cache_key = hash(str(instance.to_dict()))
        cached = self._load_cache(cache_key)
        if cached:
            return cached
        
        # Solve with Gemini
        schedule = super().solve(instance)
        
        # Save to cache
        self._save_cache(cache_key, schedule)
        return schedule
```

## 📚 Resources

- [Gemini API Docs](https://ai.google.dev/docs)
- [Gemini Models](https://ai.google.dev/models)
- [Rate Limits & Quotas](https://ai.google.dev/quotas)
- [Python Client Library](https://github.com/google/generative-ai-python)

## ✓ Checklist

- [ ] API key obtained from Google AI Studio
- [ ] `.env` file created with `GEMINI_API_KEY`
- [ ] `google-generativeai` installed (`pip install -r requirements.txt`)
- [ ] Test script runs successfully
- [ ] `main.py` shows Gemini in LLM output
- [ ] Results appear in `results/` directory

## ❓ Need Help?

1. Check [Google AI Studio](https://aistudio.google.com/) for API status
2. Review error messages in terminal
3. Test with smaller instances first
4. Verify internet connection
5. Check [Gemini Issues](https://github.com/google/generative-ai-python/issues)

---

**Status:** ✓ Gemini integration ready  
**Last updated:** 2024-04-28
