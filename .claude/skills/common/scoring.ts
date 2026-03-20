/**
 * 统一评分体系模块
 *
 * 功能：
 * 1. 计算4视角综合得分
 * 2. 定义通过标准（APPROVED/APPROVED_WITH_CONCERNS/NEEDS_IMPROVEMENT/REJECTED）
 * 3. 生成评分报告
 * 4. 确保eval-plan和review使用相同评分逻辑
 *
 * @version 1.0.0
 * @lastUpdated 2026-03-19
 */

// ==================== 类型定义 ====================

/** 单个视角的评分 */
interface PerspectiveScore {
  name: string;                  // 视角名称（如"目标达成"）
  weight: number;                // 权重（0-1）
  checks: CheckResult[];         // 检查项结果
  score: number;                 // 视角得分（0-1）
  status: 'PASS' | 'PARTIAL' | 'FAIL';
}

/** 单个检查项的结果 */
interface CheckResult {
  id: string;                    // 检查项ID（如"ga1"）
  name: string;                  // 检查项名称
  importance: 'critical' | 'high' | 'medium' | 'low';
  result: 'pass' | 'partial' | 'fail';
  message?: string;              // 说明信息
  recommendation?: string;       // 改进建议
}

/** 综合评分结果 */
interface EvaluationResult {
  // 基本信息
  timestamp: string;
  issue_number?: number;

  // 视角得分
  perspectives: {
    goal_achievement: PerspectiveScore;
    architecture_design: PerspectiveScore;
    quality_assurance: PerspectiveScore;
    risk_control: PerspectiveScore;
  };

  // 综合得分
  overall_score: number;         // 0-100
  weighted_score: number;        // 加权得分（0-1）

  // 通过状态
  status: 'APPROVED' | 'APPROVED_WITH_CONCERNS' | 'NEEDS_IMPROVEMENT' | 'REJECTED';

  // 关键发现
  critical_issues: string[];     // 关键问题列表
  recommendations: string[];     // 改进建议列表

  // 后续行动
  next_actions: string[];        // 建议的后续步骤
}

// ==================== 配置常量 ====================

/** 4视角权重配置 */
const PERSPECTIVE_WEIGHTS = {
  goal_achievement: 0.30,      // 目标达成：30%
  architecture_design: 0.30,   // 架构设计：30%
  quality_assurance: 0.25,     // 质量保障：25%
  risk_control: 0.15           // 风险控制：15%
} as const;

/** 通过标准阈值 */
const APPROVAL_THRESHOLDS = {
  APPROVED: 0.90,                      // ≥90分：批准
  APPROVED_WITH_CONCERNS: 0.80,        // 80-89分：有保留地批准
  NEEDS_IMPROVEMENT: 0.60,             // 60-79分：需要改进
  REJECTED: 0.0                        // <60分：拒绝
} as const;

/** 单项评分值 */
const CHECK_SCORES = {
  pass: 1.0,
  partial: 0.5,
  fail: 0.0
} as const;

// ==================== 核心函数 ====================

/**
 * 计算单个视角的得分
 *
 * 公式：perspective_score = (passed_checks + 0.5*partial_checks) / total_checks
 *
 * @param checks - 检查项结果数组
 * @returns 视角得分（0-1）
 */
function calculatePerspectiveScore(checks: CheckResult[]): number {
  if (checks.length === 0) {
    return 1.0;  // 如果没有检查项，默认满分
  }

  let totalScore = 0;

  checks.forEach(check => {
    totalScore += CHECK_SCORES[check.result];
  });

  return totalScore / checks.length;
}

/**
 * 计算综合得分
 *
 * 公式：final_score = sum(perspective_weight * perspective_score)
 *
 * @param perspectives - 4个视角的评分
 * @returns 加权综合得分（0-1）
 */
