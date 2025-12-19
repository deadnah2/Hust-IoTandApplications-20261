# Smart Home IoT – Backend API Spec (MongoDB)

Tài liệu này mô tả các API mà FE (`web/services/api.ts`) đang dùng.  
Các endpoint có dấu `*` là đề xuất thêm để “đủ bài/đúng kiến trúc”, FE hiện có thể chưa gọi hoặc chỉ placeholder.

## 0) Quy ước chung

- **Base URL**: `http(s)://{host}:{port}`
- **Prefix**: tất cả endpoint dưới đây đều bắt đầu bằng `/api/...`
- **Auth**: dùng JWT Bearer
  - Header: `Authorization: Bearer <id_token>`
  - FE đang lưu token ở `localStorage` key `id_token`
- **ID**: dùng MongoDB ObjectId dạng string (ví dụ `"657d...e12"`)
- **Content-Type**: `application/json`
- **Timezone**: ISO8601 UTC (`new Date().toISOString()`)

### Error format (khuyến nghị)
Trả về thống nhất để FE dễ xử lý:
```json
{
  "error": "BadRequest",
  "message": "Room not found",
  "details": { "field": "homeId" }
}
```

HTTP status:
- `200` OK, `201` Created, `204` No Content
- `400` invalid input, `401` unauthorized, `403` forbidden, `404` not found, `409` conflict

## 1) Models (MongoDB collections)

### users
```ts
{
  _id: ObjectId,
  login: string,           // unique
  email?: string,          // unique (optional nếu bài yêu cầu)
  passwordHash: string,
  createdAt: string
}
```
Index: `login` unique, `email` unique.

### homes
```ts
{
  _id: ObjectId,
  ownerUserId: ObjectId,   // ref users
  name: string,
  location?: string,
  createdAt: string,
  updatedAt: string
}
```
Index: `ownerUserId`.

### rooms
```ts
{
  _id: ObjectId,
  homeId: ObjectId,        // ref homes
  name: string,
  createdAt: string,
  updatedAt: string
}
```
Index: `homeId`.

### devices
```ts
{
  _id: ObjectId,
  roomId?: ObjectId,        // ref rooms
  name: string,
  type: "LIGHT" | "FAN" | "CAMERA",
  status: "ON" | "OFF",
  speed?: number,          // FAN: 0..3
  streamUrl?: string,      // CAMERA: optional, nếu có HLS/WebRTC url
  humanDetectionEnabled?: boolean,
  createdAt: string,
  updatedAt: string
}
```
Index: `roomId`.

### activity_logs *
```ts
{
  _id: ObjectId,
  userId: ObjectId,
  homeId?: ObjectId,
  roomId?: ObjectId,
  deviceId?: ObjectId,
  type: "INFO" | "WARNING" | "ERROR",
  message: string,
  timestamp: string
}
```
Index: `roomId + timestamp desc`, `deviceId + timestamp desc`.

### camera_recordings *
```ts
{
  _id: ObjectId,
  deviceId: ObjectId,      // ref devices (type CAMERA)
  startedAt: string,
  durationSec: number,
  playbackUrl: string
}
```
Index: `deviceId + startedAt desc`.

## 2) Auth / Account

### POST `/api/authenticate`
Login, trả JWT.
- Req:
```json
{ "username": "admin", "password": "admin" }
```
- Res (tối thiểu FE cần):
```json
{ "id_token": "jwt..." }
```
- Res (khuyến nghị để đúng `types.ts`):
```json
{ "id_token": "jwt...", "user": { "id": "u1", "login": "admin", "email": "admin@..." } }
```

### POST `/api/register`
- Req:
```json
{ "login": "alice", "email": "alice@mail.com", "password": "1234" }
```
- Res: `201` (body `{}` hoặc user)

### GET `/api/account`
(Bearer)
- Res:
```json
{ "id": "u1", "login": "admin", "email": "admin@..." }
```

### POST `/api/account` *
(Bearer) update profile
- Req:
```json
{ "email": "new@mail.com" }
```
- Res: user updated

### POST `/api/account/change-password` *
(Bearer)
- Req:
```json
{ "currentPassword": "old", "newPassword": "new" }
```
- Res: `200/201`

## 3) Homes

### GET `/api/homes`
(Bearer) list homes của user hiện tại
- Res:
```json
[
  { "id": "h1", "name": "MyHome", "location": "Ha Noi" }
]
```

### POST `/api/homes`
(Bearer)
- Req:
```json
{ "name": "MyHome", "location": "Ha Noi" }
```
- Res:
```json
{ "id": "h1", "name": "MyHome", "location": "Ha Noi" }
```

### PUT `/api/homes/:id` *
(Bearer)
- Req:
```json
{ "name": "MyHome 2", "location": "HN" }
```
- Res: `House`

