"""
AI Processing Engine for CCTV Video Analysis
==============================================

This module handles video processing, face detection, and behavior classification
for the classroom engagement monitoring system.

Features:
- Frame-by-frame video processing using OpenCV
- Face detection using Haar Cascade classifiers
- Behavior classification (Attentive, Sleepy, Distracted, Neutral)
- Engagement percentage calculation
- Results storage at configurable intervals
"""

import cv2
import numpy as np
import os
import time
from datetime import datetime
from django.utils import timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import OpenCV, handle if not available
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not installed. Video processing will not work.")


class EngagementAnalyzer:
    """
    Main class for analyzing classroom engagement from video footage.
    Uses Haar Cascade for face detection and heuristic-based classification.
    """
    
    def __init__(self, save_interval=30, min_face_size=(30, 30)):
        """
        Initialize the engagement analyzer.
        
        Args:
            save_interval: Save results every N frames (default: 30)
            min_face_size: Minimum face size to detect (default: 30x30)
        """
        self.save_interval = save_interval
        self.min_face_size = min_face_size
        self.face_cascade = None
        self.frame_count = 0
        self.total_faces_detected = 0
        
        # Classification counters (reset each save interval)
        self.attentive_count = 0
        self.sleepy_count = 0
        self.distracted_count = 0
        self.neutral_count = 0
        
        # Cumulative stats
        self.cumulative_stats = {
            'attentive': 0,
            'sleepy': 0,
            'distracted': 0,
            'neutral': 0
        }
        
        # Initialize Haar Cascade
        self._load_face_cascade()
    
    def _load_face_cascade(self):
        """Load the Haar Cascade classifier for face detection"""
        if not CV2_AVAILABLE:
            logger.error("OpenCV is not installed. Please install opencv-python")
            return
        
        # Try to load the default Haar Cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        
        if os.path.exists(cascade_path):
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            logger.info(f"Loaded Haar Cascade from {cascade_path}")
        else:
            logger.warning("Haar Cascade file not found. Using alternative detection.")
            self.face_cascade = None
    
    def classify_behavior(self, face_region):
        """
        Classify student behavior based on face region.
        
        Since we don't have a trained model, we use heuristic-based classification:
        - Based on face position, size variation, and brightness patterns
        
        Args:
            face_region: The detected face region (grayscale image)
            
        Returns:
            str: Behavior classification (Attentive, Sleepy, Distracted, Neutral)
        """
        if face_region is None or face_region.size == 0:
            return 'Neutral'
        
        try:
            # Get face dimensions
            h, w = face_region.shape[:2]
            
            if h == 0 or w == 0:
                return 'Neutral'
            
            # Calculate brightness (average intensity)
            brightness = np.mean(face_region)
            
            # Calculate contrast (standard deviation)
            contrast = np.std(face_region)
            
            # Calculate aspect ratio of face
            aspect_ratio = w / h if h > 0 else 1.0
            
            # Heuristic-based classification
            # Note: In a production system, you would use a trained ML model
            
            # Sleepy detection: Low brightness and low contrast (eyes closed/head down)
            if brightness < 80 and contrast < 30:
                return 'Sleepy'
            
            # Distracted detection: Unusual aspect ratio (face turned away)
            if aspect_ratio < 0.6 or aspect_ratio > 1.4:
                return 'Distracted'
            
            # Attentive: Good brightness, good contrast, normal aspect ratio
            if brightness > 100 and contrast > 40 and 0.7 < aspect_ratio < 1.3:
                return 'Attentive'
            
            # Default to Neutral
            return 'Neutral'
            
        except Exception as e:
            logger.debug(f"Classification error: {e}")
            return 'Neutral'
    
    def process_frame(self, frame):
        """
        Process a single frame to detect faces and classify behavior.
        
        Args:
            frame: Video frame (numpy array from OpenCV)
            
        Returns:
            tuple: (faces_detected, behavior_counts)
        """
        if frame is None:
            return 0, {}
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Equalize histogram for better detection
        gray = cv2.equalizeHist(gray)
        
        faces = []
        
        if self.face_cascade is not None:
            # Detect faces using Haar Cascade
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=self.min_face_size,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
        
        # Reset counts for this frame
        frame_attentive = 0
        frame_sleepy = 0
        frame_distracted = 0
        frame_neutral = 0
        
        # Process each detected face
        for (x, y, w, h) in faces:
            # Extract face region
            face_region = gray[y:y+h, x:x+w]
            
            # Classify behavior
            behavior = self.classify_behavior(face_region)
            
            if behavior == 'Attentive':
                frame_attentive += 1
            elif behavior == 'Sleepy':
                frame_sleepy += 1
            elif behavior == 'Distracted':
                frame_distracted += 1
            else:
                frame_neutral += 1
        
        # Update cumulative
        self.attentive_count += frame_attentive
        self.sleepy_count += frame_sleepy
        self.distracted_count += frame_distracted
        self.neutral_count += frame_neutral
        
        self.cumulative_stats['attentive'] += frame_attentive
        self.cumulative_stats['sleepy'] += frame_sleepy
        self.cumulative_stats['distracted'] += frame_distracted
        self.cumulative_stats['neutral'] += frame_neutral
        
        return len(faces), {
            'attentive': frame_attentive,
            'sleepy': frame_sleepy,
            'distracted': frame_distracted,
            'neutral': frame_neutral
        }
    
    def get_current_stats(self):
        """Get current interval statistics"""
        total = self.attentive_count + self.sleepy_count + self.distracted_count + self.neutral_count
        engagement_pct = (self.attentive_count / total * 100) if total > 0 else 0
        
        return {
            'total_students': total,
            'attentive_count': self.attentive_count,
            'sleepy_count': self.sleepy_count,
            'distracted_count': self.distracted_count,
            'neutral_count': self.neutral_count,
            'engagement_percentage': engagement_pct
        }
    
    def reset_interval_stats(self):
        """Reset interval counters after saving"""
        self.attentive_count = 0
        self.sleepy_count = 0
        self.distracted_count = 0
        self.neutral_count = 0
    
    def get_cumulative_stats(self):
        """Get cumulative statistics since start of processing"""
        total = sum(self.cumulative_stats.values())
        engagement_pct = (self.cumulative_stats['attentive'] / total * 100) if total > 0 else 0
        
        return {
            'total_students': total,
            'attentive_count': self.cumulative_stats['attentive'],
            'sleepy_count': self.cumulative_stats['sleepy'],
            'distracted_count': self.cumulative_stats['distracted'],
            'neutral_count': self.cumulative_stats['neutral'],
            'engagement_percentage': engagement_pct
        }


