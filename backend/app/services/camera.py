import cv2
import threading
import queue
import time
from ultralytics import YOLO


class CameraStream:
    def __init__(self, cameraUrl, deviceId, frameQueueSize=4, humanDetectionMode=False):
        """
        Khởi tạo CameraStream.

        :param cameraUrl: URL của camera stream (ví dụ: http://192.168.1.100:80/stream)
        :param deviceId: ID của device trong database
        :param frameQueueSize: Kích thước tối đa của queue lưu frame (mặc định 4)
        :param humanDetectionMode: Bật/tắt chế độ phát hiện người (mặc định False)
        """
        self.cameraUrl = cameraUrl
        self.deviceId = deviceId
        self.frameQueue = queue.Queue(maxsize=frameQueueSize)
        self.humanDetectionMode = humanDetectionMode

        # Biến thread
        self.captureThread = None
        self.detectionThread = None
        self.running = False

        self.processedFrame = None
        self.frameLock = threading.Lock()
        self.modeLock = threading.Lock()  # Mutex cho humanDetectionMode
        self.model = YOLO('yolo11n.pt')


    def start(self):
        """Bắt đầu các luồng capture và detection."""
        if self.running:
            return
        self.running = True
        self.captureThread = threading.Thread(target=self._capture_frames, daemon=True)
        self.detectionThread = threading.Thread(target=self._detect_humans, daemon=True)
        self.captureThread.start()
        self.detectionThread.start()
        print("CameraStream started")

    def stop(self):
        """Dừng các luồng capture và detection."""
        if not self.running:
            return
        print(f"🛑 Stopping CameraStream for {self.cameraUrl}")
        self.running = False
        
        # Đợi threads kết thúc
        if self.captureThread and self.captureThread.is_alive():
            self.captureThread.join(timeout=3)
        if self.detectionThread and self.detectionThread.is_alive():
            self.detectionThread.join(timeout=3)
        
        print("✅ CameraStream stopped successfully")

    def get_processed_frame(self):
        """Lấy frame đã được xử lý (processed frame) từ bên ngoài."""
        with self.frameLock:  # Đồng bộ truy cập
            return self.processedFrame.copy() if self.processedFrame is not None else None

    def set_detection_mode(self, enabled: bool):
        """Cập nhật humanDetectionMode từ bên ngoài."""
        with self.modeLock:
            if self.humanDetectionMode != enabled:
                self.humanDetectionMode = enabled
                print(f"🔄 Detection mode updated: {enabled}")

    def _capture_frames(self):
        """Luồng lấy frame từ cameraUrl và put vào queue."""
        cap = cv2.VideoCapture(self.cameraUrl)
        if not cap.isOpened():
            print(f"❌ Cannot open camera stream: {self.cameraUrl}")
            self.running = False
            return

        print(f"✅ Camera capture started: {self.cameraUrl}")
        while self.running:
            start_capture = time.time()
            ret, frame = cap.read()
            capture_time = time.time() - start_capture
            if ret:
                print(f"Captured frame at {time.strftime('%H:%M:%S', time.localtime())}, took {capture_time:.4f} seconds")
                print(f"Queue size after capture: {self.frameQueue.qsize()}")
                try:
                    self.frameQueue.put(frame, timeout=1)
                except queue.Full:
                    try:
                        self.frameQueue.get_nowait()
                        self.frameQueue.put(frame)
                    except queue.Empty:
                        pass
            else:
                print("⚠️ Failed to capture frame")
                time.sleep(0.04)

        cap.release()
        print("🛑 Camera capture thread stopped")

    def _detect_humans(self):
        """Luồng thực hiện detection trên frame từ queue."""
        with self.modeLock:
            initial_mode = self.humanDetectionMode
        print(f"✅ Detection thread started (mode: {initial_mode})")
        while self.running:
            try:
                frame = self.frameQueue.get(timeout=1)
                start_detect = time.time()
                processed_frame = frame.copy()

                # Đọc humanDetectionMode với mutex
                with self.modeLock:
                    detection_enabled = self.humanDetectionMode

                if detection_enabled and self.model:
                    results = self.model(processed_frame, classes=[0])
                    human_detected = False
                    for result in results:
                        for box in result.boxes:
                            if box.cls == 0:
                                human_detected = True
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                cv2.rectangle(processed_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                cv2.putText(processed_frame, "Person", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    if human_detected:
                        print("🚨 Human detected!")
                else:
                    time.sleep(0.02)

                detect_time = time.time() - start_detect
                print(f"Detected frame at {time.strftime('%H:%M:%S', time.localtime())}, took {detect_time:.4f} seconds")

                with self.frameLock:
                    self.processedFrame = processed_frame

            except queue.Empty:
                continue
        
        print("🛑 Detection thread stopped")