import cv2
import threading
import queue
import time
import torch
import asyncio
from ultralytics import YOLO

# Cache để tránh spam log human detection (giống temp_alert_cache)
_human_detection_cache: dict[str, float] = {}  # deviceId -> last_detection_time
HUMAN_DETECTION_COOLDOWN = 30  # Chỉ log 1 lần mỗi 30 giây


class CameraStream:
    def __init__(self, cameraUrl, deviceId, frameQueueSize=8, humanDetectionMode=False):
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
        self.current_fps = 0.0
        self.fpsLock = threading.Lock()  # Mutex cho current_fps
        
        # Reference to event loop for async logging from thread
        self._loop = None
        
        # Khởi tạo YOLO model với GPU nếu có
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = YOLO('yolo11s.pt')
        self.model.to(self.device)
        print(f"🔥 YOLO model loaded on: {self.device.upper()}")


    def start(self):
        """Bắt đầu các luồng capture và detection."""
        if self.running:
            return
        self.running = True
        
        # Lưu event loop để gọi async từ thread
        try:
            self._loop = asyncio.get_event_loop()
        except:
            self._loop = None
            
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

    def get_fps(self) -> float:
        """Lấy FPS hiện tại."""
        with self.fpsLock:
            return self.current_fps

    def _capture_frames(self):
        """Luồng lấy frame từ cameraUrl và put vào queue."""
        cap = cv2.VideoCapture(self.cameraUrl)
        if not cap.isOpened():
            print(f"❌ Cannot open camera stream: {self.cameraUrl}")
            self.running = False
            return

        print(f"✅ Camera capture started: {self.cameraUrl}")
        
        while self.running:
            ret, frame = cap.read()
            if ret:
                # Nếu queue đầy, bỏ frame cũ nhất và thêm frame mới
                if self.frameQueue.full():
                    try:
                        self.frameQueue.get_nowait()  # Bỏ frame cũ
                    except queue.Empty:
                        pass
                
                try:
                    self.frameQueue.put(frame, timeout=1)
                except queue.Full:
                    pass
            else:
                print("⚠️ Failed to capture frame")
                time.sleep(0.05)

        cap.release()
        print("🛑 Camera capture thread stopped")

    def _detect_humans(self):
        """Luồng thực hiện detection trên frame từ queue."""
        with self.modeLock:
            initial_mode = self.humanDetectionMode
        print(f"✅ Detection thread started (mode: {initial_mode})")
        
        frame_count = 0
        start_time = time.time()
        
        while self.running:
            try:
                frame = self.frameQueue.get(timeout=1)
                frame_count += 1
                processed_frame = frame.copy()

                # Đọc humanDetectionMode với mutex
                with self.modeLock:
                    detection_enabled = self.humanDetectionMode

                if detection_enabled and self.model:
                    results = self.model(processed_frame, classes=[0], device=self.device, verbose=False)
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
                        # Log human detection với cooldown để tránh spam
                        self._log_human_detection()
                else:
                    time.sleep(0.01)

                # Tính FPS mỗi 30 frames
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = 30 / elapsed if elapsed > 0 else 0
                    
                    # Lưu FPS vào biến dùng chung với mutex
                    with self.fpsLock:
                        self.current_fps = fps
                    
                    detection_status = "ON" if detection_enabled else "OFF"
                    # print(f"🔍 Detection FPS: {fps:.2f}, Mode: {detection_status}")
                    frame_count = 0
                    start_time = time.time()

                with self.frameLock:
                    self.processedFrame = processed_frame

            except queue.Empty:
                continue
        
        print("🛑 Detection thread stopped")

    def _log_human_detection(self):
        """Log human detection với cooldown để tránh spam"""
        global _human_detection_cache
        
        current_time = time.time()
        last_detection = _human_detection_cache.get(self.deviceId, 0)
        
        # Chỉ log nếu đã qua cooldown period
        if current_time - last_detection < HUMAN_DETECTION_COOLDOWN:
            return
        
        _human_detection_cache[self.deviceId] = current_time
        
        # Gọi async log từ thread
        if self._loop:
            try:
                asyncio.run_coroutine_threadsafe(
                    self._async_log_human_detection(),
                    self._loop
                )
            except Exception as e:
                print(f"⚠️ Failed to log human detection: {e}")

    async def _async_log_human_detection(self):
        """Async function để ghi log vào database"""
        try:
            from beanie import PydanticObjectId
            from app.models.device import Device
            from app.models.room import Room
            from app.services.activity_log import ActivityLogService
            from app.models.activity_log import LogType
            
            device = await Device.get(PydanticObjectId(self.deviceId))
            if device and device.roomId:
                room = await Room.get(device.roomId)
                if room:
                    await ActivityLogService.create_log(
                        action="HUMAN_DETECTED",
                        message=f"🚨 {device.name}: Human detected in room",
                        userId=None,
                        homeId=str(room.homeId),
                        log_type=LogType.WARNING
                    )
                    print(f"✅ Human detection logged for {device.name}")
        except Exception as e:
            print(f"⚠️ Error logging human detection: {e}")