def process_video(video_path, video_upload_id=None, save_interval=30):
    """
    Process a video file and generate engagement records.
    
    This is the main entry point for video processing.
    
    Args:
        video_path: Path to the video file
        video_upload_id: ID of the VideoUpload model instance
        save_interval: Save results every N frames
        
    Returns:
        dict: Processing results including statistics
    """
    if not CV2_AVAILABLE:
        return {
            'success': False,
            'error': 'OpenCV is not installed',
            'records_created': 0
        }
    
    if not os.path.exists(video_path):
        return {
            'success': False,
            'error': 'Video file not found',
            'records_created': 0
        }
    
    # Import here to avoid circular imports
    from engagement.models import EngagementRecord
    
    logger.info(f"Starting video processing: {video_path}")
    
    # Initialize analyzer
    analyzer = EngagementAnalyzer(save_interval=save_interval)
    
    # Open video capture
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return {
            'success': False,
            'error': 'Could not open video file',
            'records_created': 0
        }
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    logger.info(f"Video properties: {total_frames} frames, {fps} FPS, {duration:.2f} seconds")
    
    records_created = 0
    start_time = time.time()
    frame_interval_start = time.time()
    
    try:
        while True:
            # Read frame
            ret, frame = cap.read()
            
            if not ret:
                break
            
            analyzer.frame_count += 1
            
            # Process frame
            faces_detected, _ = analyzer.process_frame(frame)
            analyzer.total_faces_detected += faces_detected
            
            # Save results at intervals
            if analyzer.frame_count % save_interval == 0:
                stats = analyzer.get_current_stats()
                
                # Create engagement record
                record = EngagementRecord(
                    video_upload_id=video_upload_id,
                    timestamp=timezone.now(),
                    total_students=stats['total_students'],
                    attentive_count=stats['attentive_count'],
                    sleepy_count=stats['sleepy_count'],
                    distracted_count=stats['distracted_count'],
                    neutral_count=stats['neutral_count'],
                    engagement_percentage=stats['engagement_percentage'],
                    frame_number=analyzer.frame_count,
                    processing_time=time.time() - frame_interval_start
                )
                record.save()
                records_created += 1
                
                logger.info(f"Frame {analyzer.frame_count}: {stats}")
                
                # Reset interval stats
                analyzer.reset_interval_stats()
                frame_interval_start = time.time()
            
            # Progress logging every 100 frames
            if analyzer.frame_count % 100 == 0:
                progress = (analyzer.frame_count / total_frames * 100) if total_frames > 0 else 0
                logger.info(f"Progress: {progress:.1f}% ({analyzer.frame_count}/{total_frames} frames)")
    
    except Exception as e:
        logger.error(f"Error during video processing: {e}")
        return {
            'success': False,
            'error': str(e),
            'records_created': records_created
        }
    
    finally:
        # Release video capture
        cap.release()
    
    # Save final results if any frames processed since last save
    if analyzer.frame_count % save_interval != 0:
        stats = analyzer.get_current_stats()
        if stats['total_students'] > 0:
            record = EngagementRecord(
                video_upload_id=video_upload_id,
                timestamp=timezone.now(),
                total_students=stats['total_students'],
                attentive_count=stats['attentive_count'],
                sleepy_count=stats['sleepy_count'],
                distracted_count=stats['distracted_count'],
                neutral_count=stats['neutral_count'],
                engagement_percentage=stats['engagement_percentage'],
                frame_number=analyzer.frame_count,
                processing_time=time.time() - frame_interval_start
            )
            record.save()
            records_created += 1
    
    processing_time = time.time() - start_time
    final_stats = analyzer.get_cumulative_stats()
    
    logger.info(f"Video processing completed in {processing_time:.2f} seconds")
    logger.info(f"Final stats: {final_stats}")
    logger.info(f"Created {records_created} engagement records")
    
    return {
        'success': True,
        'total_frames': analyzer.frame_count,
        'total_faces_detected': analyzer.total_faces_detected,
        'records_created': records_created,
        'processing_time': processing_time,
        'final_stats': final_stats
    }


def simulate_processing(video_upload_id=None):
    """
    Simulate video processing with random results.
    Used for testing when OpenCV is not available.
    
    Args:
        video_upload_id: ID of the VideoUpload model instance
        
    Returns:
        dict: Simulated processing results
    """
    from engagement.models import EngagementRecord
    import random
    
    logger.info("Running simulated processing")
    
    num_records = random.randint(10, 30)
    records_created = 0
    
    for i in range(num_records):
        total = random.randint(5, 20)
        attentive = random.randint(2, total)
        sleepy = random.randint(0, total - attentive)
        distracted = random.randint(0, total - attentive - sleepy)
        neutral = total - attentive - sleepy - distracted
        
        engagement_pct = (attentive / total * 100) if total > 0 else 0
        
        record = EngagementRecord(
            video_upload_id=video_upload_id,
            timestamp=timezone.now(),
            total_students=total,
            attentive_count=attentive,
            sleepy_count=sleepy,
            distracted_count=distracted,
            neutral_count=neutral,
            engagement_percentage=engagement_pct,
            frame_number=i * 30,
            processing_time=0.5
        )
        record.save()
        records_created += 1
    
    return {
        'success': True,
        'records_created': records_created,
        'simulated': True
    }

