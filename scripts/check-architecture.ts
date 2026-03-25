#!/usr/bin/env tsx

/**
 * Architecture Check Script
 *
 * 检测架构违规：
 * 1. 循环依赖 (Circular Dependencies)
 * 2. 层级边界违规 (Layer Boundary Violations)
 * 3. 深度导入 (Deep Imports)
 */

import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

// ========================================
// Configuration
// ========================================

// ES module compatibility
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

interface ArchitectureConfig {
  rootDir: string;
  sourceDir: string;
  layers: {
    kernel: string[];
    domains: string[];
    modules: string[];
    views: string[];
  };
}

const config: ArchitectureConfig = {
  rootDir: path.resolve(__dirname, '..'),
  sourceDir: path.resolve(__dirname, '../app/src'),
  layers: {
    kernel: ['kernel'],
    domains: ['domains'],
    modules: ['modules'],
    views: ['views'],
  },
};

// ========================================
// Types
// ========================================

interface ImportStatement {
  file: string;
  line: number;
  importPath: string;
  resolvedPath: string;
}

interface Violation {
  type: 'circular' | 'layer-boundary' | 'deep-import';
  file: string;
  line?: number;
  message: string;
  details?: any;
}

// ========================================
// Utility Functions
// ========================================

/**
 * 获取所有 TypeScript 文件
 */
function getAllTypeScriptFiles(dir: string): string[] {
  const files: string[] = [];

  function traverse(currentDir: string) {
    const entries = fs.readdirSync(currentDir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);

      if (entry.isDirectory()) {
        // 跳过 node_modules
        if (entry.name === 'node_modules') continue;
        traverse(fullPath);
      } else if (entry.isFile() && /\.(ts|tsx)$/.test(entry.name)) {
        files.push(fullPath);
      }
    }
  }

  traverse(dir);
  return files;
}

/**
 * 解析文件中的导入语句
 */
function parseImports(file: string): ImportStatement[] {
  const content = fs.readFileSync(file, 'utf-8');
  const lines = content.split('\n');
  const imports: ImportStatement[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const lineNumber = i + 1;

    // 匹配 import 语句
    // import ... from '...'
    // import('...')
    const importMatch = line.match(/import\s+.*?from\s+['"]([^'"]+)['"]/);
    const dynamicImportMatch = line.match(/import\(['"]([^'"]+)['"]\)/);

    const match = importMatch || dynamicImportMatch;

    if (match) {
      const importPath = match[1];

      // 只处理相对导入和 app/ 开头的导入
      if (importPath.startsWith('.') || importPath.startsWith('app/')) {
        const resolvedPath = resolveImportPath(file, importPath);

        imports.push({
          file,
          line: lineNumber,
          importPath,
          resolvedPath,
        });
      }
    }
  }

  return imports;
}

/**
 * 解析导入路径为绝对路径
 */
