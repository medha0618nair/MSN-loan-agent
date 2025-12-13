# Frontend Setup Instructions

## Quick Start (5 minutes)

### Option 1: Automated Setup
```bash
cd frontend-react
chmod +x start.sh
./start.sh
```

### Option 2: Manual Setup
```bash
cd frontend-react
npm install
npm start
```

The app will open at **http://localhost:3000**

## Configuration

All backend URLs are configured in `.env`:

```env
# Backend Service URLs
REACT_APP_INTAKE_URL=http://localhost:8001
REACT_APP_KYC_URL=http://localhost:8002
REACT_APP_FACE_URL=http://localhost:8003
REACT_APP_PAYSLIP_URL=http://localhost:8004
REACT_APP_BANK_URL=http://localhost:8005
REACT_APP_CREDIT_URL=http://localhost:8006
REACT_APP_ORCH_URL=http://localhost:9000

# Mock mode (true = simulate backend responses)
REACT_APP_MOCK_MODE=false
```

## File Structure

```
frontend-react/
├── public/
│   └── index.html                 # HTML template
├── src/
│   ├── api/
│   │   └── client.js              # All API calls
│   ├── components/
│   │   └── Chat.jsx               # Main UI component
│   ├── styles/
│   │   └── Chat.css               # Styling
│   ├── App.jsx                    # Root component
│   ├── index.js                   # React entry point
│   └── index.css                  # Global styles
├── .env                           # Configuration
├── .gitignore
├── package.json                   # Dependencies
├── README.md
├── SETUP.md                       # This file
└── start.sh                       # Start script

```

## Features Implemented

✅ **Chat Interface**
- Bot and user message bubbles
- Auto-scroll to latest message
- Unique message IDs for React keys
- Loading indicator

✅ **File Uploads**
- KYC document upload
- Payslip upload  
- Bank statement upload
- File preview state

✅ **API Integration**
- Centralized API client in `client.js`
- All 7 backend services connected
- Error handling
- Mock mode fallback

✅ **UI/UX**
- Beautiful gradient design (purple theme)
- Responsive layout (mobile + desktop)
- Smooth animations
- Loading states
- Error messages

## API Endpoints Used

| Agent | Endpoint | Method |
|-------|----------|--------|
| Intake | /start | POST |
| Intake | /message | POST |
| KYC | /kyc/parse | POST |
| Face | /face/verify | POST |
| Payslip | /payslip/verify | POST |
| Bank | /bank/parse | POST |
| Credit | /score | POST |
| Orchestrator | /orchestrate | POST |

## Workflow

1. **Initialize**: User clicks chat → frontend calls `/start` → bot asks first question
2. **Conversation**: User answers → `/message` → bot asks next question
3. **Document Upload**: Relevant stage → upload file → `/kyc/parse`, `/payslip/verify`, `/bank/parse`
4. **Decision**: All info collected → `/score` → credit decision displayed

## Development

### Add New Endpoint
1. Add URL to `.env`
2. Create function in `src/api/client.js`
3. Call from `Chat.jsx`

### Modify UI
- Edit `src/components/Chat.jsx`
- Style changes in `src/styles/Chat.css`

### Enable Mock Mode
Set `REACT_APP_MOCK_MODE=true` in `.env`

## Troubleshooting

### "Cannot connect to backend"
- Check if all 7 Docker containers are running
- Verify `.env` URLs are correct
- Check browser console for CORS errors

### "Port 3000 already in use"
```bash
# Kill process on port 3000
lsof -i :3000  # Find PID
kill -9 <PID>

# Or use different port
PORT=3001 npm start
```

### "Module not found"
```bash
rm -rf node_modules
npm install
npm start
```

## Build for Production

```bash
npm run build
```

Creates optimized build in `build/` folder.

## Performance Notes

- Chat messages are efficiently rendered with unique keys
- CSS animations use GPU acceleration
- File uploads show loading state
- Mock mode for testing without backend

## Support

For issues with the backend services, check:
- Docker container logs: `docker-compose logs <service>`
- Backend API status: `curl http://localhost:8001/health`

---

**Happy Lending! 💰**
