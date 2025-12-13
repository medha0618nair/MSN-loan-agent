# MSN Loan Agent Frontend

React frontend for the MSN Loan Agent microservices backend.

## Setup

### 1. Install Dependencies
```bash
cd frontend-react
npm install
```

### 2. Configure Backend URLs
Edit `.env` with your backend service URLs:

```env
REACT_APP_INTAKE_URL=http://localhost:8001
REACT_APP_KYC_URL=http://localhost:8002
REACT_APP_FACE_URL=http://localhost:8003
REACT_APP_PAYSLIP_URL=http://localhost:8004
REACT_APP_BANK_URL=http://localhost:8005
REACT_APP_CREDIT_URL=http://localhost:8006
REACT_APP_ORCH_URL=http://localhost:9000
REACT_APP_MOCK_MODE=false
```

### 3. Start Development Server
```bash
npm start
```

Frontend will open at `http://localhost:3000`

## Features

✅ **Chat Interface** - Conversational loan application
✅ **File Uploads** - KYC, Payslip, Bank Statement uploads
✅ **Real-time Responses** - Connected to all 7 backend microservices
✅ **Mock Mode** - Fallback responses if backend is down
✅ **Beautiful UI** - Modern gradient design with smooth animations
✅ **Responsive Design** - Works on mobile and desktop

## File Structure

```
frontend-react/
├── public/
│   └── index.html
├── src/
│   ├── api/
│   │   └── client.js          # All API endpoints
│   ├── components/
│   │   └── Chat.jsx           # Main chat component
│   ├── styles/
│   │   └── Chat.css           # Chat styling
│   ├── App.jsx
│   ├── index.js
│   └── index.css
├── .env                        # Environment variables
├── package.json
└── README.md
```

## Backend Services

| Service | Port | Endpoint |
|---------|------|----------|
| Intake Agent | 8001 | /start, /message |
| KYC Agent | 8002 | /kyc/parse |
| Face Agent | 8003 | /face/verify |
| Payslip Agent | 8004 | /payslip/verify |
| Bank Agent | 8005 | /bank/parse |
| Credit Agent | 8006 | /score |
| Orchestrator | 9000 | /orchestrate |

## API Client

All API calls are centralized in `src/api/client.js`:

```javascript
// Start conversation
await startIntakeConversation(applicationId);

// Send message
await sendToIntakeAgent(applicationId, userMessage);

// Upload documents
await parseKYCDocument(file, applicationId, evidenceId, docType);
await verifyFace(idCropFile, selfieFile, applicationId, subjectId);
await verifyPayslip(file);
await parseBankStatement(file, applicationId, evidenceId);

// Get credit decision
await getCreditScore(evidenceBundle, loanRequest, applicationId);
```

## Mock Mode

Enable mock mode in `.env` to simulate backend responses:

```env
REACT_APP_MOCK_MODE=true
```

Useful for testing without running backend services.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

Proprietary
