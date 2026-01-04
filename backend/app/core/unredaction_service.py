"""Unredaction service for recovering redacted text from documents."""

import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import numpy as np

from app.utils.logger import logger


class RedactedRegion:
    """Represents a detected redacted region in a document."""

    def __init__(
        self,
        page: int,
        bbox: Tuple[float, float, float, float],
        context_before: str = "",
        context_after: str = "",
        region_type: str = "unknown"
    ):
        self.page = page
        self.bbox = bbox  # (x0, y0, x1, y1)
        self.context_before = context_before
        self.context_after = context_after
        self.region_type = region_type  # "blackout", "whiteout", "pixelated"


class UnredactionResult:
    """Result of unredaction attempt."""

    def __init__(
        self,
        original_text: str,
        predicted_text: str,
        confidence: float,
        method: str,
        context: str = ""
    ):
        self.original_text = original_text
        self.predicted_text = predicted_text
        self.confidence = confidence  # 0.0 to 1.0
        self.method = method  # "ai_inference", "pattern_match", "context_analysis"
        self.context = context


class UnredactionService:
    """Service for detecting and recovering redacted text."""

    def __init__(self):
        """Initialize unredaction service."""
        self.llm_client = None

    async def analyze_document(
        self,
        file_path: str,
        use_ai: bool = True,
        use_ocr: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze document for redacted regions and attempt recovery.

        Args:
            file_path: Path to document
            use_ai: Whether to use AI for prediction
            use_ocr: Whether to use OCR for detection

        Returns:
            Dictionary with analysis results
        """
        try:
            path = Path(file_path)
            extension = path.suffix.lower()

            if extension == '.pdf':
                return await self._analyze_pdf(file_path, use_ai, use_ocr)
            elif extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                return await self._analyze_image(file_path, use_ai, use_ocr)
            else:
                raise ValueError(f"Unsupported file type: {extension}")

        except Exception as e:
            logger.error(f"Unredaction analysis failed: {str(e)}")
            raise

    async def _analyze_pdf(
        self,
        file_path: str,
        use_ai: bool,
        use_ocr: bool
    ) -> Dict[str, Any]:
        """Analyze PDF for redacted content."""
        results = {
            "file_path": file_path,
            "total_pages": 0,
            "redacted_regions": [],
            "predictions": [],
            "summary": {}
        }

        try:
            doc = fitz.open(file_path)
            results["total_pages"] = len(doc)

            for page_num, page in enumerate(doc, start=1):
                # Detect redacted regions
                regions = self._detect_redacted_regions_pdf(page, page_num)
                results["redacted_regions"].extend(regions)

                # Attempt predictions for each region
                if regions:
                    page_text = page.get_text()
                    for region in regions:
                        # Try pattern matching first (always)
                        pattern_result = self._pattern_based_prediction(region)

                        # If AI is enabled and pattern matching didn't give high confidence, try AI
                        if use_ai and (not pattern_result or pattern_result.confidence < 0.7):
                            ai_result = await self._ai_based_prediction(region, page_text)
                            # Use AI result if better than pattern result
                            if ai_result and (not pattern_result or ai_result.confidence > pattern_result.confidence):
                                prediction = ai_result
                            else:
                                prediction = pattern_result
                        else:
                            prediction = pattern_result

                        if prediction:
                            results["predictions"].append(prediction)

            doc.close()

            # Generate summary
            results["summary"] = {
                "total_redactions": len(results["redacted_regions"]),
                "predictions_made": len(results["predictions"]),
                "high_confidence": len([p for p in results["predictions"] if p.confidence >= 0.8]),
                "medium_confidence": len([p for p in results["predictions"] if 0.5 <= p.confidence < 0.8]),
                "low_confidence": len([p for p in results["predictions"] if p.confidence < 0.5])
            }

            return results

        except Exception as e:
            logger.error(f"PDF analysis failed: {str(e)}")
            raise

    async def _analyze_image(
        self,
        file_path: str,
        use_ai: bool,
        use_ocr: bool
    ) -> Dict[str, Any]:
        """Analyze image for redacted content."""
        results = {
            "file_path": file_path,
            "redacted_regions": [],
            "predictions": [],
            "summary": {}
        }

        try:
            # Load image
            img = Image.open(file_path)
            img_array = np.array(img)

            # Detect redacted regions in image
            regions = self._detect_redacted_regions_image(img_array)
            results["redacted_regions"] = regions

            # TODO: OCR extraction when Tesseract is available
            if use_ocr:
                logger.warning("OCR not yet available. Install Tesseract first.")

            results["summary"] = {
                "total_redactions": len(results["redacted_regions"]),
                "predictions_made": len(results["predictions"])
            }

            return results

        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            raise

    def _detect_redacted_regions_pdf(
        self,
        page: fitz.Page,
        page_num: int
    ) -> List[RedactedRegion]:
        """Detect redacted regions in PDF page using multiple detection methods."""
        regions = []

        try:
            # Extract page text with coordinates
            text_dict = page.get_text("dict")
            blocks = text_dict.get("blocks", [])

            # Method 1: Look for drawings (common redaction method)
            drawings = page.get_drawings()
            for drawing in drawings:
                # Check if drawing is a filled path
                # Types: 'f' = fill only, 's' = stroke only, 'fs' = fill+stroke
                drawing_type = drawing.get("type", "")
                if "f" in drawing_type:  # Any filled path
                    rect = drawing.get("rect")
                    fill_color = drawing.get("fill", (0, 0, 0))

                    # Determine redaction type based on color
                    region_type = None

                    # Black redaction (most common)
                    if rect and fill_color == (0.0, 0.0, 0.0):
                        region_type = "blackout"

                    # White redaction (whiteout)
                    elif rect and fill_color == (1.0, 1.0, 1.0):
                        region_type = "whiteout"

                    # Gray redaction
                    elif rect and fill_color[0] == fill_color[1] == fill_color[2] and 0.3 < fill_color[0] < 0.7:
                        region_type = "graybox"

                    # Colored rectangles (sometimes used for redaction)
                    elif rect and any(fill_color):
                        # Check if it's a solid color and large enough to be a redaction
                        rect_area = (rect[2] - rect[0]) * (rect[3] - rect[1])
                        if rect_area > 100:  # Minimum area threshold
                            region_type = "colored_box"

                    if region_type:
                        # Extract context before and after
                        context_before, context_after = self._extract_context(
                            page, rect, blocks
                        )

                        region = RedactedRegion(
                            page=page_num,
                            bbox=rect,
                            context_before=context_before,
                            context_after=context_after,
                            region_type=region_type
                        )
                        regions.append(region)

            # Method 2: Check for annotations (redaction annotations)
            for annot in page.annots():
                if annot.type[0] == 12:  # Redaction annotation
                    rect = annot.rect
                    context_before, context_after = self._extract_context(
                        page, rect, blocks
                    )

                    region = RedactedRegion(
                        page=page_num,
                        bbox=tuple(rect),
                        context_before=context_before,
                        context_after=context_after,
                        region_type="redaction_annotation"
                    )
                    regions.append(region)

            # Method 3: Look for text-based redaction markers
            full_text = page.get_text()
            if any(marker in full_text for marker in ["█", "▇", "▆", "▅", "▄", "[REDACTED]", "REDACTED", "XXX"]):
                # Detect regions with redaction markers
                words = page.get_text("words")
                for word_info in words:
                    if len(word_info) < 5:
                        continue

                    word_text = word_info[4]
                    # Check if word contains redaction markers
                    if any(marker in word_text for marker in ["█", "▇", "▆", "▅", "▄", "REDACTED", "XXX"]):
                        rect = (word_info[0], word_info[1], word_info[2], word_info[3])

                        context_before, context_after = self._extract_context(
                            page, rect, blocks
                        )

                        region = RedactedRegion(
                            page=page_num,
                            bbox=rect,
                            context_before=context_before,
                            context_after=context_after,
                            region_type="text_marker"
                        )
                        regions.append(region)

        except Exception as e:
            logger.error(f"Region detection failed: {str(e)}")

        return regions

    def _detect_redacted_regions_image(
        self,
        img_array: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Detect redacted regions in image using multiple methods."""
        regions = []

        try:
            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = np.mean(img_array, axis=2).astype(np.uint8)
            else:
                gray = img_array

            # Try with OpenCV if available
            try:
                import cv2

                # Method 1: Detect black regions (common redaction)
                black_mask = (gray < 30).astype(np.uint8)
                black_contours, _ = cv2.findContours(
                    black_mask,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE
                )

                for contour in black_contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    if w * h > 100:  # Minimum size threshold
                        regions.append({
                            "bbox": (x, y, x + w, y + h),
                            "type": "blackout",
                            "area": w * h
                        })

                # Method 2: Detect white regions (whiteout redaction)
                white_mask = (gray > 225).astype(np.uint8)
                white_contours, _ = cv2.findContours(
                    white_mask,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE
                )

                for contour in white_contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    if w * h > 100:
                        regions.append({
                            "bbox": (x, y, x + w, y + h),
                            "type": "whiteout",
                            "area": w * h
                        })

                # Method 3: Detect gray/colored boxes
                # Edge detection to find rectangular regions
                edges = cv2.Canny(gray, 50, 150)
                kernel = np.ones((5, 5), np.uint8)
                dilated = cv2.dilate(edges, kernel, iterations=2)

                contours, _ = cv2.findContours(
                    dilated,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE
                )

                for contour in contours:
                    # Approximate contour to polygon
                    peri = cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

                    # Look for rectangular shapes (4 corners)
                    if len(approx) == 4:
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = float(w) / h if h > 0 else 0

                        # Check if it's a reasonable rectangle and large enough
                        if 0.2 < aspect_ratio < 5 and w * h > 200:
                            # Check if region has uniform color (potential redaction)
                            region_gray = gray[y:y+h, x:x+w]
                            std_dev = np.std(region_gray)

                            # Low standard deviation = uniform color = potential redaction
                            if std_dev < 30:
                                regions.append({
                                    "bbox": (x, y, x + w, y + h),
                                    "type": "uniform_box",
                                    "area": w * h
                                })

                # Method 4: Detect pixelated/blurred regions
                # Calculate local variance
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
                laplacian_var = laplacian.var()

                # Apply threshold to find low-detail regions
                _, low_detail = cv2.threshold(
                    cv2.convertScaleAbs(laplacian),
                    int(laplacian_var * 0.5),
                    255,
                    cv2.THRESH_BINARY_INV
                )

                low_detail_contours, _ = cv2.findContours(
                    low_detail,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE
                )

                for contour in low_detail_contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    if 500 < w * h < 50000:  # Reasonable size range
                        regions.append({
                            "bbox": (x, y, x + w, y + h),
                            "type": "pixelated",
                            "area": w * h
                        })

            except ImportError:
                logger.warning("OpenCV not available, using basic detection")

                # Fallback: Basic detection without OpenCV
                # Detect black regions
                black_mask = gray < 30
                # Simple bounding box detection
                rows = np.any(black_mask, axis=1)
                cols = np.any(black_mask, axis=0)
                if rows.any() and cols.any():
                    y_min, y_max = np.where(rows)[0][[0, -1]]
                    x_min, x_max = np.where(cols)[0][[0, -1]]
                    area = (x_max - x_min) * (y_max - y_min)
                    if area > 100:
                        regions.append({
                            "bbox": (x_min, y_min, x_max, y_max),
                            "type": "blackout",
                            "area": area
                        })

                # Detect white regions
                white_mask = gray > 225
                rows = np.any(white_mask, axis=1)
                cols = np.any(white_mask, axis=0)
                if rows.any() and cols.any():
                    y_min, y_max = np.where(rows)[0][[0, -1]]
                    x_min, x_max = np.where(cols)[0][[0, -1]]
                    area = (x_max - x_min) * (y_max - y_min)
                    if area > 100:
                        regions.append({
                            "bbox": (x_min, y_min, x_max, y_max),
                            "type": "whiteout",
                            "area": area
                        })

        except Exception as e:
            logger.error(f"Image region detection failed: {str(e)}")

        return regions

    def _extract_context(
        self,
        page: fitz.Page,
        redacted_rect: Tuple,
        blocks: List[Dict]
    ) -> Tuple[str, str]:
        """Extract text before and after redacted region, replacing covered text with [REDACTED]."""
        context_before = ""
        context_after = ""

        try:
            rect = fitz.Rect(redacted_rect)

            # Get all text with coordinates
            words = page.get_text("words")  # Returns list of (x0, y0, x1, y1, "word", block_no, line_no, word_no)

            for word_info in words:
                if len(word_info) < 5:
                    continue

                word_rect = fitz.Rect(word_info[0], word_info[1], word_info[2], word_info[3])
                word_text = word_info[4]

                # Check if this word overlaps with the redacted region
                if word_rect.intersects(rect):
                    # This word is redacted, use placeholder
                    word_text = "[REDACTED]"

                # Determine if word is before or after the redacted region
                # Consider reading order: top-to-bottom, left-to-right
                if word_rect.y1 < rect.y0 or (word_rect.y0 < rect.y1 and word_rect.x1 < rect.x0):
                    # Word is before the redacted region
                    context_before += word_text + " "
                elif word_rect.y0 > rect.y1 or (word_rect.y0 < rect.y1 and word_rect.x0 > rect.x1):
                    # Word is after the redacted region
                    context_after += word_text + " "

        except Exception as e:
            logger.error(f"Context extraction failed: {str(e)}")

        return context_before.strip()[-200:], context_after.strip()[:200]

    async def _predict_redacted_content(
        self,
        region: RedactedRegion,
        full_text: str
    ) -> Optional[UnredactionResult]:
        """Predict redacted content using AI and pattern analysis."""
        try:
            # First, try pattern-based prediction
            pattern_result = self._pattern_based_prediction(region)
            if pattern_result and pattern_result.confidence >= 0.7:
                return pattern_result

            # Then, try AI-based prediction
            ai_result = await self._ai_based_prediction(region, full_text)

            # Return the result with higher confidence
            if pattern_result and ai_result:
                return pattern_result if pattern_result.confidence > ai_result.confidence else ai_result
            elif pattern_result:
                return pattern_result
            else:
                return ai_result

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return None

    def _pattern_based_prediction(
        self,
        region: RedactedRegion
    ) -> Optional[UnredactionResult]:
        """Use pattern matching to predict redacted content."""
        context = f"{region.context_before} [REDACTED] {region.context_after}"

        # Common patterns (ordered by specificity - most specific first)
        patterns = {
            # === IDENTIFICATION NUMBERS === (Highest confidence)
            r"(?:SSN|Social Security Number):\s*(?:XXX-XX-)?\[REDACTED\]": ("ssn_last_4", 0.95),
            r"(?:Passport|Passport Number):\s*\[REDACTED\]": ("passport_number", 0.95),
            r"(?:Driver'?s? License|DL):\s*\[REDACTED\]": ("drivers_license", 0.95),
            r"(?:Case|Docket|File) (?:Number|No\.?|#):\s*\[REDACTED\]": ("case_number", 0.9),

            # === FINANCIAL PATTERNS ===
            r"(?:Amount|Total|Payment|Transfer):\s*\$\s*\[REDACTED\]": ("dollar_amount", 0.92),
            r"\$\s*\[REDACTED\]\s+(?:USD|dollars?|payment)": ("dollar_amount", 0.88),
            r"\$\s*\[REDACTED\]": ("dollar_amount", 0.82),
            r"Account Number:\s*\[REDACTED\]": ("account_number", 0.92),
            r"Routing Number:\s*\[REDACTED\]": ("routing_number", 0.92),
            r"(?:Credit Card|Card Number):\s*\[REDACTED\]": ("credit_card", 0.93),
            r"(?:Bitcoin|BTC|Wallet) (?:Address|ID):\s*\[REDACTED\]": ("crypto_address", 0.9),

            # === CONTACT INFORMATION ===
            r"(?:Email|E-mail):\s*\[REDACTED\]@": ("email_local_part", 0.92),
            r"@\[REDACTED\]\.(?:com|org|net|edu|gov)": ("email_domain", 0.92),
            r"@\[REDACTED\]": ("email_domain", 0.88),
            r"(?:Phone|Tel|Telephone|Mobile|Cell):\s*\[REDACTED\]": ("phone_number", 0.92),
            r"(?:Fax|Facsimile):\s*\[REDACTED\]": ("fax_number", 0.9),

            # === NAMES AND IDENTITIES ===
            r"(?:Agent|Officer|Detective|Inspector)\s+\[REDACTED\]": ("law_enforcement_name", 0.88),
            r"(?:Dr\.|Doctor|Professor|Prof\.)\s+\[REDACTED\]": ("professional_name", 0.85),
            r"(?:Mr\.|Mrs\.|Ms\.|Miss)\s+\[REDACTED\]": ("person_name_with_title", 0.85),
            r"(?:Subject|Suspect|Defendant|Plaintiff):\s*\[REDACTED\]": ("subject_name", 0.87),
            r"(?:vs\.|v\.|versus)\s*\[REDACTED\]": ("opposing_party_name", 0.87),
            r"(?:Attorney|Lawyer|Counsel)\s+\[REDACTED\]": ("attorney_name", 0.85),
            r"(?:Judge|Justice|Hon\.)\s+\[REDACTED\]": ("judge_name", 0.88),
            r"(?:President|CEO|Director|Manager)\s+\[REDACTED\]": ("executive_name", 0.83),
            r"(?:witness|testified by|deposed)\s+\[REDACTED\]": ("witness_name", 0.82),
            r"by\s+\[REDACTED\]\s+on": ("person_name_action", 0.78),
            r"\[REDACTED\]\s+(?:testified|stated|claimed|alleged)": ("person_name_statement", 0.77),

            # === LOCATIONS ===
            r"(?:located at|address:|located:)\s*\[REDACTED\]": ("street_address", 0.88),
            r"\[REDACTED\]\s+(?:Street|St\.|Avenue|Ave\.|Road|Rd\.|Boulevard|Blvd\.)": ("street_name", 0.87),
            r"(?:City|Town):\s*\[REDACTED\]": ("city_name", 0.9),
            r"(?:State of|Province of)\s+\[REDACTED\]": ("state_province", 0.88),
            r"(?:Country|Nation):\s*\[REDACTED\]": ("country_name", 0.9),
            r"(?:ZIP|Postal Code):\s*\[REDACTED\]": ("zip_code", 0.92),
            r"\[REDACTED\],\s*(?:USA|United States|America)": ("us_city", 0.85),
            r"in\s+(?:downtown|uptown|central)\s+\[REDACTED\]": ("city_area", 0.75),

            # === DATES AND TIMES ===
            r"(?:on|date:|dated:)\s*\[REDACTED\]\s+\d{1,2},\s*\d{4}": ("month_name", 0.85),
            r"\[REDACTED\]\s+\d{1,2},\s*\d{4}": ("month_name", 0.82),
            r"(?:on|date:)\s*\d{1,2}/\[REDACTED\]/\d{4}": ("month_number", 0.85),
            r"\[REDACTED\]/\d{1,2}/\d{4}": ("date_component", 0.75),
            r"(?:at|time:)\s*\[REDACTED\]\s*(?:AM|PM|a\.m\.|p\.m\.)": ("time_hour", 0.8),
            r"between\s+\[REDACTED\]\s+(?:and|to)": ("time_period_start", 0.75),

            # === VEHICLE INFORMATION ===
            r"(?:a|the)\s+\[REDACTED\]\s+(?:\d{4})\s+(?:vehicle|car|truck|SUV|sedan)": ("vehicle_color_with_year", 0.83),
            r"(?:a|the)\s+\[REDACTED\]\s+(?:Honda|Toyota|Ford|BMW|Mercedes|Lexus|Chevrolet|Nissan)": ("vehicle_color_with_make", 0.85),
            r"\[REDACTED\]\s+(?:vehicle|car|automobile)": ("vehicle_descriptor", 0.73),
            r"(?:License Plate|Plate Number|Tag):\s*\[REDACTED\]": ("license_plate", 0.92),
            r"(?:VIN|Vehicle ID):\s*\[REDACTED\]": ("vin_number", 0.93),

            # === ORGANIZATIONS ===
            r"(?:Company|Corporation|LLC|Inc\.|Ltd\.):\s*\[REDACTED\]": ("company_name", 0.85),
            r"\[REDACTED\]\s+(?:Corporation|Company|LLC|Inc\.|Ltd\.)": ("company_name_with_suffix", 0.83),
            r"(?:employed by|works for)\s+\[REDACTED\]": ("employer_name", 0.8),

            # === DOCUMENT REFERENCES ===
            r"(?:Document|Exhibit|Report)\s+(?:Number|No\.?|#):\s*\[REDACTED\]": ("document_id", 0.88),
            r"(?:Page|Pg\.|P\.)\s+\[REDACTED\]": ("page_number", 0.85),
            r"(?:Section|Sec\.|§)\s+\[REDACTED\]": ("section_number", 0.85),

            # === SURVEILLANCE/INTELLIGENCE ===
            r"(?:Subject|Target) was\s+\[REDACTED\]": ("activity_description", 0.7),
            r"(?:monitoring|surveillance of)\s+\[REDACTED\]\s+(?:activities|movements)": ("surveillance_subject", 0.72),
            r"(?:informant|source|CI-)\[REDACTED\]": ("informant_identifier", 0.88),
            r"(?:Operation|Op)\s+\[REDACTED\]": ("operation_name", 0.83),

            # === TECHNICAL ===
            r"IP Address:\s*\[REDACTED\]": ("ip_address", 0.93),
            r"(?:MAC Address|MAC):\s*\[REDACTED\]": ("mac_address", 0.93),
            r"(?:URL|Website):\s*\[REDACTED\]": ("url", 0.9),
            r"(?:Username|User ID):\s*\[REDACTED\]": ("username", 0.91),
            r"(?:Password|PIN):\s*\[REDACTED\]": ("password", 0.95),

            # === GENERIC PATTERNS === (Lower confidence)
            r"Case\s+#\d+-\d+\s+\[REDACTED\]\s+\d{1,2}": ("date_component_generic", 0.6),
            r"(?:approximately|about)\s+\[REDACTED\]\s+(?:hours|minutes|days)": ("time_duration", 0.7),
            r"\[REDACTED\]\s+(?:years old|y/o|age)": ("age", 0.8),
            r"(?:height|tall):\s*\[REDACTED\]": ("height", 0.85),
            r"(?:weight|weighs):\s*\[REDACTED\]": ("weight", 0.85),
        }

        for pattern, (pred_type, confidence) in patterns.items():
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return UnredactionResult(
                    original_text="[REDACTED]",
                    predicted_text=f"[{pred_type.upper()}]",
                    confidence=confidence,
                    method="pattern_match",
                    context=context[:300]
                )

        return None

    async def _ai_based_prediction(
        self,
        region: RedactedRegion,
        full_text: str
    ) -> Optional[UnredactionResult]:
        """Use AI to predict redacted content."""
        try:
            # Use ollama directly for predictions
            import ollama
            from app.config import settings

            # Prepare prompt for AI
            prompt = f"""You are analyzing a legal/government document with redacted information.

Context before redaction: "{region.context_before}"
Context after redaction: "{region.context_after}"

Based on the context, what type of information was likely redacted? Provide:
1. The type of information (name, SSN, address, date, amount, etc.)
2. If possible, a reasonable prediction of the specific value
3. Your confidence level (0-100%)

Respond in this format:
Type: <type>
Prediction: <your prediction or "Unknown">
Confidence: <0-100>
Reasoning: <brief explanation>
"""

            # Get AI response using ollama
            response = ollama.chat(
                model=settings.OLLAMA_LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an AI that predicts redacted information from document context."},
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response['message']['content']

            # Parse AI response
            pred_type = "unknown"
            prediction = "Unknown"
            confidence = 0.5

            lines = response_text.strip().split('\n')
            for line in lines:
                if line.startswith("Type:"):
                    pred_type = line.split(":", 1)[1].strip()
                elif line.startswith("Prediction:"):
                    prediction = line.split(":", 1)[1].strip()
                elif line.startswith("Confidence:"):
                    conf_str = line.split(":", 1)[1].strip().rstrip('%')
                    try:
                        confidence = float(conf_str) / 100.0
                    except ValueError:
                        confidence = 0.5

            return UnredactionResult(
                original_text="[REDACTED]",
                predicted_text=f"[{pred_type.upper()}: {prediction}]",
                confidence=confidence,
                method="ai_inference",
                context=f"{region.context_before} ... {region.context_after}"
            )

        except Exception as e:
            logger.error(f"AI prediction failed: {str(e)}")
            return None