function resolveImportPath(fromFile: string, importPath: string): string {
  const fromDir = path.dirname(fromFile);

  // 处理相对路径
  if (importPath.startsWith('.')) {
    let resolved = path.resolve(fromDir, importPath);

    // 尝试添加 .ts, .tsx 扩展名
    if (!fs.existsSync(resolved)) {
      if (fs.existsSync(resolved + '.ts')) {
        resolved += '.ts';
      } else if (fs.existsSync(resolved + '.tsx')) {
        resolved += '.tsx';
      } else if (fs.existsSync(path.join(resolved, 'index.ts'))) {
        resolved = path.join(resolved, 'index.ts');
      } else if (fs.existsSync(path.join(resolved, 'index.tsx'))) {
        resolved = path.join(resolved, 'index.tsx');
      }
    }

    return resolved;
  }

  // 处理 app/ 开头的绝对导入
  if (importPath.startsWith('app/')) {
    const relativePath = importPath.replace(/^app\//, '');
    return path.resolve(config.sourceDir, relativePath);
  }

  return importPath;
}

/**
 * 获取文件所属的层级
 */
function getLayer(file: string): string | null {
  const relativePath = path.relative(config.sourceDir, file);

  if (relativePath.startsWith('kernel/')) return 'kernel';
  if (relativePath.startsWith('domains/')) return 'domains';
  if (relativePath.startsWith('modules/')) return 'modules';
  if (relativePath.startsWith('views/')) return 'views';

  return null;
}

/**
 * 规范化文件路径用于显示
 */
function normalizeFilePath(file: string): string {
  return path.relative(config.rootDir, file);
}

// ========================================
// Check 1: Circular Dependency Detection
// ========================================

/**
 * 使用 DFS 检测循环依赖
 */
function detectCircularDependencies(
  files: string[],
  allImports: ImportStatement[]
): Violation[] {
  const violations: Violation[] = [];

  // 构建依赖图 (file -> [dependencies])
  const graph = new Map<string, string[]>();

  for (const file of files) {
    graph.set(file, []);
  }

  for (const imp of allImports) {
    const deps = graph.get(imp.file);
    if (deps && fs.existsSync(imp.resolvedPath)) {
      deps.push(imp.resolvedPath);
    }
  }

  // DFS 检测环
  const visited = new Set<string>();
  const recStack = new Set<string>();
  const pathStack: string[] = [];

  function dfs(file: string): boolean {
    visited.add(file);
    recStack.add(file);
    pathStack.push(file);

    const neighbors = graph.get(file) || [];

    for (const neighbor of neighbors) {
      if (!visited.has(neighbor)) {
        if (dfs(neighbor)) {
          return true;
        }
      } else if (recStack.has(neighbor)) {
        // 发现环
        const cycleStartIndex = pathStack.indexOf(neighbor);
        const cycle = pathStack.slice(cycleStartIndex);

        violations.push({
          type: 'circular',
          file: neighbor,
          message: `Circular dependency detected: ${cycle.map(normalizeFilePath).join(' → ')} → ${normalizeFilePath(neighbor)}`,
          details: { cycle },
        });

        return true;
      }
    }

    pathStack.pop();
    recStack.delete(file);
    return false;
  }

  for (const file of files) {
    if (!visited.has(file)) {
      dfs(file);
    }
  }

  return violations;
}

// ========================================
// Check 2: Layer Boundary Violation Detection
// ========================================

/**
 * 检测层级边界违规
 *
 * 规则：
 * - kernel → 不应导入任何层
 * - domains → 只能导入 kernel
 * - modules → 只能导入 kernel, domains
 * - views → 可以导入 kernel, domains, modules
 */
function detectLayerBoundaryViolations(allImports: ImportStatement[]): Violation[] {
  const violations: Violation[] = [];

  // 定义允许的导入关系
  const allowedImports: Record<string, string[]> = {
    kernel: [], // kernel 不应导入任何层
    domains: ['kernel'],
    modules: ['kernel', 'domains'],
    views: ['kernel', 'domains', 'modules'],
  };

  for (const imp of allImports) {
    const fromLayer = getLayer(imp.file);
    const toLayer = getLayer(imp.resolvedPath);

    // 如果任一文件不在已知层级中，跳过
    if (!fromLayer || !toLayer) continue;

    // 同层导入总是允许的
    if (fromLayer === toLayer) continue;

    // 检查是否允许导入
    const allowed = allowedImports[fromLayer] || [];

    if (!allowed.includes(toLayer)) {
      violations.push({
        type: 'layer-boundary',
        file: imp.file,
        line: imp.line,
        message: `Layer boundary violation: ${fromLayer} → ${toLayer} (${fromLayer} can only import from: ${allowed.length > 0 ? allowed.join(', ') : 'nothing'})`,
        details: {
          from: normalizeFilePath(imp.file),
          to: normalizeFilePath(imp.resolvedPath),
          importPath: imp.importPath,
        },
      });
    }
  }

  return violations;
}

// ========================================
// Check 3: Deep Import Detection
// ========================================

/**
 * 检测深度导入（绕过 index.ts 的导入）
 *
 * 示例：
 * ❌ import { X } from '../module/internal/deep'
 * ✅ import { X } from '../module'
 */
function detectDeepImports(allImports: ImportStatement[]): Violation[] {
  const violations: Violation[] = [];

  for (const imp of allImports) {
    // 只检查相对导入
    if (!imp.importPath.startsWith('.')) continue;

    const fromDir = path.dirname(imp.file);
    const importPath = imp.importPath;

    // 分析导入路径的深度
    // 如果导入路径超过一级目录且不是 index，则可能是深度导入
    const parts = importPath.split('/');

    // 跳过 ./ 或 ../ 开头
    const pathParts = parts.filter((p) => p !== '.' && p !== '..');

    // 如果路径深度 > 1，并且不是直接导入 index，可能是深度导入
    if (pathParts.length > 1) {
      // 检查是否有对应的 index.ts 可以使用
      const potentialBarrelPath = path.resolve(fromDir, parts.slice(0, -1).join('/'));

      // 检查该目录是否有 index.ts 或 index.tsx
      const hasIndexTs = fs.existsSync(path.join(potentialBarrelPath, 'index.ts'));
      const hasIndexTsx = fs.existsSync(path.join(potentialBarrelPath, 'index.tsx'));

      if (hasIndexTs || hasIndexTsx) {
        const suggestedPath = parts.slice(0, -1).join('/');

        violations.push({
          type: 'deep-import',
          file: imp.file,
          line: imp.line,
          message: `Deep import detected: bypassing barrel export. Use '${suggestedPath}' instead of '${importPath}'`,
          details: {
            current: imp.importPath,
            suggested: suggestedPath,
          },
        });
      }
    }
  }

  return violations;
}

// ========================================
// Main Entry Point
// ========================================

function main() {
  console.log('🔍 Architecture Check Script');
  console.log('========================================\n');

  const violations: Violation[] = [];

  console.log('📂 Scanning TypeScript files...');
  const files = getAllTypeScriptFiles(config.sourceDir);
  console.log(`   Found ${files.length} files\n`);

  // Parse all imports
  console.log('📋 Parsing imports...');
  const allImports: ImportStatement[] = [];

  for (const file of files) {
    const imports = parseImports(file);
    allImports.push(...imports);
  }

  console.log(`   Found ${allImports.length} imports\n`);

  // Run checks
  console.log('🔍 Running checks...');

  // Check 1: Circular dependencies
  console.log('   [1/3] Checking circular dependencies...');
  const circularViolations = detectCircularDependencies(files, allImports);
  violations.push(...circularViolations);
  console.log(`         ${circularViolations.length === 0 ? '✅' : '❌'} Found ${circularViolations.length} circular dependencies`);

  // Check 2: Layer boundaries
  console.log('   [2/3] Checking layer boundaries...');
  const layerViolations = detectLayerBoundaryViolations(allImports);
  violations.push(...layerViolations);
  console.log(`         ${layerViolations.length === 0 ? '✅' : '❌'} Found ${layerViolations.length} layer boundary violations`);

  // Check 3: Deep imports
  console.log('   [3/3] Checking deep imports...');
  const deepImportViolations = detectDeepImports(allImports);
  violations.push(...deepImportViolations);
  console.log(`         ${deepImportViolations.length === 0 ? '✅' : '❌'} Found ${deepImportViolations.length} deep import violations\n`);

  // Report results
  console.log('========================================');

  if (violations.length === 0) {
    console.log('✅ No violations found!');
    process.exit(0);
  } else {
    console.log(`❌ Found ${violations.length} violation(s):\n`);

    for (const violation of violations) {
      console.log(`❌ ${violation.type.toUpperCase()}`);
      console.log(`   File: ${normalizeFilePath(violation.file)}${violation.line ? `:${violation.line}` : ''}`);
      console.log(`   ${violation.message}\n`);
    }

    process.exit(1);
  }
}

// Run
main();
