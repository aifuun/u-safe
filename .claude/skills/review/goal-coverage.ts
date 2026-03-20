/**
 * 目标覆盖度检查模块
 *
 * 功能：
 * 1. 解析Issue验收标准
 * 2. 解析Plan任务清单
 * 3. 检查Issue需求覆盖度
 * 4. 检查计划任务完成度
 * 5. 识别额外功能
 *
 * @version 1.0.0
 * @lastUpdated 2026-03-19
 */

// ==================== 类型定义 ====================

/** Issue需求项 */
interface Requirement {
  id: string;           // 需求ID（从验收标准提取）
  description: string;  // 需求描述
  priority: 'must' | 'should' | 'could';  // 优先级
  source: string;       // 来源位置（如"Acceptance Criteria #1"）
}

/** Plan任务项 */
interface Task {
  id: string;           // 任务ID（如"Task 1"）
  title: string;        // 任务标题
  description: string;  // 任务描述
  completed: boolean;   // 是否完成
  phase?: string;       // 所属阶段
}

/** 覆盖度分析结果 */
interface CoverageAnalysis {
  // Issue需求覆盖
  requirements: {
    total: number;
    covered: number;
    uncovered: Requirement[];
    coverage_rate: number;  // 0-1
  };

  // Plan任务完成
  tasks: {
    total: number;
    completed: number;
    incomplete: Task[];
    completion_rate: number;  // 0-1
  };

  // 额外功能
  extras: {
    features: string[];      // 额外功能列表
    justified: boolean;      // 是否有合理理由
    justification?: string;  // 理由说明
  };

  // 综合评分
  overall_score: number;     // 0-1
  status: 'PASS' | 'PARTIAL' | 'FAIL';
}

// ==================== 核心函数 ====================

/**
 * 解析Issue验收标准
 *
 * 从Issue描述中提取验收标准，识别必须/应该/可以实现的需求
 *
 * @param issueBody - Issue的Markdown内容
 * @returns 需求列表
 *
 * @example
 * ```typescript
 * const requirements = parseRequirements(issueBody);
 * // [
 * //   { id: 'AC1', description: '实现登录功能', priority: 'must', ... },
 * //   { id: 'AC2', description: '支持记住密码', priority: 'should', ... }
 * // ]
 * ```
 */
function parseRequirements(issueBody: string): Requirement[] {
  const requirements: Requirement[] = [];

  // 1. 查找"Acceptance Criteria"或"验收标准"部分
  const acRegex = /##\s*(Acceptance Criteria|验收标准)([\s\S]*?)(?=##|$)/i;
  const match = issueBody.match(acRegex);

  if (!match) {
    // 如果没有明确的验收标准，尝试从Issue描述中提取关键需求
    const lines = issueBody.split('\n');
    lines.forEach((line, index) => {
      // 查找checkbox或numbered list
      const checkboxMatch = line.match(/^[-*]\s*\[[ x]\]\s*(.+)/);
      const numberedMatch = line.match(/^\d+\.\s*(.+)/);

      if (checkboxMatch || numberedMatch) {
        const description = (checkboxMatch?.[1] || numberedMatch?.[1] || '').trim();
        if (description.length > 10) {  // 过滤太短的项
          requirements.push({
            id: `REQ${requirements.length + 1}`,
            description,
            priority: 'must',  // 默认为必须
            source: `Line ${index + 1}`
          });
        }
      }
    });

    return requirements;
  }

  // 2. 解析验收标准列表
  const criteriaText = match[2];
  const lines = criteriaText.split('\n');

  lines.forEach((line, index) => {
    // 匹配checkbox或numbered list
    const checkboxMatch = line.match(/^[-*]\s*\[[ x]\]\s*(.+)/);
    const numberedMatch = line.match(/^\d+\.\s*(.+)/);

    if (checkboxMatch || numberedMatch) {
      const description = (checkboxMatch?.[1] || numberedMatch?.[1] || '').trim();

      // 从描述中推断优先级
      let priority: 'must' | 'should' | 'could' = 'must';
      if (description.toLowerCase().includes('should') || description.includes('应该')) {
        priority = 'should';
      } else if (description.toLowerCase().includes('could') || description.includes('可以')) {
        priority = 'could';
      }

      requirements.push({
        id: `AC${requirements.length + 1}`,
        description,
        priority,
        source: `Acceptance Criteria #${requirements.length + 1}`
      });
    }
  });

  return requirements;
}

