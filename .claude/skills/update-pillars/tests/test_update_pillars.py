"""
主测试文件 - update-pillars skill 完整测试套件

包含所有测试类别的导入和集中执行入口。
实际测试分布在:
- test_functional.py: 核心功能测试
- test_arguments.py: 参数验证测试 (待实现)
- test_safety.py: 安全机制测试 (待实现)
- test_error_handling.py: 错误处理测试 (待实现)
- test_integration.py: 集成测试 (待实现)

运行所有测试:
    pytest .claude/skills/update-pillars/tests/

运行特定文件:
    pytest .claude/skills/update-pillars/tests/test_functional.py
"""

if __name__ == "__main__":
    import pytest
    import sys

    # 运行所有测试
    sys.exit(pytest.main([__file__]))