function calculateOverallScore(perspectives: {
  goal_achievement: PerspectiveScore;
  architecture_design: PerspectiveScore;
  quality_assurance: PerspectiveScore;
  risk_control: PerspectiveScore;
}): number {
  let weightedSum = 0;

  weightedSum += perspectives.goal_achievement.score * PERSPECTIVE_WEIGHTS.goal_achievement;
  weightedSum += perspectives.architecture_design.score * PERSPECTIVE_WEIGHTS.architecture_design;
  weightedSum += perspectives.quality_assurance.score * PERSPECTIVE_WEIGHTS.quality_assurance;
  weightedSum += perspectives.risk_control.score * PERSPECTIVE_WEIGHTS.risk_control;

  return weightedSum;
}

/**
 * 确定通过状态
 *
 * 根据综合得分和关键项检查结果，确定最终状态
 *
 * @param overallScore - 综合得分（0-1）
 * @param hasCriticalFailure - 是否有关键项失败
 * @returns 通过状态
 */
function determineStatus(
  overallScore: number,
  hasCriticalFailure: boolean
): 'APPROVED' | 'APPROVED_WITH_CONCERNS' | 'NEEDS_IMPROVEMENT' | 'REJECTED' {
  // 规则1：如果有关键项失败，最高只能APPROVED_WITH_CONCERNS
  if (hasCriticalFailure && overallScore >= APPROVAL_THRESHOLDS.APPROVED_WITH_CONCERNS) {
    return 'APPROVED_WITH_CONCERNS';
  }

  // 规则2：根据得分确定状态
  if (overallScore >= APPROVAL_THRESHOLDS.APPROVED) {
    return 'APPROVED';
  } else if (overallScore >= APPROVAL_THRESHOLDS.APPROVED_WITH_CONCERNS) {
    return 'APPROVED_WITH_CONCERNS';
  } else if (overallScore >= APPROVAL_THRESHOLDS.NEEDS_IMPROVEMENT) {
    return 'NEEDS_IMPROVEMENT';
  } else {
    return 'REJECTED';
  }
}

/**
 * 检查是否有关键项失败
 *
 * @param perspectives - 4个视角的评分
 * @returns 是否有关键项失败
 */
function hasCriticalFailure(perspectives: {
  goal_achievement: PerspectiveScore;
  architecture_design: PerspectiveScore;
  quality_assurance: PerspectiveScore;
  risk_control: PerspectiveScore;
}): boolean {
  const allChecks = [
    ...perspectives.goal_achievement.checks,
    ...perspectives.architecture_design.checks,
    ...perspectives.quality_assurance.checks,
    ...perspectives.risk_control.checks
  ];

  return allChecks.some(
    check => check.importance === 'critical' && check.result === 'fail'
  );
}

/**
 * 收集关键问题
 *
 * @param perspectives - 4个视角的评分
 * @returns 关键问题列表
 */
function collectCriticalIssues(perspectives: {
  goal_achievement: PerspectiveScore;
  architecture_design: PerspectiveScore;
  quality_assurance: PerspectiveScore;
  risk_control: PerspectiveScore;
}): string[] {
  const issues: string[] = [];

  Object.values(perspectives).forEach(perspective => {
    perspective.checks.forEach(check => {
      if (check.importance === 'critical' && check.result === 'fail') {
        issues.push(`[${perspective.name}] ${check.name}: ${check.message || '未通过'}`);
      }
    });
  });

  return issues;
}

/**
 * 收集改进建议
 *
 * @param perspectives - 4个视角的评分
 * @returns 改进建议列表
 */
function collectRecommendations(perspectives: {
  goal_achievement: PerspectiveScore;
  architecture_design: PerspectiveScore;
  quality_assurance: PerspectiveScore;
  risk_control: PerspectiveScore;
}): string[] {
  const recommendations: string[] = [];

  Object.values(perspectives).forEach(perspective => {
    perspective.checks.forEach(check => {
      // 收集失败或部分通过的非关键项的建议
      if (
        (check.result === 'fail' || check.result === 'partial') &&
        check.importance !== 'critical' &&
        check.recommendation
      ) {
        recommendations.push(`[${perspective.name}] ${check.recommendation}`);
      }
    });
  });

  return recommendations;
}

/**
 * 生成后续行动建议
 *
 * 根据状态和问题，建议下一步该做什么
 *
 * @param status - 通过状态
 * @param criticalIssues - 关键问题列表
 * @returns 后续行动建议
 */
