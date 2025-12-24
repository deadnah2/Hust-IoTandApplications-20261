#include "WebServerManager.h"
#include "esp_http_server.h"
#include "esp_timer.h"
#include "esp_camera.h"
#include "Arduino.h"

// Define the camera server port
#define HTTP_PORT 80

static httpd_handle_t camera_httpd = NULL;

static esp_err_t jpg_httpd_handler(httpd_req_t *req){
    camera_fb_t * fb = NULL;
    esp_err_t res = ESP_OK;
    size_t fb_len = 0;
    int64_t fr_start = esp_timer_get_time();

    fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Camera capture failed");
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }
    res = httpd_resp_set_type(req, "image/jpeg");
    if(res == ESP_OK){
        res = httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg"); // Yêu cầu browser hiển thị hình ảnh thay vì tải xuống
    }

    if(res == ESP_OK){
        fb_len = fb->len;
        res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
    }
    esp_camera_fb_return(fb);
    int64_t fr_end = esp_timer_get_time();
    Serial.printf("JPG: %uB %ums\n", (uint32_t)(fb_len), (uint32_t)((fr_end - fr_start)/1000));
    return res;
}

static esp_err_t stream_handler(httpd_req_t *req){
    camera_fb_t * fb = NULL;
    esp_err_t res = ESP_OK;
    size_t _jpg_buf_len = 0;
    uint8_t * _jpg_buf = NULL;
    char part_buf[64];
    static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=frame";
    static const char* _STREAM_BOUNDARY = "\r\n--frame\r\n";
    // Multipart: nội dung bào gồm nhiều phần dữ liệu khác nhau (nhiều frame)
    // x-mixed-replace: báo cho trình duyệt biết rằng: "Khi nhận được phần dữ liệu mới, hãy (replace) phần dữ liệu cũ đang hiển thị bằng phần mới này".
    // boundary=frame: định nghĩa chuỗi ký tự dùng làm vách ngăn
    static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";
    // Content-Type: image/jpeg: Khẳng định phần dữ liệu nhỏ này là một ảnh JPEG.

    res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
    if(res != ESP_OK){
        return res;
    }

    while(true){
        fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Camera capture failed");
            res = ESP_FAIL;
        } else {
            size_t hlen = snprintf(part_buf, 64, _STREAM_PART, fb->len);
            res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
            if(res == ESP_OK) res = httpd_resp_send_chunk(req, part_buf, hlen);
            if(res == ESP_OK) res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
            
            esp_camera_fb_return(fb);
        }
        if(res != ESP_OK) break;
    }
    return res;
}

WebServerManager::WebServerManager() {
}

void WebServerManager::begin() {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = HTTP_PORT;

    httpd_uri_t jpg_uri = {
        .uri       = "/capture",
        .method    = HTTP_GET,
        .handler   = jpg_httpd_handler,
        .user_ctx  = NULL
    };
    
    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = stream_handler,
        .user_ctx  = NULL
    };

    Serial.printf("Starting web server on port: '%d'\n", config.server_port);
    if (httpd_start(&camera_httpd, &config) == ESP_OK) {
        httpd_register_uri_handler(camera_httpd, &jpg_uri);
        httpd_register_uri_handler(camera_httpd, &stream_uri);
    }
}
