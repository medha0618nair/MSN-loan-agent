import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, Shield, Clock, Star, Phone, Mail, MapPin, Send, Sparkles, ArrowRight, Menu, X, CheckCircle } from 'lucide-react';

const LandingPage = () => {
    const navigate = useNavigate();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 50);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const styles = {
        // Container
        mainContainer: {
            width: '100%',
            backgroundColor: '#0f1419',
            color: '#ffffff',
            overflow: 'hidden',
        },

        // Navigation
        nav: {
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            zIndex: 1000,
            backgroundColor: scrolled ? 'rgba(15, 20, 25, 0.8)' : 'transparent',
            backdropFilter: scrolled ? 'blur(10px)' : 'none',
            borderBottom: scrolled ? '1px solid rgba(6, 182, 212, 0.1)' : 'none',
            padding: scrolled ? '0.5rem 0' : '1rem 0',
            transition: 'all 0.3s ease',
        },

        navContainer: {
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '0 2rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
        },

        logo: {
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            cursor: 'pointer',
            fontSize: '1.5rem',
            fontWeight: 'bold',
        },

        logoIcon: {
            width: '32px',
            height: '32px',
            backgroundColor: '#06b6d4',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#000',
            fontWeight: 'bold',
        },

        navLinks: {
            display: 'flex',
            gap: '2rem',
            alignItems: 'center',
        },

        navLink: {
            textDecoration: 'none',
            color: '#a1a1a1',
            transition: 'color 0.3s',
            cursor: 'pointer',
        },

        ctaButton: {
            display: 'flex',
            gap: '1rem',
        },

        button: {
            padding: '0.75rem 1.5rem',
            borderRadius: '0.5rem',
            border: 'none',
            cursor: 'pointer',
            fontWeight: '600',
            transition: 'all 0.3s',
            fontSize: '1rem',
        },

        primaryButton: {
            backgroundColor: '#06b6d4',
            color: '#000',
        },

        secondaryButton: {
            backgroundColor: 'transparent',
            border: '2px solid #06b6d4',
            color: '#06b6d4',
        },

        // Hero Section
        heroSection: {
            position: 'relative',
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
            marginTop: '80px',
        },

        heroBackground: {
            position: 'absolute',
            inset: 0,
            zIndex: 0,
        },

        heroOrb: {
            position: 'absolute',
            borderRadius: '50%',
            filter: 'blur(100px)',
            opacity: 0.15,
        },

        orb1: {
            width: '400px',
            height: '400px',
            backgroundColor: '#06b6d4',
            top: '10%',
            right: '10%',
        },

        orb2: {
            width: '300px',
            height: '300px',
            backgroundColor: '#0891b2',
            bottom: '20%',
            left: '5%',
        },

        orb3: {
            width: '250px',
            height: '250px',
            backgroundColor: '#06b6d4',
            bottom: '10%',
            right: '30%',
        },

        heroContainer: {
            position: 'relative',
            zIndex: 10,
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '0 2rem',
            width: '100%',
        },

        heroGrid: {
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '3rem',
            alignItems: 'center',
        },

        heroLeft: {
            display: 'flex',
            flexDirection: 'column',
            gap: '1.5rem',
        },

        heroBadge: {
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            border: '1px solid rgba(6, 182, 212, 0.3)',
            padding: '0.5rem 1rem',
            borderRadius: '2rem',
            width: 'fit-content',
            color: '#06b6d4',
            fontSize: '0.875rem',
        },

        heroHeadline: {
            fontSize: '3.5rem',
            fontWeight: '800',
            lineHeight: '1.2',
            margin: 0,
        },

        headlineGradient: {
            background: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            display: 'inline',
        },

        heroSubtitle: {
            fontSize: '1.1rem',
            color: '#a1a1a1',
            lineHeight: '1.6',
            margin: 0,
        },

        benefitsGrid: {
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '1rem',
        },

        benefitItem: {
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
        },

        benefitCheck: {
            color: '#06b6d4',
            flexShrink: 0,
        },

        benefitText: {
            fontSize: '0.95rem',
        },

        buttonsGrid: {
            display: 'flex',
            gap: '1rem',
            marginTop: '1rem',
        },

        ctaMain: {
            padding: '1rem 2rem',
            backgroundColor: '#06b6d4',
            color: '#000',
            border: 'none',
            borderRadius: '0.5rem',
            fontSize: '1.1rem',
            fontWeight: 'bold',
            cursor: 'pointer',
            transition: 'all 0.3s',
        },

        ctaSecondary: {
            padding: '1rem 2rem',
            backgroundColor: 'transparent',
            color: '#06b6d4',
            border: '2px solid #06b6d4',
            borderRadius: '0.5rem',
            fontSize: '1.1rem',
            fontWeight: 'bold',
            cursor: 'pointer',
            transition: 'all 0.3s',
        },

        socialProof: {
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            marginTop: '1rem',
        },

        heroRight: {
            position: 'relative',
            height: '500px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
        },

        heroCard: {
            width: '100%',
            height: '400px',
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            border: '1px solid rgba(6, 182, 212, 0.2)',
            borderRadius: '1rem',
            padding: '2rem',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            flexDirection: 'column',
            gap: '1.5rem',
        },

        quickAppHeader: {
            fontSize: '1.5rem',
            fontWeight: 'bold',
        },

        quickAppItem: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            paddingBottom: '1rem',
            borderBottom: '1px solid rgba(6, 182, 212, 0.1)',
        },

        quickAppLabel: {
            color: '#a1a1a1',
        },

        quickAppValue: {
            color: '#06b6d4',
            fontWeight: 'bold',
        },

        // Stats Section
        statsSection: {
            backgroundColor: '#111318',
            padding: '4rem 2rem',
        },

        statsContainer: {
            maxWidth: '1200px',
            margin: '0 auto',
        },

        statsGrid: {
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '2rem',
        },

        statCard: {
            textAlign: 'center',
        },

        statNumber: {
            fontSize: '2.5rem',
            fontWeight: 'bold',
            color: '#06b6d4',
            marginBottom: '0.5rem',
        },

        statLabel: {
            fontSize: '1rem',
            color: '#a1a1a1',
        },

        // Features Section
        featuresSection: {
            padding: '4rem 2rem',
        },

        sectionTitle: {
            fontSize: '2.5rem',
            fontWeight: 'bold',
            textAlign: 'center',
            marginBottom: '3rem',
        },

        featuresGrid: {
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '2rem',
            maxWidth: '1200px',
            margin: '0 auto',
        },

        featureCard: {
            backgroundColor: 'rgba(6, 182, 212, 0.05)',
            border: '1px solid rgba(6, 182, 212, 0.2)',
            borderRadius: '1rem',
            padding: '2rem',
            transition: 'all 0.3s',
        },

        featureIcon: {
            width: '50px',
            height: '50px',
            backgroundColor: 'rgba(6, 182, 212, 0.2)',
            borderRadius: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1rem',
            color: '#06b6d4',
        },

        featureTitle: {
            fontSize: '1.25rem',
            fontWeight: 'bold',
            marginBottom: '0.75rem',
        },

        featureDescription: {
            color: '#a1a1a1',
            fontSize: '0.95rem',
            lineHeight: '1.6',
        },

        // How it Works
        howSection: {
            backgroundColor: '#111318',
            padding: '4rem 2rem',
        },

        stepsGrid: {
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '2rem',
            maxWidth: '1200px',
            margin: '0 auto',
        },

        stepCard: {
            textAlign: 'center',
        },

        stepNumber: {
            width: '50px',
            height: '50px',
            backgroundColor: '#06b6d4',
            color: '#000',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.5rem',
            fontWeight: 'bold',
            margin: '0 auto 1rem',
        },

        stepTitle: {
            fontSize: '1.25rem',
            fontWeight: 'bold',
            marginBottom: '0.75rem',
        },

        stepDescription: {
            color: '#a1a1a1',
            fontSize: '0.95rem',
        },

        // CTA Section
        ctaSection: {
            padding: '4rem 2rem',
            textAlign: 'center',
        },

        ctaSectionContent: {
            maxWidth: '800px',
            margin: '0 auto',
        },

        ctaSectionTitle: {
            fontSize: '2.5rem',
            fontWeight: 'bold',
            marginBottom: '1rem',
        },

        ctaSectionSubtitle: {
            fontSize: '1.1rem',
            color: '#a1a1a1',
            marginBottom: '2rem',
        },

        // Contact Section
        contactSection: {
            backgroundColor: '#111318',
            padding: '4rem 2rem',
        },

        contactGrid: {
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '3rem',
            maxWidth: '1200px',
            margin: '0 auto',
        },

        contactInfo: {
            display: 'flex',
            flexDirection: 'column',
            gap: '2rem',
        },

        contactItem: {
            display: 'flex',
            gap: '1rem',
        },

        contactIcon: {
            color: '#06b6d4',
            flexShrink: 0,
            marginTop: '0.25rem',
        },

        contactForm: {
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
        },

        formInput: {
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            border: '1px solid rgba(6, 182, 212, 0.2)',
            borderRadius: '0.5rem',
            padding: '0.75rem 1rem',
            color: '#fff',
            fontSize: '1rem',
            fontFamily: 'Plus Jakarta Sans, sans-serif',
        },

        formTextarea: {
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            border: '1px solid rgba(6, 182, 212, 0.2)',
            borderRadius: '0.5rem',
            padding: '0.75rem 1rem',
            color: '#fff',
            fontSize: '1rem',
            fontFamily: 'Plus Jakarta Sans, sans-serif',
            minHeight: '120px',
            resize: 'vertical',
        },

        submitButton: {
            backgroundColor: '#06b6d4',
            color: '#000',
            padding: '0.75rem 1.5rem',
            border: 'none',
            borderRadius: '0.5rem',
            fontSize: '1rem',
            fontWeight: 'bold',
            cursor: 'pointer',
            transition: 'all 0.3s',
        },

        // Footer
        footer: {
            backgroundColor: '#0a0d11',
            padding: '3rem 2rem',
            borderTop: '1px solid rgba(6, 182, 212, 0.1)',
        },

        footerContainer: {
            maxWidth: '1200px',
            margin: '0 auto',
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '2rem',
            marginBottom: '2rem',
        },

        footerColumn: {
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
        },

        footerTitle: {
            fontWeight: 'bold',
            marginBottom: '0.5rem',
        },

        footerLink: {
            color: '#a1a1a1',
            textDecoration: 'none',
            fontSize: '0.9rem',
            transition: 'color 0.3s',
            cursor: 'pointer',
        },

        footerBottom: {
            borderTop: '1px solid rgba(6, 182, 212, 0.1)',
            paddingTop: '2rem',
            textAlign: 'center',
            color: '#a1a1a1',
            fontSize: '0.9rem',
        },
    };

    return (
        <div style={styles.mainContainer}>
            {/* Navigation */}
            <nav style={styles.nav}>
                <div style={styles.navContainer}>
                    <div style={styles.logo} onClick={() => navigate('/')}>
                        <div style={styles.logoIcon}>M</div>
                        <span>MSN Loan</span>
                    </div>

                    <div style={styles.navLinks}>
                        <a style={styles.navLink} href="#features">Features</a>
                        <a style={styles.navLink} href="#how">How It Works</a>
                        <a style={styles.navLink} href="#contact">Contact</a>
                    </div>

                    <div style={styles.ctaButton}>
                        <button style={{ ...styles.button, ...styles.primaryButton }} onClick={() => navigate('/chat')}>Chat Agent</button>
                        <button style={{ ...styles.button, ...styles.secondaryButton }} onClick={() => navigate('/demo')}>Watch Demo</button>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section style={styles.heroSection}>
                <div style={styles.heroBackground}>
                    <div style={{ ...styles.heroOrb, ...styles.orb1 }}></div>
                    <div style={{ ...styles.heroOrb, ...styles.orb2 }}></div>
                    <div style={{ ...styles.heroOrb, ...styles.orb3 }}></div>
                </div>

                <div style={styles.heroContainer}>
                    <div style={styles.heroGrid}>
                        <div style={styles.heroLeft}>
                            <div style={styles.heroBadge}>
                                <Sparkles size={16} />
                                AI-Powered Lending Platform
                            </div>
                            <h1 style={styles.heroHeadline}>
                                Get Your Dream Loan
                                <span style={styles.headlineGradient}> Approved in Minutes</span>
                            </h1>
                            <p style={styles.heroSubtitle}>
                                Experience the future of lending with our AI-powered platform. Fast, secure, and transparent loan approvals without the hassle.
                            </p>

                            <div style={styles.benefitsGrid}>
                                <div style={styles.benefitItem}>
                                    <div style={styles.benefitCheck}><CheckCircle size={16} /></div>
                                    <span style={styles.benefitText}>Instant Pre-Approval</span>
                                </div>
                                <div style={styles.benefitItem}>
                                    <div style={styles.benefitCheck}><CheckCircle size={16} /></div>
                                    <span style={styles.benefitText}>Bank-Grade Security</span>
                                </div>
                                <div style={styles.benefitItem}>
                                    <div style={styles.benefitCheck}><CheckCircle size={16} /></div>
                                    <span style={styles.benefitText}>24/7 Support</span>
                                </div>
                                <div style={styles.benefitItem}>
                                    <div style={styles.benefitCheck}><CheckCircle size={16} /></div>
                                    <span style={styles.benefitText}>Transparent Pricing</span>
                                </div>
                            </div>

                            <div style={styles.buttonsGrid}>
                                <button style={styles.ctaMain} onClick={() => navigate('/chat')}>Get Started Free</button>
                                <button style={styles.ctaSecondary} onClick={() => navigate('/demo')}>Watch Demo</button>
                            </div>

                            <div style={styles.socialProof}>
                                <div>⭐⭐⭐⭐⭐</div>
                                <span style={{ color: '#a1a1a1' }}>Trusted by 50,000+ customers</span>
                            </div>
                        </div>

                        <div style={styles.heroRight}>
                            <div style={styles.heroCard}>
                                <div style={styles.quickAppHeader}>Quick Application</div>
                                <div style={styles.quickAppItem}>
                                    <span style={styles.quickAppLabel}>Loan Amount</span>
                                    <span style={styles.quickAppValue}>₹500,000</span>
                                </div>
                                <div style={styles.quickAppItem}>
                                    <span style={styles.quickAppLabel}>Interest Rate</span>
                                    <span style={styles.quickAppValue}>5.5% p.a.</span>
                                </div>
                                <div style={styles.quickAppItem}>
                                    <span style={styles.quickAppLabel}>Approval Time</span>
                                    <span style={styles.quickAppValue}>15 minutes</span>
                                </div>
                                <div style={styles.quickAppItem}>
                                    <span style={styles.quickAppLabel}>Processing Fee</span>
                                    <span style={styles.quickAppValue}>0%</span>
                                </div>
                                <button style={styles.ctaMain} onClick={() => navigate('/chat')}>
                                    Apply Now
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section style={styles.statsSection}>
                <div style={styles.statsContainer}>
                    <div style={styles.statsGrid}>
                        <div style={styles.statCard}>
                            <div style={styles.statNumber}>50K+</div>
                            <div style={styles.statLabel}>Happy Customers</div>
                        </div>
                        <div style={styles.statCard}>
                            <div style={styles.statNumber}>₹1000Cr+</div>
                            <div style={styles.statLabel}>Total Disbursed</div>
                        </div>
                        <div style={styles.statCard}>
                            <div style={styles.statNumber}>99.9%</div>
                            <div style={styles.statLabel}>Uptime</div>
                        </div>
                        <div style={styles.statCard}>
                            <div style={styles.statNumber}>4.9/5</div>
                            <div style={styles.statLabel}>Average Rating</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section style={styles.featuresSection} id="features">
                <h2 style={styles.sectionTitle}>Why Choose MSN Loan?</h2>
                <div style={styles.featuresGrid}>
                    <div style={styles.featureCard} onMouseEnter={(e) => e.currentTarget.style.borderColor = '#06b6d4'} onMouseLeave={(e) => e.currentTarget.style.borderColor = 'rgba(6, 182, 212, 0.2)'}>
                        <div style={styles.featureIcon}>
                            <Zap size={24} />
                        </div>
                        <h3 style={styles.featureTitle}>Lightning Fast</h3>
                        <p style={styles.featureDescription}>Get loan decisions in minutes, not days. Our AI processes your application instantly.</p>
                    </div>

                    <div style={styles.featureCard} onMouseEnter={(e) => e.currentTarget.style.borderColor = '#06b6d4'} onMouseLeave={(e) => e.currentTarget.style.borderColor = 'rgba(6, 182, 212, 0.2)'}>
                        <div style={styles.featureIcon}>
                            <Shield size={24} />
                        </div>
                        <h3 style={styles.featureTitle}>Bank-Grade Security</h3>
                        <p style={styles.featureDescription}>Military-grade encryption protects your sensitive financial data 24/7.</p>
                    </div>

                    <div style={styles.featureCard} onMouseEnter={(e) => e.currentTarget.style.borderColor = '#06b6d4'} onMouseLeave={(e) => e.currentTarget.style.borderColor = 'rgba(6, 182, 212, 0.2)'}>
                        <div style={styles.featureIcon}>
                            <Clock size={24} />
                        </div>
                        <h3 style={styles.featureTitle}>24/7 Support</h3>
                        <p style={styles.featureDescription}>Our AI chatbot and human agents are always available to help you.</p>
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section style={styles.howSection} id="how">
                <h2 style={styles.sectionTitle}>How It Works</h2>
                <div style={styles.stepsGrid}>
                    <div style={styles.stepCard}>
                        <div style={styles.stepNumber}>1</div>
                        <h3 style={styles.stepTitle}>Apply</h3>
                        <p style={styles.stepDescription}>Fill out a simple online form with your basic information.</p>
                    </div>

                    <div style={styles.stepCard}>
                        <div style={styles.stepNumber}>2</div>
                        <h3 style={styles.stepTitle}>Verify</h3>
                        <p style={styles.stepDescription}>Our AI verifies your information securely and instantly.</p>
                    </div>

                    <div style={styles.stepCard}>
                        <div style={styles.stepNumber}>3</div>
                        <h3 style={styles.stepTitle}>Receive</h3>
                        <p style={styles.stepDescription}>Get approved and receive funds directly to your account.</p>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section style={styles.ctaSection}>
                <div style={styles.ctaSectionContent}>
                    <h2 style={styles.ctaSectionTitle}>Ready to Get Started?</h2>
                    <p style={styles.ctaSectionSubtitle}>Join thousands of customers who've found financial freedom with MSN Loan</p>
                    <button style={styles.ctaMain} onClick={() => navigate('/chat')}>Apply Now</button>
                </div>
            </section>

            {/* Contact Section */}
            <section style={styles.contactSection} id="contact">
                <h2 style={styles.sectionTitle}>Get In Touch</h2>
                <div style={styles.contactGrid}>
                    <div style={styles.contactInfo}>
                        <div style={styles.contactItem}>
                            <Phone style={styles.contactIcon} size={24} />
                            <div>
                                <h4 style={{ margin: '0 0 0.5rem 0' }}>Phone</h4>
                                <p style={{ margin: 0, color: '#a1a1a1' }}>+91 1234 567 890</p>
                            </div>
                        </div>

                        <div style={styles.contactItem}>
                            <Mail style={styles.contactIcon} size={24} />
                            <div>
                                <h4 style={{ margin: '0 0 0.5rem 0' }}>Email</h4>
                                <p style={{ margin: 0, color: '#a1a1a1' }}>support@msnloan.com</p>
                            </div>
                        </div>

                        <div style={styles.contactItem}>
                            <MapPin style={styles.contactIcon} size={24} />
                            <div>
                                <h4 style={{ margin: '0 0 0.5rem 0' }}>Address</h4>
                                <p style={{ margin: 0, color: '#a1a1a1' }}>123 Finance Street, Mumbai, India</p>
                            </div>
                        </div>
                    </div>

                    <form style={styles.contactForm}>
                        <input style={styles.formInput} type="text" placeholder="Your Name" />
                        <input style={styles.formInput} type="email" placeholder="Your Email" />
                        <input style={styles.formInput} type="text" placeholder="Subject" />
                        <textarea style={styles.formTextarea} placeholder="Your Message"></textarea>
                        <button type="submit" style={styles.submitButton}>Send Message</button>
                    </form>
                </div>
            </section>

            {/* Footer */}
            <footer style={styles.footer}>
                <div style={styles.footerContainer}>
                    <div style={styles.footerColumn}>
                        <div style={styles.footerTitle}>Product</div>
                        <a style={styles.footerLink} href="#features">Features</a>
                        <a style={styles.footerLink} href="#how">How It Works</a>
                        <a style={styles.footerLink} href="#">Pricing</a>
                    </div>

                    <div style={styles.footerColumn}>
                        <div style={styles.footerTitle}>Company</div>
                        <a style={styles.footerLink} href="#">About Us</a>
                        <a style={styles.footerLink} href="#">Blog</a>
                        <a style={styles.footerLink} href="#">Careers</a>
                    </div>

                    <div style={styles.footerColumn}>
                        <div style={styles.footerTitle}>Legal</div>
                        <a style={styles.footerLink} href="#">Privacy Policy</a>
                        <a style={styles.footerLink} href="#">Terms of Service</a>
                        <a style={styles.footerLink} href="#">Contact</a>
                    </div>

                    <div style={styles.footerColumn}>
                        <div style={styles.footerTitle}>Follow Us</div>
                        <a style={styles.footerLink} href="#">Twitter</a>
                        <a style={styles.footerLink} href="#">LinkedIn</a>
                        <a style={styles.footerLink} href="#">Facebook</a>
                    </div>
                </div>

                <div style={styles.footerBottom}>
                    <p>&copy; 2025 MSN Loan. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
