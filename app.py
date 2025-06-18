from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import shutil
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import pdf2image
import PyPDF2
import cv2
import numpy as np
from datetime import datetime
import re

# Configuration for Windows paths
# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Poppler path for pdf2image
poppler_path = r'C:\Users\Mathias\Anaconda3\Library\bin'

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
TEMP_FOLDER = 'temp'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Process the file
            extracted_text = process_file(filepath)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'text': extracted_text,
                'filename': file.filename
            })
        else:
            return jsonify({'error': 'File type not allowed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_file(filepath):
    """Process uploaded file and extract text"""
    try:
        file_ext = filepath.rsplit('.', 1)[1].lower()
        
        if file_ext == 'pdf':
            return extract_text_from_pdf(filepath)
        else:
            return extract_text_from_image(filepath)
            
    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        # First try to extract text directly from PDF
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text.strip():
                    text += page_text + "\n\n"
            
            # If we got meaningful text, return it
            if len(text.strip()) > 50:  # Threshold for meaningful text
                return clean_extracted_text(text.strip())
        
        # If no text or very little text, treat as scanned PDF
        return extract_text_from_scanned_pdf(pdf_path)
        
    except Exception as e:
        # Fallback to OCR
        return extract_text_from_scanned_pdf(pdf_path)

def extract_text_from_scanned_pdf(pdf_path):
    """Extract text from scanned PDF using optimized OCR"""
    try:
        # Convert PDF pages to images with optimized DPI for speed
        pages = pdf2image.convert_from_path(
            pdf_path, 
            dpi=220,  # Optimized DPI: faster than 300, better quality than 150
            poppler_path=poppler_path,
            fmt='jpeg',  # JPEG is faster to process than PNG
            jpegopt={'quality': 85, 'progressive': True}  # Optimized JPEG settings
        )
        
        extracted_text = ""
        for i, page in enumerate(pages):
            # Save page as temporary image with optimized format
            temp_image_path = os.path.join(TEMP_FOLDER, f"temp_page_{i}.jpg")
            page.save(temp_image_path, 'JPEG', quality=85, optimize=True)
            
            # Extract text from image
            page_text = extract_text_from_image(temp_image_path)
            if page_text.strip():
                extracted_text += f"--- Page {i+1} ---\n{page_text}\n\n"
            
            # Clean up temp image
            os.remove(temp_image_path)
        
        return extracted_text.strip()
        
    except Exception as e:
        raise Exception(f"Error processing scanned PDF: {str(e)}")

def extract_text_from_image(image_path):
    """Extract text from image using optimized OCR"""
    try:
        # Load image with optimized method
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if image is None:
            # Try with PIL if OpenCV fails
            pil_image = Image.open(image_path)
            # Convert to RGB first for consistency
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Quick image size optimization for speed
        height, width = image.shape[:2]
        if height > 2000 or width > 2000:
            # Resize large images to reasonable size for faster processing
            scale = min(2000/height, 2000/width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Advanced multi-stage preprocessing and OCR
        text = advanced_image_to_text(image)
        
        return clean_extracted_text(text)
        
    except Exception as e:
        raise Exception(f"Error extracting text from image: {str(e)}")

def smart_ocr_extraction(pil_image):
    """Advanced multi-pass OCR with result fusion for maximum accuracy"""
    try:
        # Multiple OCR strategies with different configurations
        strategies = [
            {
                'name': 'fast_standard',
                'config': r'--oem 1 --psm 6 -l eng+spa -c tessedit_do_invert=0',
                'weight': 1.0
            },
            {
                'name': 'thorough_page',
                'config': r'--oem 1 --psm 3 -l eng+spa -c tessedit_do_invert=0',
                'weight': 1.2
            },
            {
                'name': 'single_column',
                'config': r'--oem 1 --psm 4 -l eng+spa -c tessedit_do_invert=0',
                'weight': 1.1
            },
            {
                'name': 'single_block',
                'config': r'--oem 1 --psm 8 -l eng+spa -c tessedit_do_invert=0',
                'weight': 0.9
            }
        ]
        
        results = []
        
        # Try each strategy
        for strategy in strategies:
            try:
                text = pytesseract.image_to_string(pil_image, config=strategy['config'])
                if text.strip():
                    quality_score = calculate_text_quality(text)
                    weighted_score = quality_score * strategy['weight']
                    results.append({
                        'text': text,
                        'score': weighted_score,
                        'strategy': strategy['name']
                    })
            except:
                continue
        
        # If no results, try with different preprocessing
        if not results:
            return fallback_ocr_extraction(pil_image)
        
        # Sort by score and return the best result
        results.sort(key=lambda x: x['score'], reverse=True)
        best_result = results[0]
        
        # If the best result is still poor, try combining approaches
        if best_result['score'] < 0.7 and len(results) > 1:
            return combine_ocr_results(results[:2])
        
        return best_result['text']
        
    except Exception:
        return fallback_ocr_extraction(pil_image)

def calculate_text_quality(text):
    """Calculate quality score for OCR result"""
    if not text or len(text.strip()) < 5:
        return 0.0
    
    # Multiple quality metrics
    words = text.split()
    if not words:
        return 0.0
    
    # 1. Letter to total character ratio
    letters = sum(c.isalpha() for c in text)
    total_chars = len([c for c in text if not c.isspace()])
    letter_ratio = letters / max(total_chars, 1)
    
    # 2. Average word length (reasonable words are 3-12 chars)
    avg_word_length = sum(len(word) for word in words) / len(words)
    length_score = 1.0 if 3 <= avg_word_length <= 12 else 0.5
    
    # 3. Ratio of valid words (containing mostly letters)
    valid_words = sum(1 for word in words if len(word) > 1 and sum(c.isalpha() for c in word) / len(word) > 0.6)
    word_ratio = valid_words / len(words)
    
    # 4. Presence of common words/patterns
    common_patterns = ['the', 'and', 'or', 'a', 'an', 'to', 'of', 'in', 'for', 'el', 'la', 'de', 'y', 'en']
    pattern_score = min(1.0, sum(1 for pattern in common_patterns if pattern.lower() in text.lower()) / 5)
    
    # Combine scores
    quality_score = (
        letter_ratio * 0.3 +
        length_score * 0.2 +
        word_ratio * 0.3 +
        pattern_score * 0.2
    )
    
    return min(1.0, quality_score)

def combine_ocr_results(results):
    """Combine multiple OCR results for better accuracy"""
    if len(results) < 2:
        return results[0]['text'] if results else ""
    
    # Simple combination: use the longer result if scores are close
    result1, result2 = results[0], results[1]
    
    if abs(result1['score'] - result2['score']) < 0.2:
        # Scores are close, prefer longer text
        if len(result2['text']) > len(result1['text']) * 1.2:
            return result2['text']
    
    return result1['text']

def advanced_image_to_text(image):
    """Advanced multi-preprocessing approach for maximum accuracy"""
    preprocessing_methods = [
        ('standard', preprocess_image),
        ('aggressive', aggressive_preprocess),
        ('gentle', gentle_preprocess)
    ]
    
    best_result = ""
    best_score = 0.0
    
    for method_name, preprocess_func in preprocessing_methods:
        try:
            # Apply preprocessing
            processed_image = preprocess_func(image)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(processed_image)
            
            # Detect and correct orientation
            pil_image = detect_and_correct_orientation(pil_image)
            
            # Apply OCR
            text = smart_ocr_extraction(pil_image)
            
            if text.strip():
                score = calculate_text_quality(text)
                
                # Bonus for longer text (within reason)
                length_bonus = min(0.2, len(text.strip()) / 1000)
                total_score = score + length_bonus
                
                if total_score > best_score:
                    best_result = text
                    best_score = total_score
                    
                # If we get a very good result, no need to try other methods
                if total_score > 0.9:
                    break
                    
        except Exception:
            continue
    
    return best_result

def fallback_ocr_extraction(pil_image):
    """Fallback OCR extraction with basic configuration"""
    try:
        config_simple = r'--oem 1 --psm 6 -l eng+spa'
        return pytesseract.image_to_string(pil_image, config=config_simple)
    except:
        return ""







def aggressive_preprocess(image):
    """Aggressive preprocessing for difficult images"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Strong noise reduction
        denoised = cv2.bilateralFilter(gray, 9, 80, 80)
        
        # Morphological operations to clean text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
        
        # Strong contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(cleaned)
        
        # Adaptive thresholding
        threshold = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 10
        )
        
        # Strong sharpening
        kernel = np.array([[-1,-1,-1,-1,-1],
                          [-1, 2, 2, 2,-1],
                          [-1, 2, 8, 2,-1],
                          [-1, 2, 2, 2,-1],
                          [-1,-1,-1,-1,-1]]) / 8.0
        sharpened = cv2.filter2D(threshold, -1, kernel)
        
        return np.clip(sharpened, 0, 255).astype(np.uint8)
        
    except Exception:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def gentle_preprocess(image):
    """Gentle preprocessing for high-quality images"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Light denoising only if needed
        mean_val = np.mean(gray)
        if mean_val < 50 or mean_val > 200:
            denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        else:
            denoised = gray
        
        # Simple Otsu thresholding
        _, threshold = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Light sharpening if the image seems blurry
        if np.std(threshold) < 80:
            kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
            threshold = cv2.filter2D(threshold, -1, kernel)
            threshold = np.clip(threshold, 0, 255).astype(np.uint8)
        
        return threshold
        
    except Exception:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def fallback_ocr_extraction(pil_image):
    """Fallback OCR extraction with basic configuration"""
    try:
        config_simple = r'--oem 1 --psm 6 -l eng+spa'
        return pytesseract.image_to_string(pil_image, config=config_simple)
    except:
        return ""

def is_good_ocr_result(text):
    """Check if OCR result seems reliable"""
    if not text or len(text.strip()) < 10:
        return False
    
    # Check ratio of letters to total characters
    letters = sum(c.isalpha() for c in text)
    total_chars = len([c for c in text if not c.isspace()])
    
    if total_chars == 0:
        return False
    
    letter_ratio = letters / total_chars
    
    # Good result should have at least 60% letters
    return letter_ratio >= 0.6

def detect_and_correct_orientation(image):
    """Detect and correct text orientation for better OCR"""
    try:
        # Get OSD (Orientation and Script Detection) info
        osd_config = r'--psm 0 -l eng+spa'
        osd_data = pytesseract.image_to_osd(image, config=osd_config)
        
        # Extract rotation angle
        for line in osd_data.split('\n'):
            if 'Rotate:' in line:
                angle = int(line.split(':')[1].strip())
                if angle != 0:
                    # Rotate image to correct orientation
                    rotated = image.rotate(-angle, expand=True, fillcolor='white')
                    return rotated
        
        return image
    except:
        # If OSD fails, return original image
        return image

def preprocess_image(image):
    """Enhanced preprocessing for better accuracy and speed balance"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Analyze image characteristics for intelligent processing
        mean_intensity = np.mean(gray)
        std_intensity = np.std(gray)
        
        # Apply noise reduction based on image quality
        if std_intensity < 30:  # Low contrast image
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
        elif mean_intensity < 100 or mean_intensity > 200:
            # Use bilateral filter for noisy images
            enhanced = cv2.bilateralFilter(gray, 5, 50, 50)
        else:
            enhanced = gray
        
        # Apply morphological operations to clean small noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        cleaned = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
        
        # Smart thresholding based on image characteristics
        if mean_intensity < 128:  # Dark image
            _, threshold = cv2.threshold(cleaned, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:  # Light image
            threshold = cv2.adaptiveThreshold(
                cleaned, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        
        # Sharpening for better character recognition (if needed)
        if np.std(threshold) < 60:  # Image might be blurry
            kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
            threshold = cv2.filter2D(threshold, -1, kernel)
            threshold = np.clip(threshold, 0, 255).astype(np.uint8)
        
        return threshold
        
    except Exception:
        # If preprocessing fails, return original grayscale
        try:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        except:
            return image

def correct_bullet_points(line, lines, current_index):
    """Ultra-advanced bullet point correction with context awareness"""
    corrected_line = line.strip()
    
    if corrected_line:
        # Enhanced bullet character detection
        if re.match(r'^[o0O*\-•·▪▫■□◆◇○●⋅‣⁃]\s+', corrected_line):
            # Convert to consistent bullet point
            corrected_line = re.sub(r'^[o0O*\-•·▪▫■□◆◇○●⋅‣⁃]\s+', '• ', corrected_line)
        
        # Fix OCR errors where bullets become letters/numbers
        elif re.match(r'^[lI1]\s+[A-Z]', corrected_line):
            # "I Something" or "l Something" might be "• Something"
            if is_likely_bullet_context(lines, current_index):
                corrected_line = re.sub(r'^[lI1]\s+', '• ', corrected_line)
        
        # Fix cases where bullet is misread as punctuation
        elif re.match(r'^[.,;:]\s+[A-Z]', corrected_line):
            if is_likely_bullet_context(lines, current_index):
                corrected_line = re.sub(r'^[.,;:]\s+', '• ', corrected_line)
        
        # Fix numbered lists (be more careful with context)
        elif re.match(r'^[Il1]\.\s+', corrected_line):
            if is_likely_numbered_list(lines, current_index):
                corrected_line = re.sub(r'^[Il1]\.', '1.', corrected_line)
        
        elif re.match(r'^[Il1]\)\s+', corrected_line):
            if is_likely_numbered_list(lines, current_index):
                corrected_line = re.sub(r'^[Il1]\)', '1)', corrected_line)
        
        # Fix common OCR mistakes in bullet contexts
        elif re.match(r'^[•]\s*[Il1]\s+', corrected_line):
            # "• I text" should be "• text" 
            corrected_line = re.sub(r'^([•])\s*[Il1]\s+', r'\1 ', corrected_line)
        
        # Fix cases where text after bullet is merged
        elif re.match(r'^[•]\w', corrected_line):
            # "•Something" should be "• Something"
            corrected_line = re.sub(r'^([•])(\w)', r'\1 \2', corrected_line)
    
    return corrected_line

def is_likely_bullet_context(lines, current_index):
    """Check if current line is likely in a bullet point context"""
    # Look for bullet patterns in nearby lines
    start = max(0, current_index - 2)
    end = min(len(lines), current_index + 3)
    
    bullet_count = 0
    for i in range(start, end):
        if i != current_index and i < len(lines):
            line = lines[i].strip()
            if re.match(r'^[•◦▪▫○●⋅‣⁃oO*\-]\s', line):
                bullet_count += 1
    
    return bullet_count >= 1

def is_likely_numbered_list(lines, current_index):
    """Check if current line is likely part of a numbered list"""
    # Look for pattern of numbered items nearby
    for i in range(max(0, current_index-2), min(len(lines), current_index+3)):
        if i != current_index and lines[i].strip():
            if re.match(r'^[0-9Il1]+[\.\)]\s+', lines[i].strip()):
                return True
    return False

def clean_extracted_text(text):
    """Clean and post-process extracted text with smart bullet point correction"""
    if not text:
        return ""
    
    # Fix bullet points first
    text = fix_bullet_points(text)
    
    # Remove excessive whitespace while preserving structure
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove leading/trailing whitespace
        cleaned_line = line.strip()
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
        elif cleaned_lines and cleaned_lines[-1]:  # Preserve paragraph breaks
            cleaned_lines.append('')
    
    # Join lines back together
    result = '\n'.join(cleaned_lines)
    
    # Remove excessive blank lines (more than 2 consecutive)
    while '\n\n\n' in result:
        result = result.replace('\n\n\n', '\n\n')
    
    return result.strip()

def fix_bullet_points(text):
    """Advanced bullet point correction with context awareness"""
    lines = text.split('\n')
    corrected_lines = []
    
    for i, line in enumerate(lines):
        corrected_line = line.strip()
        
        if corrected_line:
            # Check if line starts with potential bullet characters
            if re.match(r'^[o0O*\-•·▪▫■□◆◇○●]\s+', corrected_line):
                # Convert to consistent bullet point
                corrected_line = re.sub(r'^[o0O*\-•·▪▫■□◆◇○●]\s+', '• ', corrected_line)
            
            # Fix numbered lists (be more careful with context)
            elif re.match(r'^[Il1]\.\s+', corrected_line):
                # Check if this looks like a numbered list by looking at context
                if is_likely_numbered_list(lines, i):
                    corrected_line = re.sub(r'^[Il1]\.', '1.', corrected_line)
            
            elif re.match(r'^[Il1]\)\s+', corrected_line):
                if is_likely_numbered_list(lines, i):
                    corrected_line = re.sub(r'^[Il1]\)', '1)', corrected_line)
            
            # Fix common OCR mistakes in bullet contexts
            elif re.match(r'^[•]\s*[Il1]\s+', corrected_line):
                # "• I text" should be "• text" 
                corrected_line = re.sub(r'^([•])\s*[Il1]\s+', r'\1 ', corrected_line)
        
        corrected_lines.append(corrected_line)
    
    return '\n'.join(corrected_lines)



if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug, host='0.0.0.0', port=port) 