/**
 * 决策引擎模块
 *
 * 功能：
 * 1. 定义4个检查策略（quick/targeted/standard/deep）
 * 2. 实现决策规则（基于改动特征）
 * 3. 实现路径→视角映射逻辑
 * 4. 输出决策理由（transparency）
 *
 * @version 1.0.0
 * @lastUpdated 2026-03-19
 */

import { ChangeAnalysis, CriticalPath } from './change-analyzer';

// ==================== 类型定义 ====================

/** 检查策略 */
type CheckStrategy = 'quick' | 'targeted' | 'standard' | 'deep';

/** 视角启用配置 */
interface PerspectiveConfig {
  goal_achievement: boolean;     // 是否检查目标达成
  architecture_design: boolean;  // 是否检查架构设计
  quality_assurance: boolean;    // 是否检查质量保障
  risk_control: boolean;         // 是否检查风险控制
}

/** 决策结果 */
interface DecisionResult {
  strategy: CheckStrategy;
  perspectives: PerspectiveConfig;
  depth: {
    goal_achievement: 'skip' | 'light' | 'full';
    architecture_design: 'skip' | 'light' | 'full';
    quality_assurance: 'skip' | 'light' | 'full';
    risk_control: 'skip' | 'light' | 'full';
  };
  reasoning: string[];           // 决策理由列表
  estimated_tokens: number;      // 预估token消耗
}

// ==================== 配置常量 ====================

/** 策略定义 */
const STRATEGIES = {
  quick: {
    name: '快速检查',
    description: '仅检查关键问题，适用于小改动',
    perspectives: {
      goal_achievement: true,   // 总是检查目标
      architecture_design: false,
      quality_assurance: false,
      risk_control: true        // 总是检查风险
    },
    depth: {
      goal_achievement: 'light' as const,
      architecture_design: 'skip' as const,
      quality_assurance: 'skip' as const,
      risk_control: 'light' as const
    },
    estimated_tokens: 3000
  },
  targeted: {
    name: '定向检查',
    description: '根据改动路径选择性检查，适用于关键路径改动',
    perspectives: {
      goal_achievement: true,
      architecture_design: true, // 关键路径需要架构检查
      quality_assurance: false,
      risk_control: true
    },
    depth: {
      goal_achievement: 'full' as const,
      architecture_design: 'full' as const,
      quality_assurance: 'light' as const,
      risk_control: 'full' as const
    },
    estimated_tokens: 6000
  },
  standard: {
    name: '标准检查',
    description: '检查所有4个视角（轻量级），适用于中等改动',
    perspectives: {
      goal_achievement: true,
      architecture_design: true,
      quality_assurance: true,
      risk_control: true
    },
    depth: {
      goal_achievement: 'full' as const,
      architecture_design: 'light' as const,
      quality_assurance: 'light' as const,
      risk_control: 'full' as const
    },
    estimated_tokens: 8000
  },
  deep: {
    name: '深度检查',
    description: '全面深度检查，适用于大改动或高风险改动',
    perspectives: {
      goal_achievement: true,
      architecture_design: true,
      quality_assurance: true,
      risk_control: true
    },
    depth: {
      goal_achievement: 'full' as const,
      architecture_design: 'full' as const,
      quality_assurance: 'full' as const,
      risk_control: 'full' as const
    },
    estimated_tokens: 15000
  }
} as const;

/** 决策规则权重 */
const DECISION_WEIGHTS = {
  scale: 0.3,           // 改动规模权重
  complexity: 0.3,      // 复杂度权重
  critical_paths: 0.4   // 关键路径权重
};

// ==================== 核心函数 ====================

/**
 * 根据改动规模评分
 *
 * @param scale - 改动规模
 * @returns 规模得分（0-100）
 */
function scoreByScale(scale: ChangeAnalysis['scale']): number {
  const scaleScores = {
    tiny: 10,
    small: 30,
    medium: 50,
    large: 75,
    very_large: 100
  };
  return scaleScores[scale];
}

