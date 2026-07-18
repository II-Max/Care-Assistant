-- ============================================
-- 🏥 Migration 001: Initial Schema
-- AI Customer Care Assistant — Bệnh viện Tim Hà Nội
-- Phase 3: Booking & Hospital Integration
-- ============================================

-- Appointments
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL DEFAULT '',
    doctor_id VARCHAR(64) NOT NULL DEFAULT '',
    department_id VARCHAR(64) NOT NULL,
    booking_date DATE NOT NULL,
    booking_time VARCHAR(10) NOT NULL,
    slot_id VARCHAR(64) NOT NULL DEFAULT '',
    schedule_id VARCHAR(64) NOT NULL DEFAULT '',
    patient_name VARCHAR(200) NOT NULL,
    patient_phone VARCHAR(20) NOT NULL,
    patient_email VARCHAR(200) DEFAULT '',
    symptoms TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    is_bhyt INTEGER DEFAULT 0,
    idempotency_key VARCHAR(64) UNIQUE,
    source VARCHAR(32) DEFAULT 'ai_chat',
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed', 'no_show')),
    cancel_reason TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_appointments_phone ON appointments(patient_phone);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(booking_date);
CREATE INDEX IF NOT EXISTS idx_appointments_idempotency ON appointments(idempotency_key);

-- Doctors
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id VARCHAR(64) PRIMARY KEY,
    department_id VARCHAR(64) NOT NULL,
    name VARCHAR(200) NOT NULL,
    title VARCHAR(200) DEFAULT '',
    specialization TEXT DEFAULT '',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_doctors_dept ON doctors(department_id);

-- Schedules
CREATE TABLE IF NOT EXISTS schedules (
    schedule_id VARCHAR(64) PRIMARY KEY,
    doctor_id VARCHAR(64) NOT NULL,
    department_id VARCHAR(64) NOT NULL,
    work_date DATE NOT NULL,
    is_available INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doctor_id, work_date)
);

CREATE INDEX IF NOT EXISTS idx_schedules_date ON schedules(work_date);
CREATE INDEX IF NOT EXISTS idx_schedules_doctor ON schedules(doctor_id);

-- Time Slots (optimistic locking via version column)
CREATE TABLE IF NOT EXISTS time_slots (
    slot_id VARCHAR(64) PRIMARY KEY,
    doctor_id VARCHAR(64) NOT NULL,
    schedule_id VARCHAR(64) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_booked INTEGER DEFAULT 0,
    booked_by VARCHAR(64) DEFAULT NULL,
    version INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(schedule_id, start_time)
);

CREATE INDEX IF NOT EXISTS idx_slots_schedule ON time_slots(schedule_id);
CREATE INDEX IF NOT EXISTS idx_slots_booked ON time_slots(is_booked);

-- Notification Queue
CREATE TABLE IF NOT EXISTS notification_queue (
    notification_id VARCHAR(64) PRIMARY KEY,
    appointment_id VARCHAR(64) NOT NULL,
    channel VARCHAR(20) NOT NULL
        CHECK (channel IN ('sms', 'zalo', 'email', 'push')),
    recipient VARCHAR(200) NOT NULL,
    template VARCHAR(64) NOT NULL,
    params TEXT DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'sent', 'failed', 'cancelled')),
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT DEFAULT NULL,
    scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notif_status ON notification_queue(status);
CREATE INDEX IF NOT EXISTS idx_notif_appointment ON notification_queue(appointment_id);

-- Audit Events
CREATE TABLE IF NOT EXISTS audit_events (
    event_id VARCHAR(64) PRIMARY KEY,
    event_type VARCHAR(32) NOT NULL,
    appointment_id VARCHAR(64) DEFAULT NULL,
    user_id VARCHAR(64) DEFAULT '',
    actor_role VARCHAR(32) DEFAULT 'patient',
    details TEXT DEFAULT '{}',
    ip_address VARCHAR(64) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_type ON audit_events(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_appointment ON audit_events(appointment_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_events(created_at);

-- Feedback
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id VARCHAR(64) NOT NULL,
    message_id VARCHAR(64) DEFAULT '',
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT DEFAULT '',
    category VARCHAR(32) DEFAULT 'general',
    user_ip_hash VARCHAR(64) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Seed Data: Departments
-- ============================================
INSERT OR IGNORE INTO audit_events (event_id, event_type, details)
VALUES ('seed_departments_v1', 'schema_migration', '{"version": "001", "description": "Initial schema with departments seed data"}');