### DELETE `/api/homes/:id` *
(Bearer)
- Res: `204`
- Quy ước: có thể cascade xoá rooms/devices hoặc chặn nếu còn dữ liệu (tuỳ BE quyết).

## 4) Rooms

### GET `/api/rooms?homeId={homeId}`
(Bearer) list rooms theo house
- Res:
```json
[
  { "id": "r1", "homeId": "h1", "name": "Room 1" }
]
```

### POST `/api/rooms`
(Bearer)
- Req:
```json
{ "homeId": "h1", "name": "Room 1" }
```
- Res: `Room`

### PUT `/api/rooms/:id` *
(Bearer)
- Req:
```json
{ "name": "Living room" }
```
- Res: `Room`

### DELETE `/api/rooms/:id?homeId={homeId}`
(Bearer)
- Res: `204`
- BE **phải verify**: room thuộc `homeId` và home thuộc user.

> Gợi ý: có thể support thêm `DELETE /api/rooms/:id` (không query) nhưng vẫn phải lookup `room.homeId` để verify ownership.

## 5) Devices (Room → Device)

### GET `/api/devices?roomId={roomId}`
(Bearer)
- Res:
```json
[
  { "id": "d2", "roomId": "r1", "name": "Ceiling Light", "type": "LIGHT", "status": "OFF" }
]
```

### POST `/api/devices`
(Bearer)
- Req:
```json
{ "roomId": "r1", "name": "Ceiling Light", "type": "LIGHT" }
```
- Res: `Device` (tạo mới nên set mặc định `status="OFF"`, `speed=0` nếu FAN)

### PUT `/api/devices/:id` *
(Bearer) update name/streamUrl...
- Req:
```json
{ "name": "Light 1", "streamUrl": "" } // cân nhắc việc FE stream trực tiếp.
```
- Res: `Device`

### DELETE `/api/devices/:id`
(Bearer)
- Res: `204`

## 6) Device Control (MQTT bridge)

### POST `/api/devices/:id/command`
(Bearer)
- Req:
```json
{ "action": "ON" }
```
hoặc
```json
{ "action": "SET_SPEED", "speed": 2 }
```
- Res: `{ "ok": true }` (hoặc trả `Device` mới)

Validation:
- `action` ∈ `ON|OFF|SET_SPEED`
- Nếu `SET_SPEED` thì `speed` bắt buộc và trong `0..3`
- Nếu `type !== FAN` mà `SET_SPEED` → `400`

Side effects (khuyến nghị):
- Update DB: `status`, `speed`, `updatedAt`
- Ghi `activity_logs` *
- Publish MQTT (nếu có):
  - topic đề xuất: `homes/{homeId}/rooms/{roomId}/devices/{deviceId}/command`
  - payload: `{ deviceId, action, speed?, time, creator }`

## 7) Camera (mục này có vẻ không cần nữa)

### POST `/api/cameras/:id/human-detection`
(Bearer)
- Req:
```json
{ "enabled": true }
```
- Res: `{ "ok": true }` hoặc trả `Device/Camera`
- Side effects: update `devices.humanDetectionEnabled`, log event *

### GET `/api/cameras?roomId={roomId}` *
(Bearer) list camera devices theo room
- Res: danh sách camera (có thể reuse `Device` type CAMERA)

### GET `/api/cameras/:id/stream` *
(Bearer)
- Res:
```json
{ "type": "HLS", "url": "https://.../index.m3u8" }
```
Ghi chú: browser FE không play RTSP trực tiếp; ưu tiên HLS/WebRTC.

### GET `/api/cameras/:id/recordings` *
(Bearer)
- Res:
```json
[
  { "id": "rec1", "startedAt": "2025-12-17T12:00:00.000Z", "durationSec": 60, "playbackUrl": "https://.../rec1.mp4" }
]
```

## 8) Activity Logs *

### GET `/api/logs?roomId={roomId}&limit=50`
(Bearer)
- Res:
```json
[
  { "id": "l1", "timestamp": "2025-12-17T12:00:00.000Z", "message": "Fan speed set to 2", "type": "INFO" }
]
```

### POST `/api/logs` *
(Bearer/admin hoặc internal)
- Req:
```json
{ "type": "INFO", "message": "System initialized", "roomId": "r1", "deviceId": "d1" }
```

## 9) CORS / Mobile

- Web chạy trên Vite dev server (thường `http://localhost:5173`), cần CORS.
- Android emulator gọi backend bằng `http://10.0.2.2:{port}`.

## 10) Notes để khớp FE hiện tại

- FE đang gọi:
  - `DELETE /api/rooms/:id?homeId=...` (đã sửa để gửi `homeId` nếu có)
  - `GET /api/devices?roomId=...`
  - `POST /api/devices/:id/command`
  - `POST /api/cameras/:id/human-detection`
- Nếu BE làm khác path/query, FE sẽ phải đổi trong `web/services/api.ts`.

