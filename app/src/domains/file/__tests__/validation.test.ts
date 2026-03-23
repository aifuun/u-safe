import { describe, it, expect } from 'vitest';
import {
  FILE_SIZE_LIMITS,
  ALLOWED_EXTENSIONS,
  formatFileSize,
  getFileExtension,
  isFileTypeAllowed,
  validateFileSize,
  validateFileType,
  validateFile,
  validateFiles,
} from '../rules/validation';

describe('File Validation Rules', () => {
  describe('formatFileSize', () => {
    it('should format bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 B');
      expect(formatFileSize(1024)).toBe('1.00 KB');
      expect(formatFileSize(1024 * 1024)).toBe('1.00 MB');
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1.00 GB');
    });
  });

  describe('getFileExtension', () => {
    it('should extract file extension correctly', () => {
      expect(getFileExtension('document.pdf')).toBe('.pdf');
      expect(getFileExtension('photo.JPG')).toBe('.jpg');
      expect(getFileExtension('archive.tar.gz')).toBe('.gz');
      expect(getFileExtension('noextension')).toBe('');
    });
  });

  describe('isFileTypeAllowed', () => {
    it('should allow whitelisted file types', () => {
      expect(isFileTypeAllowed('document.pdf')).toBe(true);
      expect(isFileTypeAllowed('photo.jpg')).toBe(true);
      expect(isFileTypeAllowed('video.mp4')).toBe(true);
      expect(isFileTypeAllowed('archive.zip')).toBe(true);
    });

    it('should reject non-whitelisted file types', () => {
      expect(isFileTypeAllowed('malware.exe')).toBe(false);
      expect(isFileTypeAllowed('script.bat')).toBe(false);
      expect(isFileTypeAllowed('config.ini')).toBe(false);
    });

    it('should be case-insensitive', () => {
      expect(isFileTypeAllowed('Document.PDF')).toBe(true);
      expect(isFileTypeAllowed('PHOTO.JPG')).toBe(true);
    });
  });

  describe('validateFileSize', () => {
    it('should pass for normal file sizes', () => {
      const result = validateFileSize('test.pdf', 1024 * 1024); // 1MB
      expect(result).toBeNull();
    });

    it('should warn for large files (>2GB)', () => {
      const result = validateFileSize(
        'large.mp4',
        FILE_SIZE_LIMITS.WARNING + 1
      );
      expect(result).toMatchObject({
        reason: 'large',
        fileName: 'large.mp4',
      });
    });

    it('should error for files exceeding max size (>5GB)', () => {
      const result = validateFileSize(
        'huge.zip',
        FILE_SIZE_LIMITS.MAX + 1
      );
      expect(result).toMatchObject({
        reason: 'size',
        fileName: 'huge.zip',
      });
    });
  });

  describe('validateFileType', () => {
    it('should pass for allowed file types', () => {
      const result = validateFileType('document.pdf', 1024);
      expect(result).toBeNull();
    });

    it('should error for disallowed file types', () => {
      const result = validateFileType('malware.exe', 1024);
      expect(result).toMatchObject({
        reason: 'type',
        fileName: 'malware.exe',
      });
    });
  });

  describe('validateFile', () => {
    it('should pass validation for valid files', () => {
      const result = validateFile('document.pdf', 1024 * 1024);
      expect(result.valid).toBe(true);
      expect(result.error).toBeUndefined();
      expect(result.warning).toBeUndefined();
    });

    it('should return warning for large files', () => {
      const result = validateFile(
        'large.mp4',
        FILE_SIZE_LIMITS.WARNING + 1
      );
      expect(result.valid).toBe(true);
      expect(result.warning).toBeDefined();
      expect(result.warning?.reason).toBe('large');
    });

    it('should return error for oversized files', () => {
      const result = validateFile('huge.zip', FILE_SIZE_LIMITS.MAX + 1);
      expect(result.valid).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.error?.reason).toBe('size');
    });

    it('should return error for disallowed file types', () => {
      const result = validateFile('malware.exe', 1024);
      expect(result.valid).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.error?.reason).toBe('type');
    });
  });

  describe('validateFiles', () => {
    it('should batch validate multiple files', () => {
      const files = [
        { name: 'valid1.pdf', size: 1024 },
        { name: 'valid2.jpg', size: 2048 },
        { name: 'invalid.exe', size: 1024 },
        { name: 'huge.zip', size: FILE_SIZE_LIMITS.MAX + 1 },
      ];

      const result = validateFiles(files);

      expect(result.validFiles).toHaveLength(2);
      expect(result.validFiles).toContain('valid1.pdf');
      expect(result.validFiles).toContain('valid2.jpg');

      expect(result.errors).toHaveLength(2);
      expect(result.errors.some((e) => e.fileName === 'invalid.exe')).toBe(true);
      expect(result.errors.some((e) => e.fileName === 'huge.zip')).toBe(true);
    });

    it('should collect warnings for large files', () => {
      const files = [
        { name: 'large1.mp4', size: FILE_SIZE_LIMITS.WARNING + 1 },
        { name: 'large2.mkv', size: FILE_SIZE_LIMITS.WARNING + 1000 },
      ];

      const result = validateFiles(files);

      expect(result.validFiles).toHaveLength(2);
      expect(result.warnings).toHaveLength(2);
      expect(result.warnings.every((w) => w.reason === 'large')).toBe(true);
    });
  });
});
