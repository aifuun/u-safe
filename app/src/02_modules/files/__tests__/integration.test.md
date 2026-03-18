# File Management Integration Tests

## Overview

Integration tests for Phase 3 (M3) File Management module.

## Test Scenarios

### Scenario 1: Complete Encryption/Decryption Flow

**Steps:**
1. Launch application
2. Select a test directory containing sample files
3. File tree loads and displays correctly
4. Right-click on a `.txt` file
5. Select "加密" from context menu
6. Enter password "test123"
7. Verify encrypted file appears with `.enc` extension
8. Verify 🔒 icon displays on encrypted file
9. Right-click encrypted file
10. Select "解密" from context menu
11. Enter password "test123"
12. Verify decrypted file appears without `.enc` extension
13. Verify file content matches original

**Expected Results:**
- ✅ File tree renders in < 1 second
- ✅ Encryption progress displayed
- ✅ Decryption progress displayed
- ✅ Original and decrypted content match
- ✅ Error handling for wrong password

### Scenario 2: Large Directory Performance

**Steps:**
1. Create test directory with 1000 files
2. Load file tree via `scan_file_tree` IPC
3. Measure load time
4. Expand/collapse directories
5. Scroll through file list

**Expected Results:**
- ✅ Initial scan completes in < 500ms
- ✅ Render completes in < 1 second
- ✅ UI remains responsive during interactions
- ✅ No memory leaks after multiple loads

### Scenario 3: File Type Detection

**Steps:**
1. Create directory with various file types:
   - `document.pdf`
   - `image.jpg`
   - `video.mp4`
   - `audio.mp3`
   - `archive.zip`
   - `code.rs`
2. Load file tree
3. Verify each file displays correct icon

**Expected Results:**
- ✅ PDF shows 📄 (document icon)
- ✅ JPG shows 🖼️ (image icon)
- ✅ MP4 shows 🎬 (video icon)
- ✅ MP3 shows 🎵 (audio icon)
- ✅ ZIP shows 📦 (archive icon)
- ✅ RS shows 💻 (code icon)

### Scenario 4: Context Menu Interactions

**Steps:**
1. Load file tree
2. Right-click on file (not encrypted)
3. Verify menu shows: 加密, 重命名, 删除
4. Right-click on file (encrypted)
5. Verify menu shows: 解密, 重命名, 删除
6. Click outside menu
7. Verify menu closes
8. Press ESC key while menu open
9. Verify menu closes

**Expected Results:**
- ✅ Menu shows correct operations based on file state
- ✅ Click outside closes menu
- ✅ ESC key closes menu
- ✅ Keyboard navigation works

### Scenario 5: Error Handling

**Test Cases:**
1. **Nonexistent path**
   - Input: `/nonexistent/path`
   - Expected: Error message "路径不存在"

2. **Permission denied**
   - Input: Protected system directory (macOS: `/System`)
   - Expected: Skip inaccessible files, log warning, continue

3. **Wrong decryption password**
   - Input: Encrypted file + wrong password
   - Expected: Error message "解密失败: MAC 验证失败"

4. **Corrupted encrypted file**
   - Input: Manually corrupted `.enc` file
   - Expected: Error message "解密失败"

**Expected Results:**
- ✅ All error cases handled gracefully
- ✅ User receives clear error messages
- ✅ Application doesn't crash
- ✅ Can retry operation after error

## Manual Testing Checklist

- [ ] File tree loads without errors
- [ ] Expand/collapse works smoothly
- [ ] File selection highlights correctly
- [ ] Right-click menu appears at cursor position
- [ ] Encrypt operation completes successfully
- [ ] Decrypt operation completes successfully
- [ ] Progress bars update during operations
- [ ] Encrypted files show 🔒 indicator
- [ ] File type icons display correctly
- [ ] Performance acceptable with 1000+ files
- [ ] Error messages are user-friendly
- [ ] No console errors during normal operation

## Automated Test Commands

```bash
# Run Rust unit tests
cd src-tauri
cargo test

# Run TypeScript unit tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test iconMap.test.ts
```

## Performance Benchmarks

| Metric | Target | Actual |
|--------|--------|--------|
| Scan 1000 files | < 500ms | TBD |
| Render 1000 files | < 1s | TBD |
| Encrypt 10MB file | < 2s | TBD |
| Decrypt 10MB file | < 2s | TBD |

## Notes

- Integration tests require full Tauri environment
- Run manual tests in dev mode: `npm run tauri dev`
- Performance tests should run on production build
- Test on both macOS and Windows (if applicable)
