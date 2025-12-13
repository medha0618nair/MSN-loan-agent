// Centralized API client with all endpoints
// All URLs come from .env - never hardcoded

// Build endpoints from env variables
const API_ENDPOINTS = {
    // Intake Agent (Port 8001)
    INTAKE_START: `${process.env.REACT_APP_INTAKE_URL}/start`,
    INTAKE_MESSAGE: `${process.env.REACT_APP_INTAKE_URL}/message`,
    INTAKE_STATE: `${process.env.REACT_APP_INTAKE_URL}/state`,

    // KYC Agent (Port 8002)
    KYC_PARSE: `${process.env.REACT_APP_KYC_URL}/kyc/parse`,
    KYC_HEALTH: `${process.env.REACT_APP_KYC_URL}/health`,

    // Face Agent (Port 8003)
    FACE_VERIFY: `${process.env.REACT_APP_FACE_URL}/face/verify`,
    FACE_HEALTH: `${process.env.REACT_APP_FACE_URL}/health`,

    // Payslip Agent (Port 8004)
    PAYSLIP_VERIFY: `${process.env.REACT_APP_PAYSLIP_URL}/payslip/verify`,
    PAYSLIP_HEALTH: `${process.env.REACT_APP_PAYSLIP_URL}/health`,

    // Bank Agent (Port 8005)
    BANK_PARSE: `${process.env.REACT_APP_BANK_URL}/bank/parse`,
    BANK_HEALTH: `${process.env.REACT_APP_BANK_URL}/health`,

    // Credit Agent (Port 8006)
    CREDIT_SCORE: `${process.env.REACT_APP_CREDIT_URL}/score`,
    CREDIT_HEALTH: `${process.env.REACT_APP_CREDIT_URL}/health`,

    // Orchestrator (Port 9000)
    ORCHESTRATOR_HEALTH: `${process.env.REACT_APP_ORCH_URL}/health`,
    ORCHESTRATOR_ORCHESTRATE: `${process.env.REACT_APP_ORCH_URL}/orchestrate`,
};

const MOCK_MODE = process.env.REACT_APP_MOCK_MODE === 'true';

// Mock response generator (if API fails)
const generateMockResponse = (endpoint) => {
    switch (endpoint) {
        case 'kyc':
            return {
                application_id: `APP-${Math.random().toString(36).substr(2, 9)}`,
                status: 'success',
                data: { confidence: 0.95, doc_type: 'pan' }
            };
        case 'face':
            return {
                similarity: 0.92,
                liveness_score: 0.88,
                match_confidence: 0.90
            };
        case 'payslip':
            return {
                monthly_income: 45000,
                income_confidence: 0.90
            };
        case 'bank':
            return {
                avg_salary: 48000,
                months_salary_detected: 12,
                confidence: 0.92
            };
        case 'credit':
            return {
                pd_score: 0.15,
                risk_tier: 'LOW',
                recommended_action: 'APPROVE',
                max_eligible_loan: 500000
            };
        default:
            return { status: 'success' };
    }
};

/**
 * Start intake conversation
 */
export const startIntakeConversation = async (applicationId = null) => {
    try {
        const response = await fetch(API_ENDPOINTS.INTAKE_START, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ application_id: applicationId }),
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Intake start failed:', error);
        if (MOCK_MODE) {
            return {
                application_id: `APP-${Math.random().toString(36).substr(2, 9)}`,
                bot_message: 'What type of loan do you need? (personal/home/auto/education)',
                current_stage: 'loan_type',
                collected_data: {}
            };
        }
        throw error;
    }
};

/**
 * Send message to intake agent
 */
export const sendToIntakeAgent = async (applicationId, userMessage) => {
    try {
        const response = await fetch(API_ENDPOINTS.INTAKE_MESSAGE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                application_id: applicationId,
                user_message: userMessage,
            }),
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Intake message failed:', error);
        if (MOCK_MODE) {
            return {
                application_id: applicationId,
                bot_message: 'Got it! Next question...',
                current_stage: 'name',
                completed: false,
                collected_data: {}
            };
        }
        throw error;
    }
};

/**
 * Parse KYC document (file upload)
 */
export const parseKYCDocument = async (file, applicationId, evidenceId, docType = 'pan') => {
    try {
        const formData = new FormData();
        formData.append('application_id', applicationId);
        formData.append('evidence_id', evidenceId);
        formData.append('doc_type', docType);
        formData.append('file_path', `/tmp/${file.name}`); // Backend expects file path

        // For actual file upload, you may need to adjust based on backend implementation
        const response = await fetch(API_ENDPOINTS.KYC_PARSE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                application_id: applicationId,
                evidence_id: evidenceId,
                doc_type: docType,
                file_path: `/tmp/${file.name}`
            }),
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('KYC parse failed:', error);
        if (MOCK_MODE) return generateMockResponse('kyc');
        throw error;
    }
};

/**
 * Verify face (file upload)
 */
export const verifyFace = async (idCropFile, selfieFile, applicationId, subjectId) => {
    try {
        const formData = new FormData();
        formData.append('id_crop', idCropFile);
        formData.append('selfie', selfieFile);
        formData.append('application_id', applicationId);
        formData.append('subject_id', subjectId);

        const response = await fetch(API_ENDPOINTS.FACE_VERIFY, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Face verification failed:', error);
        if (MOCK_MODE) return generateMockResponse('face');
        throw error;
    }
};

/**
 * Verify payslip (file upload)
 */
export const verifyPayslip = async (file) => {
    try {
        const formData = new FormData();
        formData.append('payslip_file', file);

        const response = await fetch(API_ENDPOINTS.PAYSLIP_VERIFY, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Payslip verification failed:', error);
        if (MOCK_MODE) return generateMockResponse('payslip');
        throw error;
    }
};

/**
 * Parse bank statement
 */
export const parseBankStatement = async (file, applicationId, evidenceId) => {
    try {
        const formData = new FormData();
        formData.append('application_id', applicationId);
        formData.append('evidence_id', evidenceId);
        formData.append('file_uri', `/tmp/${file.name}`);

        const response = await fetch(API_ENDPOINTS.BANK_PARSE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                application_id: applicationId,
                evidence_id: evidenceId,
                file_uri: `/tmp/${file.name}`
            }),
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Bank parse failed:', error);
        if (MOCK_MODE) return generateMockResponse('bank');
        throw error;
    }
};

/**
 * Get credit score
 */
export const getCreditScore = async (evidenceBundle, loanRequest, applicationId) => {
    try {
        const response = await fetch(API_ENDPOINTS.CREDIT_SCORE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                application_id: applicationId,
                evidence: evidenceBundle,
                loan_request: loanRequest,
                app_metadata: {
                    submission_ts: new Date().toISOString(),
                    source: 'web'
                }
            }),
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Credit score failed:', error);
        if (MOCK_MODE) return generateMockResponse('credit');
        throw error;
    }
};

/**
 * Orchestrate workflow
 */
export const orchestrateWorkflow = async (applicationId, intent, parameters) => {
    try {
        const response = await fetch(API_ENDPOINTS.ORCHESTRATOR_ORCHESTRATE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                application_id: applicationId,
                intent: intent,
                parameters: parameters,
            }),
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Orchestration failed:', error);
        if (MOCK_MODE) return generateMockResponse('orchestrator');
        throw error;
    }
};

export default API_ENDPOINTS;
