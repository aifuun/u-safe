/**
 * 改动分析算法模块
 *
 * 功能：
 * 1. 统计文件数量和改动行数
 * 2. 检测关键路径（auth/api/cache等）
 * 3. 计算改动复杂度
 * 4. 返回ChangeAnalysis对象供决策引擎使用
 *
 * @version 1.0.0
 * @lastUpdated 2026-03-19
 */

// ==================== 类型定义 ====================

/** 文件改动信息 */
interface FileChange {
  path: string;              // 文件路径
  additions: number;         // 新增行数
  deletions: number;         // 删除行数
  changes: number;           // 总改动行数（additions + deletions）
  is_new: boolean;           // 是否新文件
  is_deleted: boolean;       // 是否删除的文件
  file_type: string;         // 文件类型（.ts/.test.ts/.md等）
}

/** 改动分析结果 */
interface ChangeAnalysis {
  // 基本统计
  files_changed: number;
  total_additions: number;
  total_deletions: number;
  total_changes: number;

  // 文件类型分布
  file_types: {
    code: number;            // 代码文件数量（.ts/.js/.py等）
    test: number;            // 测试文件数量（.test.ts/.spec.ts等）
    config: number;          // 配置文件数量（.json/.yaml等）
    docs: number;            // 文档文件数量（.md等）
    other: number;           // 其他文件数量
  };

  // 关键路径检测
  critical_paths: CriticalPath[];

  // 复杂度评估
  complexity: {
    score: number;           // 复杂度得分（0-100）
    level: 'simple' | 'moderate' | 'complex' | 'very_complex';
    factors: string[];       // 复杂度因素列表
  };

  // 改动规模
  scale: 'tiny' | 'small' | 'medium' | 'large' | 'very_large';

  // 改动特征
  characteristics: string[]; // 改动特征列表（如"新功能"、"重构"、"bug修复"）
}

/** 关键路径信息 */
interface CriticalPath {
  pattern: string;           // 路径模式（如"auth/"）
  name: string;              // 路径名称（如"认证系统"）
  risk_level: 'critical' | 'high' | 'medium' | 'low';
  files_affected: number;    // 受影响的文件数
  description: string;       // 路径描述
}

// ==================== 配置常量 ====================

/** 关键路径模式配置 */
const CRITICAL_PATHS_CONFIG: Array<{
  pattern: RegExp;
  name: string;
  risk_level: 'critical' | 'high' | 'medium' | 'low';
  description: string;
}> = [
  {
    pattern: /\/auth\//i,
    name: '认证系统',
    risk_level: 'critical',
    description: '用户认证和授权相关代码，影响安全性'
  },
  {
    pattern: /\/api\//i,
    name: 'API接口',
    risk_level: 'high',
    description: 'API端点定义，影响前后端集成'
  },
  {
    pattern: /\/database\//i,
    name: '数据库层',
    risk_level: 'critical',
    description: '数据库操作和迁移，影响数据完整性'
  },
  {
    pattern: /\/cache\//i,
    name: '缓存系统',
    risk_level: 'high',
    description: '缓存逻辑，影响性能和一致性'
  },
  {
    pattern: /\/payment\//i,
    name: '支付系统',
    risk_level: 'critical',
    description: '支付处理，影响财务安全'
  },
  {
    pattern: /\/security\//i,
    name: '安全模块',
    risk_level: 'critical',
    description: '安全相关代码，影响系统安全性'
  },
  {
    pattern: /\/core\//i,
    name: '核心模块',
    risk_level: 'high',
    description: '核心业务逻辑，影响多个功能'
  },
  {
    pattern: /\/infrastructure\//i,
    name: '基础设施',
    risk_level: 'high',
    description: '基础设施代码（日志、监控等）'
  },
  {
    pattern: /migration|schema/i,
    name: '数据库迁移',
    risk_level: 'critical',
    description: '数据库结构变更，需要仔细审查'
  },
  {
    pattern: /package\.json|requirements\.txt|Cargo\.toml/i,
    name: '依赖管理',
    risk_level: 'medium',
    description: '依赖变更，可能引入安全漏洞'
  }
];

/** 复杂度因素配置 */
const COMPLEXITY_FACTORS = {
  large_file_changes: {
    threshold: 300,          // 单文件改动超过300行
    score: 20,
    description: '大量代码改动'
  },
  many_files: {
    threshold: 15,           // 改动超过15个文件
    score: 15,
    description: '涉及多个文件'
  },
  critical_path: {
    score: 25,
    description: '触及关键路径'
  },
  new_files: {
    threshold: 5,            // 新增超过5个文件
    score: 10,
    description: '大量新增文件'
  },
  low_test_ratio: {
    threshold: 0.3,          // 测试文件比例低于30%
    score: 15,
    description: '测试覆盖不足'
  },
  config_changes: {
    score: 10,
    description: '配置文件变更'
  }
};

// ==================== 核心函数 ====================

