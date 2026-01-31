# 🚀 JobBoard API

**Free, open-source job aggregation API** - fetch jobs from RemoteOK, HN Who's Hiring, Greenhouse, Lever, and more.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/jobboard-api)

---

## ⚡ Quick Deploy (GitHub + Vercel)

### Step 1: Push to GitHub

```bash
# Create a new repo on GitHub, then:
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/jobboard-api.git
git push -u origin main
```

### Step 2: Deploy to Vercel (FREE)

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "New Project"
3. Import your `jobboard-api` repository
4. Click "Deploy"
5. Your API is live at `https://jobboard-api-xxx.vercel.app`

**That's it!** Your API is now live and free.

---

## 📡 API Endpoints

### Base URL
```
https://your-project.vercel.app
```

### GET `/api/jobs`

Fetch and search jobs from all sources.

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query (title, company, description, skills) |
| `remote` | boolean | Filter remote jobs only |
| `location` | string | Filter by location |
| `minSalary` | number | Minimum salary filter |
| `skills` | string | Comma-separated skills (e.g., `react,python`) |
| `source` | string | Filter by source (`remoteok`, `hn-hiring`) |
| `limit` | number | Max results (default: 100) |

**Example:**
```bash
curl "https://your-api.vercel.app/api/jobs?q=react&remote=true&minSalary=100000"
```

**Response:**
```json
{
  "success": true,
  "count": 42,
  "jobs": [
    {
      "id": "abc123",
      "title": "Senior Frontend Engineer",
      "company": "TechCorp",
      "location": "Remote",
      "remote": true,
      "salaryMin": 120000,
      "salaryMax": 180000,
      "skills": ["react", "typescript", "node"],
      "applyUrl": "https://...",
      "source": "remoteok",
      "postedAt": "2024-01-15T..."
    }
  ]
}
```

### GET `/api/skills`

Extract skills from text or match candidate skills to job.

**Extract skills:**
```bash
curl "https://your-api.vercel.app/api/skills?text=Looking for React and Python developer&categorize=true"
```

**Match skills:**
```bash
curl "https://your-api.vercel.app/api/skills?candidate=react,python,aws&job=react,node,docker"
```

**Response (match):**
```json
{
  "success": true,
  "mode": "match",
  "score": 33,
  "matched": ["react"],
  "missing": ["node", "docker"]
}
```

---

## 🔧 Local Development

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/jobboard-api.git
cd jobboard-api

# Install dependencies
npm install

# Run locally
npm run dev

# API available at http://localhost:3000
```

---

## 📦 Project Structure

```
jobboard-api/
├── api/
│   ├── index.js        # Health check & API info
│   ├── jobs.js         # Main jobs endpoint
│   └── skills.js       # Skills extraction endpoint
├── src/
│   ├── index.js        # Core SDK (Job, JobAdapter, JobAggregator)
│   ├── adapters/
│   │   ├── remoteok.js
│   │   ├── hn-hiring.js
│   │   └── ats.js      # Greenhouse & Lever
│   └── utils/
│       └── skills.js   # Skills extraction utilities
├── package.json
├── vercel.json
└── README.md
```

---

## 🔌 Adding More Sources

### Add a Company's Greenhouse Board

Edit `api/jobs.js`:

```javascript
// Uncomment and customize:
aggregator.registerAdapter(new GreenhouseAdapter({ boardToken: 'stripe' }));
aggregator.registerAdapter(new GreenhouseAdapter({ boardToken: 'airbnb' }));
```

### Add a Company's Lever Board

```javascript
aggregator.registerAdapter(new LeverAdapter({ companySlug: 'figma' }));
aggregator.registerAdapter(new LeverAdapter({ companySlug: 'netflix' }));
```

### Create Custom Adapter

```javascript
import { JobAdapter, Job } from '../src/index.js';

class MyAdapter extends JobAdapter {
  constructor() {
    super('my-source');
  }

  async fetchJobs() {
    const response = await fetch('https://api.example.com/jobs');
    const data = await response.json();
    return data.map(item => new Job({
      title: item.job_title,
      company: item.company_name,
      // ... map other fields
      source: 'my-source'
    }));
  }
}
```

---

## 🌐 Alternative Hosting Options

### Railway (Also Free)

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### Render (Free Tier)

1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repo
4. Deploy

### Self-Hosted (VPS)

```bash
# On your server
git clone https://github.com/YOUR_USERNAME/jobboard-api.git
cd jobboard-api
npm install
npm start  # Runs on port 3000
```

---

## 📊 Job Schema

Every job is normalized to this format:

```typescript
interface Job {
  id: string;
  title: string;
  company: string;
  location: string | null;
  remote: boolean;
  remoteType: 'full' | 'hybrid' | 'occasional' | null;
  salaryMin: number | null;
  salaryMax: number | null;
  salaryCurrency: string;
  salaryPeriod: 'hour' | 'month' | 'year';
  description: string;
  requirements: string[];
  skills: string[];
  experienceLevel: 'entry' | 'mid' | 'senior' | 'lead' | 'executive' | null;
  employmentType: 'full-time' | 'part-time' | 'contract' | 'internship';
  postedAt: string; // ISO date
  expiresAt: string | null;
  applyUrl: string | null;
  source: string;
  sourceId: string | null;
}
```

---

## 🤝 Contributing

PRs welcome! Ideas:

- [ ] More adapters (Indeed, LinkedIn, Glassdoor)
- [ ] Better NLP for skills extraction
- [ ] Salary estimation when not provided
- [ ] Company enrichment (size, funding, reviews)
- [ ] Redis caching layer
- [ ] Rate limiting

---

## 📄 License

MIT © Your Name

---

<p align="center">
  <strong>Built for developers who want job data without the hassle.</strong>
</p>
