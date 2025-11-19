Here’s a README.md you can drop straight into that branch 👇
(You can tweak the backend URL bits once you finalize the Lambda.)

⸻


# AWS Invoice Scanner (Step 1 – Frontend)

AI-powered invoice scanner UI built with **Vue 3 + Vite**.  
This step focuses on the frontend that lets you upload an invoice image and send it to a backend (AWS Lambda + Bedrock Claude) for extraction.

> This is **Step 1** of the series – frontend only. The AWS backend (Lambda / Bedrock) is wired in later steps.

---

## 🧰 Tech Stack

- [Vue 3](https://vuejs.org/)
- [Vite](https://vitejs.dev/)
- JavaScript / TypeScript-ready

---

## ✅ Prerequisites

- **Node.js** 18+ (20+ recommended)
- **npm** (comes with Node) or **pnpm/yarn** if you prefer
- Git (to clone the repo)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/saasscaleup/aws-invoice-scanner.git
cd aws-invoice-scanner
git checkout ais-step-1

2. Install dependencies

Using npm:

npm install

(or)

Using pnpm:

pnpm install


⸻

🏃‍♂️ Run the Dev Server

Start the Vite dev server:

npm run dev

You’ll see output similar to:

  VITE vX.X.X  ready in Xs

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/

Open the Local URL in your browser (usually http://localhost:5173).

⸻

🏗️ Build for Production

To create an optimized production build:

npm run build

This outputs static assets into the dist/ directory.

You can preview the production build locally with:

npm run preview


⸻

🔌 Connecting to Your AWS Backend (Lambda + Bedrock)

In later steps of the project, this frontend will call an AWS Lambda Function URL that:
	•	Accepts a base64-encoded invoice image
	•	Calls Amazon Bedrock (Claude) to extract invoice data
	•	Returns JSON with fields like place, date, and payment

For now (Step 1), you can:
	•	Point the frontend to your own Lambda URL, or
	•	Stub/mock the API endpoint during development

Check the API call in the src directory (e.g. where fetch() or axios is used) and update the URL to match your deployed Lambda endpoint.

⸻

🧹 Useful npm Scripts

Common commands:

npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview built app

(If you use pnpm or yarn, just swap npm with pnpm/yarn.)

⸻

📺 Follow Along With the Tutorial

This repo is part of the AWS Serverless Invoice Scanner YouTube series on the Scale-Up SaaS channel.
Watch Step 1 to see how this frontend was built and how it will connect to AWS in the next steps.

⸻


If you tell me the exact env variable / file you’re using for the Lambda URL (e.g. `VITE_LAMBDA_URL` in `.env`), I can add a short “Environment Variables” section to this too.