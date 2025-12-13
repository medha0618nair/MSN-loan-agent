#!/usr/bin/env python3
"""
KYC Agent - Test Real OCR Processing
Shows what actually comes from OCR vs test mock data
"""

import subprocess
import sys
import os

print("\n" + "="*100)
print("🔍 KYC AGENT - REAL OCR PROCESSING TEST")
print("="*100)

# Check if Tesseract is installed
print("\n1️⃣  CHECKING TESSERACT OCR INSTALLATION")
print("-" * 100)

try:
    result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("✅ Tesseract OCR is INSTALLED")
        print(f"   Version: {result.stdout.split(chr(10))[0]}")
    else:
        print("❌ Tesseract OCR is NOT properly installed")
        print("   KYC Agent will return ZERO confidence for image OCR")
except FileNotFoundError:
    print("❌ Tesseract OCR NOT FOUND")
    print("   Install with: brew install tesseract")
    print("   KYC Agent cannot perform real image OCR")
except Exception as e:
    print(f"❌ Error checking Tesseract: {e}")

# Check if pytesseract is available
print("\n2️⃣  CHECKING PYTHON OCR LIBRARIES")
print("-" * 100)

try:
    import pytesseract
    print("✅ pytesseract is installed")
except ImportError:
    print("❌ pytesseract is NOT installed")
    print("   Install with: pip install pytesseract")

try:
    from PIL import Image
    print("✅ PIL/Pillow is installed")
except ImportError:
    print("❌ PIL/Pillow is NOT installed")
    print("   Install with: pip install Pillow")

try:
    import pdfplumber
    print("✅ pdfplumber is installed")
except ImportError:
    print("❌ pdfplumber is NOT installed")
    print("   Install with: pip install pdfplumber")

# Test actual OCR on PAN image
print("\n3️⃣  TESTING ACTUAL OCR ON PAN IMAGE")
print("-" * 100)

pan_file = "./images/nithinPAN.png"

if os.path.exists(pan_file):
    print(f"✅ PAN file exists: {pan_file}")
    print(f"   File size: {os.path.getsize(pan_file)} bytes")
    
    try:
        import pytesseract
        from PIL import Image
        
        # Open and read the image
        image = Image.open(pan_file)
        print(f"   Image size: {image.size}")
        print(f"   Image mode: {image.mode}")
        
        # Get OCR text
        print("\n   Running Tesseract OCR...")
        text = pytesseract.image_to_string(image)
        
        if text.strip():
            print(f"\n✅ OCR SUCCESSFULLY EXTRACTED TEXT:")
            print("   " + "-"*96)
            
            # Show first 1000 chars
            print(text[:1000])
            if len(text) > 1000:
                print(f"\n   ... (Total {len(text)} characters)")
            
            print("   " + "-"*96)
            
            # Check for PAN pattern
            import re
            pan_pattern = re.compile(r'[A-Z]{5}[0-9]{4}[A-Z]{1}')
            pan_matches = pan_pattern.findall(text)
            
            if pan_matches:
                print(f"\n✅ PAN NUMBER FOUND: {pan_matches}")
            else:
                print(f"\n❌ PAN NUMBER NOT FOUND in OCR text")
                print("   (May need image enhancement or format verification)")
            
            # Check for name
            name_keywords = ['name', 'नाम', 'nom']
            has_name = any(kw.lower() in text.lower() for kw in name_keywords)
            if has_name:
                print(f"✅ NAME FIELD DETECTED in OCR text")
            else:
                print(f"❌ NAME FIELD NOT clearly detected")
        else:
            print("\n❌ OCR returned NO TEXT")
            print("   Image may be:")
            print("   • Blurry or low quality")
            print("   • Not a real PAN document")
            print("   • Needs image preprocessing")
    
    except ImportError as e:
        print(f"\n⚠️  Cannot test OCR: {e}")
        print("   Install required: pip install pytesseract Pillow")
    except Exception as e:
        print(f"\n❌ OCR Error: {e}")
        print(f"   Type: {type(e).__name__}")
else:
    print(f"❌ PAN file NOT found: {pan_file}")

# Summary
print("\n\n" + "="*100)
print("📋 KYC AGENT CAPABILITIES SUMMARY")
print("="*100)

summary = """
REAL KYC AGENT ARCHITECTURE:
───────────────────────────────────────────────────────────────────────────
1. RECEIVES: PAN image file path (./images/nithinPAN.png)
2. PROCESSES: 
   ✓ If Tesseract installed: Real OCR extraction
   ✗ If Tesseract NOT installed: Returns 0.0 confidence, empty results
3. EXTRACTS:
   ✓ PAN number (pattern: AAAAN1234K)
   ✓ Name from document
   ✓ Contact info (if visible)
   ✓ Confidence score (0.0 - 1.0)
4. RETURNS: Structured data with actual extracted values

CURRENT ISSUES DETECTED:
───────────────────────────────────────────────────────────────────────────
❌ TEST SCRIPT SHOWING MOCK DATA:
   The test is showing hardcoded results like:
   • "name": "Nithin Nair"  ← HARDCODED, not from image
   • "pan": "AAAAN1234K"    ← HARDCODED, not from OCR
   
✅ REAL KYC AGENT SHOULD:
   • Read actual image file
   • Run Tesseract OCR
   • Extract real text from image
   • Return what was actually found
   
⚠️  If your PAN image is:
   • A placeholder/test image (not real PAN)
   • Low quality/blurry
   • In an unsupported format
   Then OCR may fail and return empty results

VERIFICATION STEPS:
───────────────────────────────────────────────────────────────────────────
1. Install Tesseract: brew install tesseract
2. Test image: file ./images/nithinPAN.png
3. Verify image quality: Is it a real/readable PAN?
4. Run KYC agent on actual image
5. Check returned confidence and extracted data

RECOMMENDATION:
───────────────────────────────────────────────────────────────────────────
The KYC agent IS programmed correctly to do real OCR, but:
• You need Tesseract installed for it to work
• Your PAN image needs to be clear and readable
• The test script should call the actual agent endpoint, not mock data
"""

print(summary)
print("="*100 + "\n")
