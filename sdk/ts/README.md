# ECaDP TypeScript SDK

TypeScript client for the Ethical Crawler & Data Platform API.

## Installation
```bash
npm install
```

## Usage
```typescript
import { ECaDPClient } from './index';

const client = new ECaDPClient({ apiKey: "YOUR_API_KEY" });

async function main() {
  const job = await client.submitCrawlJob({ startUrl: "http://example.com" });
  console.log(job);
}

main();