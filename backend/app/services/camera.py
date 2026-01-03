import cv2
import threading
import queue
import time
from ultralytics import YOLO


class CameraStream:
    def __init__(self, cameraUrl, frameQueueSize=4, humanDetectionMode=False):
        """
        Khởi tạo CameraStream.

        :param cameraUrl: URL của camera stream (ví dụ: http://192.168.1.100:80/stream)
        :param frameQueueSize: Kích thước tối đa của queue lưu frame (mặc định 4)
        :param humanDetectionMode: Bật/tắt chế độ phát hiện người (mặc định False)
        """
        self.cameraUrl = cameraUrl
        self.frameQueue = queue.Queue(maxsize=frameQueueSize)
        self.humanDetectionMode = humanDetectionMode

        # Biến thread
        self.captureThread = None
        self.detectionThread = None
        self.running = False

        self.processedFrame = None
        self.frameLock = threading.Lock()
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
        self.running = False
        if self.captureThread:
            self.captureThread.join(timeout=2)
        if self.detectionThread:
            self.detectionThread.join(timeout=2)
        print("CameraStream stopped")

    def get_processed_frame(self):
        """Lấy frame đã được xử lý (processed frame) từ bên ngoài."""
        with self.frameLock:  # Đồng bộ truy cập
            return self.processedFrame.copy() if self.processedFrame is not None else None

    def _capture_frames(self):
        """Luồng lấy frame từ cameraUrl và put vào queue."""
        cap = cv2.VideoCapture(self.cameraUrl)
        if not cap.isOpened():
            print(f"Cannot open camera stream: {self.cameraUrl}")
            return

        while self.running:
            start_capture = time.time()
            ret, frame = cap.read()
            capture_time = time.time() - start_capture
            if ret:
                print(f"Captured frame at {time.strftime('%H:%M:%S', time.localtime())}, took {capture_time:.4f} seconds")
                print(f"Queue size after capture: {self.frameQueue.qsize()}")
                try:
                    self.frameQueue.put(frame, timeout=1)  # Đặt timeout để không block vĩnh viễn
                except queue.Full:
                    # Nếu queue đầy, bỏ frame cũ nhất và thêm frame mới
                    try:
                        self.frameQueue.get_nowait()
                        self.frameQueue.put(frame)
                    except queue.Empty:
                        pass
            else:
                print("Failed to capture frame")
                time.sleep(0.05)  # Tránh loop quá nhanh

        cap.release()

    def _detect_humans(self):
        """Luồng thực hiện detection trên frame từ queue."""
        while self.running:
            try:
                frame = self.frameQueue.get(timeout=1)
                start_detect = time.time()
                processed_frame = frame.copy()  # Sao chép frame để xử lý

                if self.humanDetectionMode and self.model:
                    # Chạy YOLO detection
                    results = self.model(processed_frame, classes=[0])  # Chỉ detect class 'person' (0 trong COCO)

                    # Xử lý kết quả và vẽ bounding box
                    human_detected = False # xem trong ảnh có người không
                    for result in results:
                        for box in result.boxes:
                            if box.cls == 0:  # person
                                human_detected = True
                                # Vẽ bounding box
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                cv2.rectangle(processed_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                cv2.putText(processed_frame, "Person", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    if human_detected:
                        print("Human detected!") # Dùng MQTT để gửi cho server
                # if self.humanDetectionMode:
                #     self.model = YOLO('yolov8n.pt')
                # else:
                #     self.model = None 

                detect_time = time.time() - start_detect
                print(f"Detected frame at {time.strftime('%H:%M:%S', time.localtime())}, took {detect_time:.4f} seconds")

                # Lưu processed frame
                with self.frameLock:
                    self.processedFrame = processed_frame

            except queue.Empty:
                continue