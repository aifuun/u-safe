# Secret Management Rules

> Never hardcode secrets in code.

## Rules

- **加密密钥**: 由 Argon2id 从用户密码派生，不存储明文密码
- **Salt**: 随机生成，存储在 `.u-safe/keys/` 中
- **内存安全**: 使用 `zeroize` crate 清零敏感内存
- **无网络**: U-Safe 是离线应用，无 API key 管理需求

## Checklist

- [ ] 密码不写入日志
- [ ] 密钥用完后 zeroize 清零
- [ ] 临时解密文件关闭后立即删除
- [ ] 无明文缓存到宿主硬盘