/**
 * 解析Plan任务清单
 *
 * 从Plan Markdown文件中提取任务列表和完成状态
 *
 * @param planContent - Plan的Markdown内容
 * @returns 任务列表
 *
 * @example
 * ```typescript
 * const tasks = parseTasks(planContent);
 * // [
 * //   { id: 'Task 1', title: '创建数据模型', completed: true, ... },
 * //   { id: 'Task 2', title: '实现API', completed: false, ... }
 * // ]
 * ```
 */
function parseTasks(planContent: string): Task[] {
  const tasks: Task[] = [];

  // 查找"## Tasks"部分
  const tasksRegex = /##\s*Tasks([\s\S]*?)(?=##\s*Acceptance|##\s*Progress|$)/i;
  const match = planContent.match(tasksRegex);

  if (!match) {
    return tasks;
  }

  const tasksText = match[1];
  const lines = tasksText.split('\n');

  let currentPhase = '';
  let taskCounter = 0;

  lines.forEach((line) => {
    // 识别阶段标题（### Phase N: ...）
    const phaseMatch = line.match(/^###\s*(Phase\s*\d+[^#]*)/i);
    if (phaseMatch) {
      currentPhase = phaseMatch[1].trim();
      return;
    }

    // 识别任务标题（#### Task N: ...）
    const taskMatch = line.match(/^####\s*(Task\s*\d+)[:\s]+(.+)/i);
    if (taskMatch) {
      taskCounter++;
      const taskId = taskMatch[1];
      const title = taskMatch[2].trim();

      tasks.push({
        id: taskId,
        title,
        description: '',
        completed: false,  // 稍后通过checkbox更新
        phase: currentPhase
      });
      return;
    }

    // 识别checkbox（- [ ] 或 - [x]）
    const checkboxMatch = line.match(/^[-*]\s*\[([ x])\]\s*(.+)/);
    if (checkboxMatch && tasks.length > 0) {
      const isCompleted = checkboxMatch[1] === 'x';
      const description = checkboxMatch[2].trim();

      // 更新最后一个任务的完成状态
      const lastTask = tasks[tasks.length - 1];
      if (!lastTask.description) {
        lastTask.description = description;
      }

      // 如果所有checkbox都完成，则任务完成
      if (isCompleted) {
        lastTask.completed = true;
      }
    }
  });

  return tasks;
}

/**
 * 检查Issue需求覆盖度
 *
 * 对比Issue需求和Plan内容，识别未覆盖的需求
 *
 * @param requirements - Issue需求列表
 * @param planContent - Plan内容（用于关键词匹配）
 * @returns 覆盖度分析
 */
function checkIssueRequirements(
  requirements: Requirement[],
  planContent: string
): { covered: number; uncovered: Requirement[] } {
  const uncovered: Requirement[] = [];
  let covered = 0;

  requirements.forEach((req) => {
    // 提取需求中的关键词（去除停用词）
    const keywords = extractKeywords(req.description);

    // 检查Plan中是否包含这些关键词
    const isCovered = keywords.some(keyword => {
      const regex = new RegExp(keyword, 'i');
      return regex.test(planContent);
    });

    if (isCovered) {
      covered++;
    } else {
      uncovered.push(req);
    }
  });

  return { covered, uncovered };
}

/**
 * 检查计划任务完成度
 *
 * 统计已完成和未完成的任务
 *
 * @param tasks - 任务列表
 * @returns 完成度分析
 */
function checkTaskCompletion(tasks: Task[]): {
  completed: number;
  incomplete: Task[];
} {
  const completed = tasks.filter(t => t.completed).length;
  const incomplete = tasks.filter(t => !t.completed);

  return { completed, incomplete };
}

/**
 * 识别额外功能
 *
 * 检测Plan中未在Issue中提及的功能（可能是合理的技术债偿还或过度设计）
 *
 * @param requirements - Issue需求
 * @param tasks - Plan任务
 * @param planContent - Plan完整内容
 * @returns 额外功能列表及合理性判断
 */
function findUnexpectedFeatures(
  requirements: Requirement[],
  tasks: Task[],
  planContent: string
): { features: string[]; justified: boolean; justification?: string } {
  const extras: string[] = [];

  // 提取Issue中的所有关键词
  const issueKeywords = new Set<string>();
  requirements.forEach(req => {
    extractKeywords(req.description).forEach(kw => issueKeywords.add(kw.toLowerCase()));
  });

  // 检查每个任务是否与Issue需求相关
  tasks.forEach(task => {
    const taskKeywords = extractKeywords(task.title + ' ' + task.description);
    const isRelated = taskKeywords.some(kw => issueKeywords.has(kw.toLowerCase()));

    if (!isRelated) {
      // 检查是否是合理的技术改进关键词
      const technicalKeywords = ['重构', 'refactor', '测试', 'test', '文档', 'doc', '优化', 'optimize'];
      const isTechnical = technicalKeywords.some(kw =>
        task.title.toLowerCase().includes(kw) || task.description.toLowerCase().includes(kw)
      );

      if (!isTechnical) {
        extras.push(`${task.id}: ${task.title}`);
      }
    }
  });

  // 检查是否在Plan的Notes中解释了额外功能
  const notesRegex = /##\s*Notes([\s\S]*?)$/i;
  const notesMatch = planContent.match(notesRegex);
  const notesContent = notesMatch?.[1];
  const hasJustification = notesContent &&
                           (notesContent.toLowerCase().includes('额外') ||
                            notesContent.toLowerCase().includes('extra'));

  return {
    features: extras,
    justified: extras.length === 0 || hasJustification,
    justification: hasJustification && notesContent ? notesContent.trim() : undefined
  };
}

/**
 * 提取关键词
 *
 * 从文本中提取有意义的关键词（去除停用词）
 *
 * @param text - 输入文本
 * @returns 关键词数组
 */
function extractKeywords(text: string): string[] {
  // 停用词列表（中英文）
  const stopWords = new Set([
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    '的', '了', '和', '与', '或', '在', '是', '有', '个', '这', '那'
  ]);

  // 分词（简单按空格和标点分割）
  const words = text
    .toLowerCase()
    .split(/[\s,，.。;；:：!！?？(（)）\[\]【】]+/)
    .filter(word => word.length > 2 && !stopWords.has(word));

  // 去重并返回
  return Array.from(new Set(words));
}

/**
 * 主函数：执行完整的目标覆盖度检查
 *
 * @param issueBody - Issue内容
 * @param planContent - Plan内容
 * @returns 完整的覆盖度分析
 */
export function analyzeCoverage(
  issueBody: string,
  planContent: string
): CoverageAnalysis {
  // 1. 解析需求和任务
  const requirements = parseRequirements(issueBody);
  const tasks = parseTasks(planContent);

  // 2. 检查覆盖度
  const reqCoverage = checkIssueRequirements(requirements, planContent);
  const taskCompletion = checkTaskCompletion(tasks);
  const extras = findUnexpectedFeatures(requirements, tasks, planContent);

  // 3. 计算综合得分
  // 需求覆盖权重：40%
  // 任务完成权重：40%
  // 无额外功能奖励：20%
  const requirementScore = requirements.length > 0 ? reqCoverage.covered / requirements.length : 1.0;
  const taskScore = tasks.length > 0 ? taskCompletion.completed / tasks.length : 1.0;
  const extrasScore = extras.justified ? 1.0 : 0.5;

  const overallScore = requirementScore * 0.4 + taskScore * 0.4 + extrasScore * 0.2;

  // 4. 确定状态
  let status: 'PASS' | 'PARTIAL' | 'FAIL';
  if (overallScore >= 0.8) {
    status = 'PASS';
  } else if (overallScore >= 0.6) {
    status = 'PARTIAL';
  } else {
    status = 'FAIL';
  }

  return {
    requirements: {
      total: requirements.length,
      covered: reqCoverage.covered,
      uncovered: reqCoverage.uncovered,
      coverage_rate: requirementScore
    },
    tasks: {
      total: tasks.length,
      completed: taskCompletion.completed,
      incomplete: taskCompletion.incomplete,
      completion_rate: taskScore
    },
    extras,
    overall_score: overallScore,
    status
  };
}

// ==================== 导出 ====================

export {
  parseRequirements,
  parseTasks,
  checkIssueRequirements,
  checkTaskCompletion,
  findUnexpectedFeatures,
  extractKeywords,
  type Requirement,
  type Task,
  type CoverageAnalysis
};