/**
 * 根据复杂度评分
 *
 * @param complexity - 复杂度信息
 * @returns 复杂度得分（0-100）
 */
function scoreByComplexity(complexity: ChangeAnalysis['complexity']): number {
  return complexity.score;
}

/**
 * 根据关键路径评分
 *
 * @param criticalPaths - 关键路径列表
 * @returns 关键路径得分（0-100）
 */
function scoreByCriticalPaths(criticalPaths: CriticalPath[]): number {
  if (criticalPaths.length === 0) return 0;

  // 按风险等级加权
  const riskWeights = { critical: 40, high: 25, medium: 15, low: 5 };
  let totalScore = 0;

  criticalPaths.forEach(path => {
    totalScore += riskWeights[path.risk_level];
  });

  return Math.min(totalScore, 100); // 最高100分
}

/**
 * 计算综合决策得分
 *
 * @param analysis - 改动分析结果
 * @returns 决策得分（0-100）
 */
function calculateDecisionScore(analysis: ChangeAnalysis): number {
  const scaleScore = scoreByScale(analysis.scale);
  const complexityScore = scoreByComplexity(analysis.complexity);
  const criticalPathScore = scoreByCriticalPaths(analysis.critical_paths);

  const weightedScore =
    scaleScore * DECISION_WEIGHTS.scale +
    complexityScore * DECISION_WEIGHTS.complexity +
    criticalPathScore * DECISION_WEIGHTS.critical_paths;

  return Math.round(weightedScore);
}

/**
 * 根据得分选择策略
 *
 * @param score - 决策得分（0-100）
 * @param hasCriticalPath - 是否有关键路径
 * @returns 选择的策略
 */
function selectStrategy(score: number, hasCriticalPath: boolean): CheckStrategy {
  // 规则1: 关键路径改动至少使用targeted策略
  if (hasCriticalPath && score < 40) {
    return 'targeted';
  }

  // 规则2: 根据得分选择策略
  if (score < 20) {
    return 'quick';       // 0-19分：快速检查
  } else if (score < 40) {
    return 'targeted';    // 20-39分：定向检查
  } else if (score < 70) {
    return 'standard';    // 40-69分：标准检查
  } else {
    return 'deep';        // 70-100分：深度检查
  }
}

/**
 * 生成决策理由
 *
 * @param analysis - 改动分析结果
 * @param score - 决策得分
 * @param strategy - 选择的策略
 * @returns 决策理由列表
 */
function generateReasoning(
  analysis: ChangeAnalysis,
  score: number,
  strategy: CheckStrategy
): string[] {
  const reasoning: string[] = [];

  // 1. 总体决策
  reasoning.push(`决策得分：${score}/100 → 策略：${STRATEGIES[strategy].name}`);

  // 2. 规模因素
  const scaleDescriptions = {
    tiny: '微小改动（<50行）',
    small: '小改动（50-200行）',
    medium: '中等改动（200-500行）',
    large: '大改动（500-1000行）',
    very_large: '超大改动（>1000行）'
  };
  reasoning.push(`改动规模：${scaleDescriptions[analysis.scale]}（${analysis.total_changes}行）`);

  // 3. 复杂度因素
  if (analysis.complexity.factors.length > 0) {
    reasoning.push(`复杂度因素：${analysis.complexity.factors.join('; ')}`);
  }

  // 4. 关键路径因素
  if (analysis.critical_paths.length > 0) {
    const criticalPathsStr = analysis.critical_paths
      .map(p => `${p.name}(${p.risk_level})`)
      .join(', ');
    reasoning.push(`关键路径：${criticalPathsStr}`);
  }

  // 5. 策略说明
  reasoning.push(`策略说明：${STRATEGIES[strategy].description}`);

  // 6. 预估token消耗
  reasoning.push(`预估token：${STRATEGIES[strategy].estimated_tokens}`);

  return reasoning;
}

