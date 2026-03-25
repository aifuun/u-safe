import { describe, it, expect } from 'vitest';
import {
  getFolderIcon,
  getFileTypeIcon,
  getFileIcon,
  guessFileTypeByExtension,
  FOLDER_ICONS,
  FILE_TYPE_ICONS,
} from '../iconMap';

describe('iconMap', () => {
  describe('getFolderIcon', () => {
    it('should return collapsed icon when not expanded', () => {
      expect(getFolderIcon(false)).toBe(FOLDER_ICONS.collapsed);
      expect(getFolderIcon(false)).toBe('📁');
    });

    it('should return expanded icon when expanded', () => {
      expect(getFolderIcon(true)).toBe(FOLDER_ICONS.expanded);
      expect(getFolderIcon(true)).toBe('📂');
    });
  });

  describe('getFileTypeIcon', () => {
    it('should return correct icon for each file type', () => {
      expect(getFileTypeIcon('document')).toBe('📄');
      expect(getFileTypeIcon('image')).toBe('🖼️');
      expect(getFileTypeIcon('video')).toBe('🎬');
      expect(getFileTypeIcon('audio')).toBe('🎵');
      expect(getFileTypeIcon('archive')).toBe('📦');
      expect(getFileTypeIcon('code')).toBe('💻');
      expect(getFileTypeIcon('unknown')).toBe('📄');
    });

    it('should return unknown icon for undefined type', () => {
      expect(getFileTypeIcon(undefined)).toBe(FILE_TYPE_ICONS.unknown);
    });

    it('should return unknown icon for invalid type', () => {
      expect(getFileTypeIcon('invalid' as any)).toBe(FILE_TYPE_ICONS.unknown);
    });
  });

  describe('getFileIcon', () => {
    it('should return base icon when not encrypted', () => {
      expect(getFileIcon('document', false)).toBe('📄');
      expect(getFileIcon('image', false)).toBe('🖼️');
    });

    it('should return icon with encryption indicator when encrypted', () => {
      expect(getFileIcon('document', true)).toBe('🔒 📄');
      expect(getFileIcon('image', true)).toBe('🔒 🖼️');
    });

    it('should handle undefined file type', () => {
      expect(getFileIcon(undefined, false)).toBe('📄');
      expect(getFileIcon(undefined, true)).toBe('🔒 📄');
    });
  });

  describe('guessFileTypeByExtension', () => {
    describe('document types', () => {
      it('should recognize common document extensions', () => {
        expect(guessFileTypeByExtension('pdf')).toBe('document');
        expect(guessFileTypeByExtension('doc')).toBe('document');
        expect(guessFileTypeByExtension('docx')).toBe('document');
        expect(guessFileTypeByExtension('xls')).toBe('document');
        expect(guessFileTypeByExtension('xlsx')).toBe('document');
        expect(guessFileTypeByExtension('txt')).toBe('document');
        expect(guessFileTypeByExtension('md')).toBe('document');
      });
    });

    describe('image types', () => {
      it('should recognize common image extensions', () => {
        expect(guessFileTypeByExtension('jpg')).toBe('image');
        expect(guessFileTypeByExtension('jpeg')).toBe('image');
        expect(guessFileTypeByExtension('png')).toBe('image');
        expect(guessFileTypeByExtension('gif')).toBe('image');
        expect(guessFileTypeByExtension('webp')).toBe('image');
        expect(guessFileTypeByExtension('svg')).toBe('image');
      });
    });

    describe('video types', () => {
      it('should recognize common video extensions', () => {
        expect(guessFileTypeByExtension('mp4')).toBe('video');
        expect(guessFileTypeByExtension('avi')).toBe('video');
        expect(guessFileTypeByExtension('mkv')).toBe('video');
        expect(guessFileTypeByExtension('mov')).toBe('video');
      });
    });

    describe('audio types', () => {
      it('should recognize common audio extensions', () => {
        expect(guessFileTypeByExtension('mp3')).toBe('audio');
        expect(guessFileTypeByExtension('wav')).toBe('audio');
        expect(guessFileTypeByExtension('flac')).toBe('audio');
        expect(guessFileTypeByExtension('ogg')).toBe('audio');
      });
    });

    describe('archive types', () => {
      it('should recognize common archive extensions', () => {
        expect(guessFileTypeByExtension('zip')).toBe('archive');
        expect(guessFileTypeByExtension('rar')).toBe('archive');
        expect(guessFileTypeByExtension('7z')).toBe('archive');
        expect(guessFileTypeByExtension('tar')).toBe('archive');
        expect(guessFileTypeByExtension('gz')).toBe('archive');
      });
    });

    describe('code types', () => {
      it('should recognize common code extensions', () => {
        expect(guessFileTypeByExtension('js')).toBe('code');
        expect(guessFileTypeByExtension('ts')).toBe('code');
        expect(guessFileTypeByExtension('tsx')).toBe('code');
        expect(guessFileTypeByExtension('jsx')).toBe('code');
        expect(guessFileTypeByExtension('py')).toBe('code');
        expect(guessFileTypeByExtension('rs')).toBe('code');
        expect(guessFileTypeByExtension('go')).toBe('code');
      });
    });

    it('should be case insensitive', () => {
      expect(guessFileTypeByExtension('PDF')).toBe('document');
      expect(guessFileTypeByExtension('JPG')).toBe('image');
      expect(guessFileTypeByExtension('Mp4')).toBe('video');
    });

    it('should return unknown for undefined extension', () => {
      expect(guessFileTypeByExtension(undefined)).toBe('unknown');
    });

    it('should return unknown for unrecognized extension', () => {
      expect(guessFileTypeByExtension('xyz')).toBe('unknown');
      expect(guessFileTypeByExtension('unknown')).toBe('unknown');
    });
  });
});
