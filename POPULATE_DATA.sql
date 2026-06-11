-- =====================================================
-- Beat Plan Pro - Initial Data Setup
-- Run this in Supabase SQL Editor to populate test data
-- =====================================================

-- Clear existing data (optional - uncomment if needed)
-- DELETE FROM planned_visits WHERE id != -1;
-- DELETE FROM gst_master WHERE id != -1;
-- DELETE FROM employee_master WHERE id != -1;
-- DELETE FROM admin_master WHERE id != -1;

-- =====================================================
-- 1. ADD ADMIN CREDENTIALS
-- =====================================================
INSERT INTO admin_master (Username, Password) VALUES
  ('admin', 'admin123'),
  ('manager', 'manager123')
ON CONFLICT (Username) DO NOTHING;

-- =====================================================
-- 2. ADD TEST EMPLOYEES
-- =====================================================
INSERT INTO employee_master (EmployeeCode, EmployeeName, Password) VALUES
  ('EMP001', 'John Doe', 'john123'),
  ('EMP002', 'Jane Smith', 'jane123'),
  ('EMP003', 'Mike Johnson', 'mike123')
ON CONFLICT (EmployeeCode) DO NOTHING;

-- =====================================================
-- 3. ADD TEST STORES
-- =====================================================
INSERT INTO gst_master (StoreID, StoreName, GSTNumber, City, EmployeeCode) VALUES
  ('S00001', 'Store A - Mumbai', '27AABCS1234D2Z5', 'Mumbai', 'EMP001'),
  ('S00002', 'Store B - Mumbai', '27AABCS1234D2Z6', 'Mumbai', 'EMP001'),
  ('S00003', 'Store C - Delhi', '27AABCS1234D2Z7', 'Delhi', 'EMP002'),
  ('S00004', 'Store D - Delhi', '27AABCS1234D2Z8', 'Delhi', 'EMP002'),
  ('S00005', 'Store E - Bangalore', '27AABCS1234D2Z9', 'Bangalore', 'EMP003'),
  ('S00006', 'Store F - Pune', '27AABCS1234E2Z0', 'Pune', 'EMP003')
ON CONFLICT (StoreID) DO NOTHING;

-- =====================================================
-- 4. VERIFY DATA (SELECT queries to check)
-- =====================================================

-- Check admins
SELECT 'ADMIN ACCOUNTS' as category, COUNT(*) as count FROM admin_master;

-- Check employees
SELECT 'EMPLOYEES' as category, COUNT(*) as count FROM employee_master;

-- Check stores
SELECT 'STORES' as category, COUNT(*) as count FROM gst_master;

-- See all admins
SELECT 'Admin Credentials:' as info, Username, Password FROM admin_master;

-- See all employees
SELECT 'Employee Credentials:' as info, EmployeeCode, EmployeeName, Password FROM employee_master;

-- See all stores with their assigned employees
SELECT StoreName, City, GSTNumber, EmployeeCode FROM gst_master ORDER BY City;

-- =====================================================
-- ✅ NOW YOU CAN LOGIN WITH:
-- =====================================================
-- Admin Login:
--   Username: admin
--   Password: admin123
--
-- Employee Login:
--   Code: EMP001
--   Password: john123
-- =====================================================