/**
 * 根据关键路径调整检查深度
 *
 * @param criticalPaths - 关键路径列表
 * @param baseDepth - 基础深度配置
 * @returns 调整后的深度配置
 */
function adjustDepthByCriticalPaths(
  criticalPaths: CriticalPath[],
  baseDepth: DecisionResult['depth']
): DecisionResult['depth'] {
  const adjusted = { ...baseDepth };

  // 如果触及关键路径，加强相关视角的检查深度
  criticalPaths.forEach(path => {
    switch (path.risk_level) {
      case 'critical':
        // 关键路径：所有视角都用full
        adjusted.architecture_design = 'full';
        adjusted.quality_assurance = 'full';
        adjusted.risk_control = 'full';
        break;

      case 'high':
        // 高风险路径：架构和风险用full
        if (adjusted.architecture_design === 'skip') {
          adjusted.architecture_design = 'light';
        }
        adjusted.risk_control = 'full';
        break;

      case 'medium':
        // 中风险路径：至少用light
        if (adjusted.risk_control === 'skip') {
          adjusted.risk_control = 'light';
        }
        break;
    }
  });

  return adjusted;
}

/**
 * 主函数：执行智能决策
 *
 * @param analysis - 改动分析结果
 * @returns 决策结果
 */
export function makeDecision(analysis: ChangeAnalysis): DecisionResult {
  // 1. 计算决策得分
  const score = calculateDecisionScore(analysis);

  // 2. 选择基础策略
  const hasCriticalPath = analysis.critical_paths.length > 0;
  const strategy = selectStrategy(score, hasCriticalPath);

  // 3. 获取基础配置
  const baseConfig = STRATEGIES[strategy];

  // 4. 根据关键路径调整深度
  const adjustedDepth = adjustDepthByCriticalPaths(
    analysis.critical_paths,
    baseConfig.depth
  );

  // 5. 生成决策理由
  const reasoning = generateReasoning(analysis, score, strategy);

  return {
    strategy,
    perspectives: baseConfig.perspectives,
    depth: adjustedDepth,
    reasoning,
    estimated_tokens: baseConfig.estimated_tokens
  };
}

/**
 * 辅助函数：判断是否应该跳过某个视角
 *
 * @param perspective - 视角名称
 * @param decision - 决策结果
 * @returns 是否应该跳过
 */
export function shouldSkipPerspective(
  perspective: keyof PerspectiveConfig,
  decision: DecisionResult
): boolean {
  return !decision.perspectives[perspective] || decision.depth[perspective] === 'skip';
}

/**
 * 辅助函数：获取视角检查深度
 *
 * @param perspective - 视角名称
 * @param decision - 决策结果
 * @returns 检查深度
 */
export function getPerspectiveDepth(
  perspective: keyof PerspectiveConfig,
  decision: DecisionResult
): 'skip' | 'light' | 'full' {
  return decision.depth[perspective];
}

/**
 * 辅助函数：生成决策摘要（用于日志）
 *
 * @param decision - 决策结果
 * @returns 决策摘要字符串
 */
export function summarizeDecision(decision: DecisionResult): string {
  const enabledPerspectives = Object.entries(decision.perspectives)
    .filter(([_, enabled]) => enabled)
    .map(([name, _]) => name)
    .join(', ');

  return `策略: ${decision.strategy} | 视角: ${enabledPerspectives} | 预估token: ${decision.estimated_tokens}`;
}

// ==================== 导出 ====================

export {
  STRATEGIES,
  DECISION_WEIGHTS,
  scoreByScale,
  scoreByComplexity,
  scoreByCriticalPaths,
  calculateDecisionScore,
  selectStrategy,
  generateReasoning,
  adjustDepthByCriticalPaths,
  type CheckStrategy,
  type PerspectiveConfig,
  type DecisionResult
};
