-- ============================================
-- 🏥 Migration 002: Seed Data
-- AI Customer Care Assistant — Bệnh viện Tim Hà Nội
-- ============================================

-- Departments (7 chuyên khoa)
CREATE TABLE IF NOT EXISTS departments (
    department_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    icon VARCHAR(10) DEFAULT '🏥',
    is_active INTEGER DEFAULT 1
);

INSERT OR IGNORE INTO departments (department_id, name, description, icon) VALUES
('noi-khoa', 'Nội khoa Tim mạch', 'Chẩn đoán, điều trị nội khoa Tim mạch. Siêu âm tim Doppler 2D/4D, Holter điện tim, Holter huyết áp, Nghiệm pháp gắng sức.', '🫀'),
('can-thiep', 'Tim mạch Can thiệp', 'Lĩnh vực mạnh nhất. Can thiệp động mạch vành, nong van hai lá, stent graft ĐMC, thay van ĐMC qua da, điện sinh lý tim.', '💉'),
('phau-thuat', 'Phẫu thuật Tim mạch', 'Đứng đầu cả nước về phẫu thuật tim hở. Sửa van, thay van, bắc cầu ĐMV. Phẫu thuật cho bệnh nhi từ 2kg.', '🔬'),
('nhi-khoa', 'Nhi khoa Tim mạch', 'Đơn vị tim mạch nhi hoàn chỉnh. Chẩn đoán và điều trị hầu hết các bệnh tim bẩm sinh phức tạp ở trẻ em và sơ sinh.', '👶'),
('chuyen-hoa', 'Tim mạch Chuyển hóa', 'Khám và điều trị đái tháo đường, rối loạn mỡ máu. Phòng khám bàn chân đái tháo đường chuyên biệt.', '🧬'),
('duoc', 'Khoa Dược & Hiệu thuốc', 'Cung ứng thuốc chất lượng cao, tư vấn sử dụng thuốc, cấp phát thuốc BHYT.', '💊'),
('tong-quat', 'Khám bệnh Tổng quát', 'Khám sức khỏe tổng quát, khám sức khỏe định kỳ cho cá nhân và doanh nghiệp.', '🏥');

-- Doctors (sample data)
INSERT OR IGNORE INTO doctors (doctor_id, department_id, name, title, specialization) VALUES
('bs-hoang-van', 'can-thiep', 'TS.BS Hoàng Văn', 'Phó Giám đốc', 'Can thiệp động mạch vành, TAVI, điện sinh lý tim'),
('bs-nguyen-van-a', 'noi-khoa', 'BS.CKII Nguyễn Văn An', 'Trưởng khoa Nội', 'Siêu âm tim, tăng huyết áp, suy tim'),
('bs-tran-thi-b', 'phau-thuat', 'TS.BS Trần Thị Bình', 'Trưởng khoa Phẫu thuật', 'Phẫu thuật tim hở, tim bẩm sinh'),
('bs-le-van-c', 'nhi-khoa', 'BS.CKII Lê Văn Cường', 'Trưởng khoa Nhi', 'Tim bẩm sinh trẻ em, siêu âm tim thai'),
('bs-pham-van-d', 'chuyen-hoa', 'BS.CKII Phạm Văn Dũng', 'Trưởng khoa Chuyển hóa', 'Đái tháo đường, rối loạn mỡ máu');

-- Schedules (next 30 days for each doctor)
INSERT OR IGNORE INTO schedules (schedule_id, doctor_id, department_id, work_date, is_available)
SELECT 
    'schedule_' || d.doctor_id || '_' || strftime('%Y%m%d', date('now', '+' || n.n || ' days')),
    d.doctor_id,
    d.department_id,
    date('now', '+' || n.n || ' days'),
    1
FROM (SELECT doctor_id, department_id FROM doctors) d
CROSS JOIN (
    SELECT 0 AS n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
    UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9
    UNION SELECT 10 UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14
    UNION SELECT 15 UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19
    UNION SELECT 20 UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24
    UNION SELECT 25 UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29
) n
WHERE strftime('%w', date('now', '+' || n.n || ' days')) NOT IN ('0');  -- Không có Chủ nhật

-- Time slots for each schedule
INSERT OR IGNORE INTO time_slots (slot_id, doctor_id, schedule_id, start_time, end_time, is_booked)
SELECT 
    'slot_' || s.schedule_id || '_' || REPLACE(t.time_val, ':', ''),
    s.doctor_id,
    s.schedule_id,
    t.time_val,
    time(t.time_val, '+30 minutes'),
    0
FROM schedules s
CROSS JOIN (
    SELECT '07:30' AS time_val UNION SELECT '08:00' UNION SELECT '08:30'
    UNION SELECT '09:00' UNION SELECT '09:30' UNION SELECT '10:00'
    UNION SELECT '10:30' UNION SELECT '11:00' UNION SELECT '13:30'
    UNION SELECT '14:00' UNION SELECT '14:30' UNION SELECT '15:00'
    UNION SELECT '15:30'
) t
WHERE s.is_available = 1;