/**
 * 解析git diff统计输出
 *
 * @param diffStat - git diff --stat输出
 * @returns 文件改动列表
 *
 * @example
 * Input:
 * ```
 * src/auth/login.ts           | 45 +++++++++++++++++++++++--
 * src/auth/types.ts           | 12 +++++++
 * tests/auth.test.ts          | 89 +++++++++++++++++++++++++++++++++++++++++++++
 * 3 files changed, 143 insertions(+), 2 deletions(-)
 * ```
 *
 * Output:
 * ```typescript
 * [
 *   { path: 'src/auth/login.ts', additions: 43, deletions: 2, ... },
 *   { path: 'src/auth/types.ts', additions: 12, deletions: 0, ... },
 *   { path: 'tests/auth.test.ts', additions: 89, deletions: 0, ... }
 * ]
 * ```
 */
function parseGitDiffStat(diffStat: string): FileChange[] {
  const changes: FileChange[] = [];
  const lines = diffStat.split('\n');

  lines.forEach(line => {
    // 匹配格式：path | changes ++++----
    const match = line.match(/^\s*(.+?)\s+\|\s+(\d+)\s+([\+\-]+)$/);
    if (!match) return;

    const path = match[1].trim();
    const totalChanges = parseInt(match[2]);
    const markers = match[3];

    const additions = (markers.match(/\+/g) || []).length;
    const deletions = (markers.match(/\-/g) || []).length;

    // 检测文件类型
    const fileType = detectFileType(path);

    changes.push({
      path,
      additions,
      deletions,
      changes: additions + deletions,
      is_new: additions > 0 && deletions === 0,
      is_deleted: deletions > 0 && additions === 0,
      file_type: fileType
    });
  });

  return changes;
}

/**
 * 检测文件类型
 *
 * @param filePath - 文件路径
 * @returns 文件类型
 */
function detectFileType(filePath: string): string {
  if (/\.test\.(ts|js|tsx|jsx)$/.test(filePath) || /\.spec\.(ts|js|tsx|jsx)$/.test(filePath)) {
    return 'test';
  } else if (/\.(ts|js|tsx|jsx|py|go|rs|java|cpp|c|h)$/.test(filePath)) {
    return 'code';
  } else if (/\.(json|yaml|yml|toml|ini|conf)$/.test(filePath)) {
    return 'config';
  } else if (/\.(md|txt|rst)$/.test(filePath)) {
    return 'docs';
  } else {
    return 'other';
  }
}

/**
 * 统计文件类型分布
 *
 * @param changes - 文件改动列表
 * @returns 文件类型分布
 */
function analyzeFileTypes(changes: FileChange[]): {
  code: number;
  test: number;
  config: number;
  docs: number;
  other: number;
} {
  const counts = { code: 0, test: 0, config: 0, docs: 0, other: 0 };

  changes.forEach(change => {
    const type = change.file_type;
    if (type in counts) {
      counts[type as keyof typeof counts]++;
    }
  });

  return counts;
}

/**
 * 检测关键路径
 *
 * @param changes - 文件改动列表
 * @returns 触及的关键路径列表
 */
function detectCriticalPaths(changes: FileChange[]): CriticalPath[] {
  const detectedPaths: Map<string, CriticalPath> = new Map();

  changes.forEach(change => {
    CRITICAL_PATHS_CONFIG.forEach(config => {
      if (config.pattern.test(change.path)) {
        const key = config.name;
        if (!detectedPaths.has(key)) {
          detectedPaths.set(key, {
            pattern: config.pattern.source,
            name: config.name,
            risk_level: config.risk_level,
            files_affected: 0,
            description: config.description
          });
        }
        detectedPaths.get(key)!.files_affected++;
      }
    });
  });

  return Array.from(detectedPaths.values()).sort((a, b) => {
    // 按风险等级和受影响文件数排序
    const riskOrder = { critical: 4, high: 3, medium: 2, low: 1 };
    const riskDiff = riskOrder[b.risk_level] - riskOrder[a.risk_level];
    if (riskDiff !== 0) return riskDiff;
    return b.files_affected - a.files_affected;
  });
}

/**
 * 计算改动复杂度
 *
 * @param changes - 文件改动列表
 * @param fileTypes - 文件类型分布
 * @param criticalPaths - 关键路径列表
 * @returns 复杂度评估结果
 */
