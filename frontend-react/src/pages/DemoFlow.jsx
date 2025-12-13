import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const DemoFlow = () => {
    const navigate = useNavigate();

    const styles = {
        container: {
            display: 'flex',
            flexDirection: 'column',
            height: '100vh',
            backgroundColor: '#0f1419',
            color: '#ffffff',
            fontFamily: 'Plus Jakarta Sans, sans-serif',
        },
        header: {
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            borderBottom: '1px solid rgba(6, 182, 212, 0.2)',
            padding: '1.5rem 2rem',
            textAlign: 'center',
        },
        headerTitle: {
            margin: 0,
            fontSize: '1.8rem',
            fontWeight: 'bold',
            color: '#06b6d4',
        },
        headerSubtitle: {
            margin: '0.5rem 0 0 0',
            color: '#a1a1a1',
            fontSize: '0.95rem',
        },
        headerAppId: {
            display: 'block',
            marginTop: '0.5rem',
            fontSize: '0.8rem',
            color: '#06b6d4',
            opacity: 0.7,
        },
        content: {
            flex: 1,
            display: 'grid',
            gridTemplateColumns: '2fr 1fr',
            gap: '1rem',
            padding: '1rem',
            overflow: 'hidden',
        },
        messagesSection: {
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: 'rgba(6, 182, 212, 0.05)',
            border: '1px solid rgba(6, 182, 212, 0.2)',
            borderRadius: '1rem',
            overflow: 'hidden',
        },
        messagesContainer: {
            flex: 1,
            overflowY: 'auto',
            padding: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
        },
        message: {
            padding: '1rem',
            borderRadius: '0.75rem',
            whiteSpace: 'pre-wrap',
            lineHeight: '1.6',
            animation: 'slideIn 0.3s ease',
        },
        userMessage: {
            backgroundColor: '#06b6d4',
            color: '#000',
            alignSelf: 'flex-end',
            maxWidth: '70%',
            borderBottomRightRadius: '0.25rem',
        },
        botMessage: {
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            border: '1px solid rgba(6, 182, 212, 0.2)',
            color: '#ffffff',
            alignSelf: 'flex-start',
            maxWidth: '85%',
            borderBottomLeftRadius: '0.25rem',
        },
        messageTime: {
            fontSize: '0.7rem',
            color: '#a1a1a1',
            marginTop: '0.5rem',
            display: 'block',
        },
        agentPanel: {
            backgroundColor: 'rgba(6, 182, 212, 0.05)',
            border: '1px solid rgba(6, 182, 212, 0.2)',
            borderRadius: '1rem',
            padding: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            overflowY: 'auto',
        },
        agentPanelTitle: {
            fontSize: '1.2rem',
            fontWeight: 'bold',
            color: '#06b6d4',
            margin: 0,
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
        },
        agentsGrid: {
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem',
        },
        agentCard: {
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            border: '1px solid rgba(6, 182, 212, 0.2)',
            borderRadius: '0.75rem',
            padding: '1rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            transition: 'all 0.3s',
        },
        agentCardProcessing: {
            borderColor: '#06b6d4',
            backgroundColor: 'rgba(6, 182, 212, 0.15)',
        },
        agentCardComplete: {
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
        },
        agentName: {
            fontWeight: '600',
            fontSize: '0.9rem',
        },
        agentIndicator: {
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
        },
        spinner: {
            width: '16px',
            height: '16px',
            border: '2px solid rgba(6, 182, 212, 0.3)',
            borderTop: '2px solid #06b6d4',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
        },
        checkmark: {
            color: '#10b981',
            fontSize: '1.2rem',
            fontWeight: 'bold',
        },
        controls: {
            backgroundColor: 'rgba(6, 182, 212, 0.05)',
            borderTop: '1px solid rgba(6, 182, 212, 0.2)',
            padding: '1.5rem 2rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '1rem',
        },
        backButton: {
            backgroundColor: 'transparent',
            border: '2px solid #06b6d4',
            color: '#06b6d4',
            padding: '0.75rem 1.5rem',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            transition: 'all 0.3s',
        },
        startButton: {
            backgroundColor: '#06b6d4',
            color: '#000',
            border: 'none',
            padding: '0.75rem 2rem',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold',
            transition: 'all 0.3s',
        },
        resetButton: {
            backgroundColor: 'rgba(6, 182, 212, 0.2)',
            border: '2px solid #06b6d4',
            color: '#06b6d4',
            padding: '0.75rem 2rem',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold',
            transition: 'all 0.3s',
        },
    };
    const [stage, setStage] = useState('intro');
    const [messages, setMessages] = useState([]);
    const [agentStatus, setAgentStatus] = useState({});
    const [applicationData, setApplicationData] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Initial greeting
    useEffect(() => {
        addMessage('bot', '👋 Welcome to MSN Loan Assistant - Live Demonstration\n\nI will guide you through a complete loan application processing workflow with real AI agents working in parallel.\n\nLet\'s begin with Nithin\'s loan application for ₹30,00,000 over 60 months.');
    }, []);

    const addMessage = (type, text, metadata = {}) => {
        const newMessage = {
            id: `msg-${Date.now()}-${Math.random()}`,
            type,
            text,
            timestamp: new Date(),
            ...metadata
        };
        setMessages(prev => [...prev, newMessage]);
    };

    const startIntakePhase = async () => {
        setStage('intake');
        setIsProcessing(true);

        // Simulate intake conversation
        addMessage('bot', '📋 PHASE 1: INTAKE CONVERSATION\n\nCollecting applicant information...');

        await delay(1000);
        addMessage('bot', '❓ What is your name?');
        await delay(1500);
        addMessage('user', 'Nithin Nair');

        await delay(1000);
        addMessage('bot', '❓ What is your date of birth?');
        await delay(1500);
        addMessage('user', '15-05-1995');

        await delay(1000);
        addMessage('bot', '❓ What is your monthly income?');
        await delay(1500);
        addMessage('user', '₹5,00,000');

        await delay(1000);
        addMessage('bot', '❓ What loan amount do you need?');
        await delay(1500);
        addMessage('user', '₹30,00,000');

        await delay(1000);
        addMessage('bot', '❓ What is your preferred loan duration?');
        await delay(1500);
        addMessage('user', '60 months (5 years)');

        await delay(1000);
        addMessage('bot', '✅ Intake Complete!\n\n📝 Application Created\nApplication ID: APP-45A58F541428');

        setApplicationData({
            id: 'APP-45A58F541428',
            name: 'Nithin Nair',
            dob: '15-05-1995',
            monthlyIncome: 500000,
            loanAmount: 3000000,
            duration: 60
        });

        setIsProcessing(false);
        await delay(1500);

        startVerificationPhase();
    };

    const startVerificationPhase = async () => {
        setStage('verification');
        setIsProcessing(true);

        addMessage('bot', '🔄 PHASE 2: PARALLEL AGENT VERIFICATION\n\nStarting all verification agents simultaneously...');

        await delay(1500);

        // Launch all agents in parallel
        const agents = [
            { name: 'KYC Agent', port: '8002', task: 'PAN Verification', file: 'nithinofPAN.jpeg' },
            { name: 'Face Agent', port: '8003', task: 'Biometric Verification', file: 'nithin3.jpg' },
            { name: 'Payslip Agent', port: '8004', task: 'Income Verification', file: 'payslip_nithin_j.txt' },
            { name: 'Bank Agent', port: '8005', task: 'Account Verification', file: 'bank_transactions_ACC1001.csv' }
        ];

        addMessage('bot', '🚀 Launching agents on parallel execution:\n\n' +
            agents.map((a, i) => `${i + 1}. ${a.name} (Port ${a.port}): ${a.task}`).join('\n'));

        await delay(2000);

        // Simulate parallel execution
        const agentPromises = agents.map((agent, index) =>
            simulateAgentExecution(agent, index * 200)
        );

        await Promise.all(agentPromises);

        await delay(1000);
        startCreditPhase();
    };

    const simulateAgentExecution = async (agent, delayMs) => {
        await delay(delayMs);

        const processingStart = Date.now();

        // Update status to processing
        setAgentStatus(prev => ({
            ...prev,
            [agent.name]: { status: 'processing', progress: 0 }
        }));

        addMessage('bot', `⏳ ${agent.name} started processing...`, {
            agentName: agent.name,
            type: 'agent-start'
        });

        // Simulate processing time (500-800ms)
        const processingTime = 500 + Math.random() * 300;
        await delay(processingTime);

        // Get agent results
        const results = getAgentResult(agent.name);

        // Update status to complete
        setAgentStatus(prev => ({
            ...prev,
            [agent.name]: { status: 'complete', result: results }
        }));

        addMessage('bot', `✅ ${agent.name} VERIFIED\n\n${results.message}`, {
            agentName: agent.name,
            type: 'agent-complete',
            result: results
        });
    };

    const getAgentResult = (agentName) => {
        const results = {
            'KYC Agent': {
                status: '✅ VERIFIED',
                message: '📋 PAN Verification Complete\n\nPAN: AAUPA0055K\nName: Nithin Nair\nStatus: Authentic\nChecksum: Valid ✓\n\n🎯 Identity Confirmed',
                data: { pan: 'AAUPA0055K', authentic: true }
            },
            'Face Agent': {
                status: '✅ VERIFIED',
                message: '👤 Biometric Verification Complete\n\nFace Detection: Liveness Verified ✓\nMatch Score: 98%\nSpoof Check: Passed ✓\nConfidence: High\n\n🎯 Real Person Confirmed',
                data: { liveness: true, matchScore: 0.98 }
            },
            'Payslip Agent': {
                status: '✅ VERIFIED',
                message: '💰 Income Verification Complete\n\nMonthly Salary: ₹5,00,000\nCompany: Microsoft India\nDesignation: Senior Software Engineer\nGross Annual: ₹60,00,000\n\n🎯 Income Verified',
                data: { salary: 500000, company: 'Microsoft India' }
            },
            'Bank Agent': {
                status: '✅ VERIFIED',
                message: '🏦 Bank Statement Analysis Complete\n\nAccount: ACC1001\nCurrent Balance: ₹80,602\nAverage Monthly Inflow: ₹45,000\nCredit Score: 679/900\nDelinquency: None\n\n🎯 Financial Health Good',
                data: { balance: 80602, creditScore: 679 }
            }
        };
        return results[agentName] || { status: 'unknown', message: 'No result' };
    };

    const startCreditPhase = async () => {
        setStage('credit');
        addMessage('bot', '📊 PHASE 3: CREDIT DECISION\n\nAnalyzing all verification results...');

        await delay(2000);

        addMessage('bot', '🧮 Risk Assessment Calculation:\n\n' +
            '• DTI Ratio: 1.8% (Excellent ✓)\n' +
            '• Credit Score: 679 (Good ✓)\n' +
            '• Income Stability: High ✓\n' +
            '• Employment: Verified ✓\n' +
            '• Identity: Confirmed ✓\n' +
            '• Financial Health: Stable ✓\n\n' +
            'Risk Score: 2.1/10 (Very Low Risk) 🟢');

        await delay(2000);

        addMessage('bot', '🎯 LOAN DECISION: APPROVED ✅\n\n' +
            '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n' +
            'Loan Amount: ₹30,00,000\n' +
            'Duration: 60 months\n' +
            'Interest Rate: 7.5% p.a.\n' +
            'Monthly EMI: ₹3,856.24\n' +
            'Total Interest: ₹8,49,888\n' +
            'Total Repayment: ₹30,84,988\n' +
            '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n' +
            '✨ Congratulations! Your loan has been approved!');

        setStage('complete');
        setIsProcessing(false);
    };

    const resetDemo = () => {
        setStage('intro');
        setMessages([]);
        setAgentStatus({});
        setApplicationData(null);
        setIsProcessing(false);
        addMessage('bot', '👋 Welcome to MSN Loan Assistant - Live Demonstration\n\nI will guide you through a complete loan application processing workflow with real AI agents working in parallel.\n\nLet\'s begin with Nithin\'s loan application for ₹30,00,000 over 60 months.');
    };

    return (
        <div style={styles.container}>
            <style>
                {`
                    @keyframes slideIn {
                        from { opacity: 0; transform: translateX(-20px); }
                        to { opacity: 1; transform: translateX(0); }
                    }
                    @keyframes spin {
                        from { transform: rotate(0deg); }
                        to { transform: rotate(360deg); }
                    }
                `}
            </style>

            <div style={styles.header}>
                <h1 style={styles.headerTitle}>💰 MSN Loan Assistant - Live Demo</h1>
                <p style={styles.headerSubtitle}>Complete Loan Processing Workflow</p>
                {applicationData && <small style={styles.headerAppId}>Application ID: {applicationData.id}</small>}
            </div>

            <div style={styles.content}>
                <div style={styles.messagesSection}>
                    <div style={styles.messagesContainer}>
                        {messages.map((msg) => (
                            <div key={msg.id}>
                                <div style={{
                                    ...styles.message,
                                    ...(msg.type === 'user' ? styles.userMessage : styles.botMessage)
                                }}>
                                    {msg.text}
                                    <span style={styles.messageTime}>
                                        {msg.timestamp.toLocaleTimeString()}
                                    </span>
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                </div>

                <div style={styles.agentPanel}>
                    <h3 style={styles.agentPanelTitle}>🤖 Agent Status</h3>
                    <div style={styles.agentsGrid}>
                        {Object.entries(agentStatus).map(([name, status]) => (
                            <div
                                key={name}
                                style={{
                                    ...styles.agentCard,
                                    ...(status.status === 'processing' ? styles.agentCardProcessing : {}),
                                    ...(status.status === 'complete' ? styles.agentCardComplete : {})
                                }}
                            >
                                <div style={styles.agentName}>{name}</div>
                                <div style={styles.agentIndicator}>
                                    {status.status === 'processing' && <div style={styles.spinner}></div>}
                                    {status.status === 'complete' && <span style={styles.checkmark}>✓</span>}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div style={styles.controls}>
                <button
                    style={styles.backButton}
                    onClick={() => navigate('/')}
                    title="Back to Home"
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(6, 182, 212, 0.1)'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                    <ArrowLeft size={18} />
                    Back to Home
                </button>

                {stage === 'intro' && (
                    <button
                        style={styles.startButton}
                        onClick={startIntakePhase}
                        disabled={isProcessing}
                        onMouseEnter={(e) => {
                            if (!isProcessing) e.currentTarget.style.backgroundColor = '#0891b2';
                        }}
                        onMouseLeave={(e) => {
                            if (!isProcessing) e.currentTarget.style.backgroundColor = '#06b6d4';
                        }}
                    >
                        🚀 Start Demo
                    </button>
                )}
                {stage === 'complete' && (
                    <button
                        style={styles.resetButton}
                        onClick={resetDemo}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(6, 182, 212, 0.3)'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'rgba(6, 182, 212, 0.2)'}
                    >
                        🔄 Run Again
                    </button>
                )}
            </div>
        </div>
    );
};

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export default DemoFlow;