function generateNextActions(
  status: 'APPROVED' | 'APPROVED_WITH_CONCERNS' | 'NEEDS_IMPROVEMENT' | 'REJECTED',
  criticalIssues: string[]
): string[] {
  const actions: string[] = [];

  switch (status) {
    case 'APPROVED':
      actions.push('✅ 可以合并到主分支');
      actions.push('运行 /finish-issue 完成工作流');
      break;

    case 'APPROVED_WITH_CONCERNS':
      actions.push('⚠️ 可以合并，但建议后续改进');
      actions.push('记录改进项到技术债清单');
      actions.push('运行 /finish-issue 或先修复建议项');
      break;

    case 'NEEDS_IMPROVEMENT':
      actions.push('❌ 需要修复以下问题后再合并：');
      criticalIssues.forEach(issue => {
        actions.push(`   - ${issue}`);
      });
      actions.push('修复后重新运行 /review');
      break;

    case 'REJECTED':
      actions.push('🚫 代码存在严重问题，不建议继续：');
      criticalIssues.forEach(issue => {
        actions.push(`   - ${issue}`);
      });
      actions.push('重新评估方案或从头开始');
      break;
  }

  return actions;
}

/**
 * 主函数：计算完整的评估结果
 *
 * @param perspectives - 4个视角的评分
 * @param issueNumber - Issue编号（可选）
 * @returns 完整的评估结果
 */
export function evaluateCode(
  perspectives: {
    goal_achievement: PerspectiveScore;
    architecture_design: PerspectiveScore;
    quality_assurance: PerspectiveScore;
    risk_control: PerspectiveScore;
  },
  issueNumber?: number
): EvaluationResult {
  // 1. 计算综合得分
  const weightedScore = calculateOverallScore(perspectives);
  const overallScore = Math.round(weightedScore * 100);  // 转换为0-100分

  // 2. 检查关键项
  const hasCritical = hasCriticalFailure(perspectives);

  // 3. 确定状态
  const status = determineStatus(weightedScore, hasCritical);

  // 4. 收集问题和建议
  const criticalIssues = collectCriticalIssues(perspectives);
  const recommendations = collectRecommendations(perspectives);

  // 5. 生成后续行动
  const nextActions = generateNextActions(status, criticalIssues);

  return {
    timestamp: new Date().toISOString(),
    issue_number: issueNumber,
    perspectives,
    overall_score: overallScore,
    weighted_score: weightedScore,
    status,
    critical_issues: criticalIssues,
    recommendations,
    next_actions: nextActions
  };
}

/**
 * 辅助函数：创建视角评分对象
 *
 * @param name - 视角名称
 * @param weight - 权重
 * @param checks - 检查项结果
 * @returns 视角评分对象
 */
export function createPerspectiveScore(
  name: string,
  weight: number,
  checks: CheckResult[]
): PerspectiveScore {
  const score = calculatePerspectiveScore(checks);

  // 确定视角状态
  let status: 'PASS' | 'PARTIAL' | 'FAIL';
  if (score >= 0.9) {
    status = 'PASS';
  } else if (score >= 0.6) {
    status = 'PARTIAL';
  } else {
    status = 'FAIL';
  }

  return {
    name,
    weight,
    checks,
    score,
    status
  };
}

/**
 * 辅助函数：创建检查项结果
 *
 * @param params - 检查项参数
 * @returns 检查项结果对象
 */
export function createCheckResult(params: {
  id: string;
  name: string;
  importance: 'critical' | 'high' | 'medium' | 'low';
  result: 'pass' | 'partial' | 'fail';
  message?: string;
  recommendation?: string;
}): CheckResult {
  return { ...params };
}

// ==================== 导出 ====================

export {
  PERSPECTIVE_WEIGHTS,
  APPROVAL_THRESHOLDS,
  CHECK_SCORES,
  calculatePerspectiveScore,
  calculateOverallScore,
  determineStatus,
  hasCriticalFailure,
  collectCriticalIssues,
  collectRecommendations,
  generateNextActions,
  type PerspectiveScore,
  type CheckResult,
  type EvaluationResult
};
