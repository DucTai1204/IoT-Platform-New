// Chuyển sang database iot_db
db = db.getSiblingDB('iot_db');

// Tạo collection devices (nếu chưa tồn tại)
db.createCollection('devices');

// // Thêm 1 document mẫu để đảm bảo database xuất hiện
// db.devices.insertOne({
//     device_id: "sample_device_001",
//     temp: 25,
//     hum: 60,
//     timestamp: new Date()
// });