function calculateComplexity(
  changes: FileChange[],
  fileTypes: ReturnType<typeof analyzeFileTypes>,
  criticalPaths: CriticalPath[]
): {
  score: number;
  level: 'simple' | 'moderate' | 'complex' | 'very_complex';
  factors: string[];
} {
  let score = 0;
  const factors: string[] = [];

  // 因素1：大文件改动
  const largeFiles = changes.filter(c => c.changes > COMPLEXITY_FACTORS.large_file_changes.threshold);
  if (largeFiles.length > 0) {
    score += COMPLEXITY_FACTORS.large_file_changes.score;
    factors.push(`${largeFiles.length}个大文件改动（>${COMPLEXITY_FACTORS.large_file_changes.threshold}行）`);
  }

  // 因素2：文件数量多
  if (changes.length > COMPLEXITY_FACTORS.many_files.threshold) {
    score += COMPLEXITY_FACTORS.many_files.score;
    factors.push(`涉及${changes.length}个文件`);
  }

  // 因素3：关键路径
  if (criticalPaths.length > 0) {
    score += COMPLEXITY_FACTORS.critical_path.score;
    factors.push(`触及${criticalPaths.length}个关键路径：${criticalPaths.map(p => p.name).join(', ')}`);
  }

  // 因素4：新增文件多
  const newFiles = changes.filter(c => c.is_new);
  if (newFiles.length > COMPLEXITY_FACTORS.new_files.threshold) {
    score += COMPLEXITY_FACTORS.new_files.score;
    factors.push(`新增${newFiles.length}个文件`);
  }

  // 因素5：测试覆盖不足
  const totalCode = fileTypes.code;
  const testRatio = totalCode > 0 ? fileTypes.test / totalCode : 0;
  if (testRatio < COMPLEXITY_FACTORS.low_test_ratio.threshold) {
    score += COMPLEXITY_FACTORS.low_test_ratio.score;
    factors.push(`测试文件比例低（${Math.round(testRatio * 100)}%）`);
  }

  // 因素6：配置变更
  if (fileTypes.config > 0) {
    score += COMPLEXITY_FACTORS.config_changes.score;
    factors.push(`${fileTypes.config}个配置文件变更`);
  }

  // 确定复杂度等级
  let level: 'simple' | 'moderate' | 'complex' | 'very_complex';
  if (score < 20) {
    level = 'simple';
  } else if (score < 40) {
    level = 'moderate';
  } else if (score < 60) {
    level = 'complex';
  } else {
    level = 'very_complex';
  }

  return { score, level, factors };
}

/**
 * 确定改动规模
 *
 * @param totalChanges - 总改动行数
 * @returns 改动规模
 */
function determineScale(totalChanges: number): 'tiny' | 'small' | 'medium' | 'large' | 'very_large' {
  if (totalChanges < 50) return 'tiny';
  if (totalChanges < 200) return 'small';
  if (totalChanges < 500) return 'medium';
  if (totalChanges < 1000) return 'large';
  return 'very_large';
}

/**
 * 推断改动特征
 *
 * @param changes - 文件改动列表
 * @param fileTypes - 文件类型分布
 * @returns 改动特征列表
 */
function inferCharacteristics(
  changes: FileChange[],
  fileTypes: ReturnType<typeof analyzeFileTypes>
): string[] {
  const characteristics: string[] = [];

  // 新功能：大量新增文件
  const newFiles = changes.filter(c => c.is_new);
  if (newFiles.length >= 3) {
    characteristics.push('新功能开发');
  }

  // 重构：改动/新增比例高
  const totalAdditions = changes.reduce((sum, c) => sum + c.additions, 0);
  const totalDeletions = changes.reduce((sum, c) => sum + c.deletions, 0);
  if (totalDeletions > totalAdditions * 0.5) {
    characteristics.push('代码重构');
  }

  // Bug修复：改动少但测试多
  if (changes.length <= 5 && fileTypes.test >= fileTypes.code) {
    characteristics.push('Bug修复');
  }

  // 文档更新
  if (fileTypes.docs > 0 && fileTypes.code === 0) {
    characteristics.push('文档更新');
  }

  // 配置变更
  if (fileTypes.config > 0) {
    characteristics.push('配置调整');
  }

  // 测试补充
  if (fileTypes.test > fileTypes.code) {
    characteristics.push('测试补充');
  }

  return characteristics;
}

/**
 * 主函数：分析代码改动
 *
 * @param diffStat - git diff --stat输出
 * @returns 完整的改动分析结果
 */
export function analyzeChanges(diffStat: string): ChangeAnalysis {
  // 1. 解析改动
  const changes = parseGitDiffStat(diffStat);

  // 2. 基本统计
  const filesChanged = changes.length;
  const totalAdditions = changes.reduce((sum, c) => sum + c.additions, 0);
  const totalDeletions = changes.reduce((sum, c) => sum + c.deletions, 0);
  const totalChanges = totalAdditions + totalDeletions;

  // 3. 文件类型分布
  const fileTypes = analyzeFileTypes(changes);

  // 4. 关键路径检测
  const criticalPaths = detectCriticalPaths(changes);

  // 5. 复杂度评估
  const complexity = calculateComplexity(changes, fileTypes, criticalPaths);

  // 6. 改动规模
  const scale = determineScale(totalChanges);

  // 7. 改动特征
  const characteristics = inferCharacteristics(changes, fileTypes);

  return {
    files_changed: filesChanged,
    total_additions: totalAdditions,
    total_deletions: totalDeletions,
    total_changes: totalChanges,
    file_types: fileTypes,
    critical_paths: criticalPaths,
    complexity,
    scale,
    characteristics
  };
}

// ==================== 导出 ====================

export {
  parseGitDiffStat,
  detectFileType,
  analyzeFileTypes,
  detectCriticalPaths,
  calculateComplexity,
  determineScale,
  inferCharacteristics,
  type FileChange,
  type ChangeAnalysis,
  type CriticalPath
};
