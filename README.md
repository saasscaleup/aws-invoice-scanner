# AWS Invoice Scanner — Step 1 (Frontend)

AI-powered invoice scanner UI built with Vue 3 and Vite.  
In this step, you build the frontend that uploads an invoice image and sends it to an AWS backend (Lambda + Bedrock Claude) for extraction.

> This is Step 1 of the full serverless project.  
> The AWS backend integration is added in later steps.

---

## Tech Stack

- Vue 3
- Vite
- JavaScript (TypeScript-ready)

---

## Prerequisites

Make sure you have:

- Node.js 18+ (20+ recommended)
- npm, pnpm, or yarn
- Git

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/saasscaleup/aws-invoice-scanner.git
cd aws-invoice-scanner
git checkout ais-step-1
```

### 2. Install dependencies

Using npm:

```bash
npm install
```

Or using pnpm:

```bash
pnpm install
```

---

## Running the Development Server

Start the Vite dev server:

```bash
npm run dev
```

You should see output similar to:

```text
VITE vX.X.X  ready in Xs
➜  Local:   http://localhost:5173/
➜  Network: http://192.168.x.x:5173/
```

Open the local URL (usually `http://localhost:5173/`) in your browser.

---

## Building for Production

Create an optimized production build:

```bash
npm run build
```

This generates static files in the `dist/` folder.

Preview the production build locally:

```bash
npm run preview
```

---

## Connecting to the AWS Backend (Later Steps)

This frontend is designed to send invoice images to an AWS Lambda Function URL that:

- Accepts a base64-encoded invoice image
- Sends it to Amazon Bedrock (Claude) for extraction
- Returns structured JSON fields, for example:

```json
{
  "place": "Vendor Name",
  "date": "2025-01-10",
  "payment": 42.75,
  "currency": "USD"
}
```

In the frontend code, update the API endpoint to match your deployed Lambda URL.  
If you use environment variables, create a `.env` file:

```env
VITE_LAMBDA_URL=https://your-lambda-url.aws
```

And in your code, reference:

```js
const apiUrl = import.meta.env.VITE_LAMBDA_URL;
```

---

## NPM Script Reference

| Command           | Description                  |
|-------------------|------------------------------|
| `npm run dev`     | Run the development server   |
| `npm run build`   | Build for production         |
| `npm run preview` | Preview the production build |

(Replace `npm` with `pnpm` or `yarn` if you prefer.)

---

## YouTube Series

This repository is part of the "AWS Serverless Invoice Scanner" YouTube series on the ScaleUp SaaS channel.

Step 1 covers building this frontend UI.  
Future steps add:

- AWS Lambda
- Bedrock Claude extraction
- S3 uploads
- DynamoDB storage
- Full end-to-end invoice parsing pipeline

---

## License

This project is licensed under the MIT License.

## Support 🙏😃
  
 If you Like the tutorial and you want to support my channel so I will keep releasing amzing content that will turn you to a desirable Developer with Amazing Cloud skills... I will realy appricite if you:
 
 1. Subscribe to My youtube channel and leave a comment: http://www.youtube.com/@ScaleUpSaaS?sub_confirmation=1
 2. Buy me A coffee ❤️ : https://www.buymeacoffee.com/scaleupsaas

Thanks for your support :)
