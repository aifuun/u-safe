# Password Reset Feature - Testing Guide

## Overview

This document provides a comprehensive testing guide for the password reset feature (Issue #40).

## Prerequisites

Before testing, ensure:
- [ ] Backend (Rust) compiles without errors
- [ ] Frontend (React) builds successfully
- [ ] Application runs with `npm run tauri dev`

## Test Scenarios

### Scenario 1: Complete Reset Flow (Happy Path)

**Setup:**
1. Create a test database with some encrypted files and tags
2. Set a master password (e.g., "OldPassword123")

**Test Steps:**
1. Open the application
2. Enter wrong password 3 times to trigger lockout (optional)
3. Click "重置密码并清空数据" button on login page
4. **Verify Warning Page:**
   - [ ] Shows correct encrypted files count
   - [ ] Shows correct total files count
   - [ ] Shows correct tags count
   - [ ] Shows database size
   - [ ] "取消" button returns to login page
5. Click "我了解风险，继续" button
6. **Verify Confirm Page:**
   - [ ] Two checkboxes are unchecked by default
   - [ ] "DELETE" text input is empty
   - [ ] "确认重置并清空数据" button is disabled
7. Check both checkboxes
8. Type "DELETE" (uppercase) in text input
   - [ ] Button becomes enabled after all conditions met
   - [ ] Typing wrong text (e.g., "delete", "Delete") shows validation hint
9. Click "确认重置并清空数据" button
10. **Verify Reset Execution:**
    - [ ] Console shows "[reset:app] 开始应用重置" log
    - [ ] Console shows "[reset:archive_db] 归档数据库" log
    - [ ] Console shows "[reset:delete_hash] 删除密码文件" log
    - [ ] Console shows "[reset:clear_db] 清空数据库表" log
    - [ ] Console shows "[reset:app] 应用重置完成" log
11. **Verify Post-Reset State:**
    - [ ] App redirects to `/setup` page
    - [ ] localStorage is cleared
    - [ ] Can set a new password
    - [ ] New password works for login

### Scenario 2: Verify Database Backup

**Test Steps:**
1. Complete Scenario 1
2. Navigate to data directory:
   - macOS: `~/Library/Application Support/.u-safe/`
   - Windows: `%APPDATA%\.u-safe\`
   - Linux: `~/.local/share/.u-safe/`
3. **Verify Backup Files:**
   - [ ] `metadata.db.backup` file exists
   - [ ] File size > 0
   - [ ] File modified timestamp matches reset time
   - [ ] Original `metadata.db` exists and is empty/clean

### Scenario 3: Verify Password Hash Deletion

**Test Steps:**
1. Complete Scenario 1
2. Navigate to keys directory:
   - macOS: `~/Library/Application Support/.u-safe/keys/`
3. **Verify Password File:**
   - [ ] `password.hash` file is deleted
   - [ ] Directory still exists (not deleted)

### Scenario 4: Cancel at Warning Page

**Test Steps:**
1. Navigate to login page
2. Click "重置密码并清空数据" button
3. On warning page, click "取消" button
4. **Verify:**
   - [ ] Returns to login page
   - [ ] No data is deleted
   - [ ] Password hash file still exists
   - [ ] Can still login with old password

### Scenario 5: Cancel at Confirm Page

**Test Steps:**
1. Navigate to reset-confirm page
2. Click "取消" button
3. **Verify:**
   - [ ] Returns to login page
   - [ ] No data is deleted
   - [ ] Can still login with old password

### Scenario 6: Validation Tests

**Test Steps:**
1. Navigate to reset-confirm page
2. **Test Checkbox Validation:**
   - [ ] Button disabled when no checkboxes checked
   - [ ] Button disabled when only one checkbox checked
   - [ ] Button disabled when both checked but text input empty
3. **Test Text Input Validation:**
   - [ ] Type "delete" → validation hint shows
   - [ ] Type "Delete" → validation hint shows
   - [ ] Type "DEL" → validation hint shows
   - [ ] Type "DELETE" → validation hint disappears
   - [ ] Button only enables when all conditions met

### Scenario 7: Error Handling

**Test Steps:**
1. **Test Backend Error:**
   - Stop database service (if external)
   - Try to execute reset
   - [ ] Error message displayed
   - [ ] No navigation occurs
   - [ ] User can retry or cancel
2. **Test Network/IPC Error:**
   - Simulate IPC failure (modify invoke call to fail)
   - [ ] Error displayed
   - [ ] State remains consistent

### Scenario 8: Re-setup After Reset

**Test Steps:**
1. Complete full reset
2. On setup page, create new password (e.g., "NewPassword456")
3. **Verify:**
   - [ ] New password is saved
   - [ ] Can login with new password
   - [ ] Cannot login with old password
   - [ ] App works normally after reset

## Manual Verification Checklist

After running all scenarios, verify:

### Backend Logs
- [ ] All reset operations logged with `[reset:*]` prefix
- [ ] No error logs during successful reset
- [ ] Warning logs for critical operations

### Frontend Behavior
- [ ] All UI transitions smooth
- [ ] No console errors in browser DevTools
- [ ] Buttons have correct hover/focus states
- [ ] Accessibility: keyboard navigation works

### Data Integrity
- [ ] Database backup is valid SQLite file
- [ ] Can open backup with SQLite browser
- [ ] Backup contains old data
- [ ] New database is clean after reset

### Security
- [ ] Password hash is completely removed
- [ ] No sensitive data in logs
- [ ] Cannot recover old password after reset
- [ ] Multiple confirmations prevent accidental reset

## Performance Tests

### Load Statistics Page
- [ ] Loads in < 1 second with 1000 files
- [ ] Loads in < 2 seconds with 10000 files

### Reset Execution
- [ ] Completes in < 5 seconds with 1000 files
- [ ] Completes in < 10 seconds with 10000 files

## Edge Cases

### Large Database
- [ ] Reset works with 100MB+ database
- [ ] Backup creation doesn't timeout

### Empty Database
- [ ] Reset works with no files/tags
- [ ] Statistics show 0 for all counts

### Partial Data
- [ ] Reset works with files but no tags
- [ ] Reset works with tags but no files

## Browser Compatibility (if web view)

Test on:
- [ ] Chrome-based (Edge, Arc)
- [ ] Firefox
- [ ] Safari (macOS only)

## Platform Tests

Test on:
- [ ] macOS (Intel)
- [ ] macOS (Apple Silicon)
- [ ] Windows 10/11
- [ ] Linux (Ubuntu/Debian)

## Regression Tests

After reset, verify these features still work:
- [ ] Create new encrypted file
- [ ] Create new tag
- [ ] File tree view loads
- [ ] Settings page works

## Known Issues

None currently documented.

## Test Results

### Test Run 1: [Date]
- Tester: [Name]
- Platform: [OS]
- Result: [Pass/Fail]
- Notes: [Any observations]

### Test Run 2: [Date]
- Tester: [Name]
- Platform: [OS]
- Result: [Pass/Fail]
- Notes: [Any observations]

## Next Steps

After all tests pass:
1. Update user documentation
2. Create PR for review
3. Merge to main branch
4. Update release notes
