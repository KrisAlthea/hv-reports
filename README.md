# hv-reports

基于 `hv-analysis`（横纵分析法）生成的行业、产品与前沿技术深度研报发布仓库。

本仓库通过 **Cloudflare Pages** 全托管部署，并绑定域名 `report.carpediemai.me`。

## 目录结构
- `index.html`: 报告列表导航首页
- `reports/`: 存放各期报告的 HTML 及 PDF 文件
- `assets/`: 静态资源文件

## 工作流
1. 使用 `hv-analysis` 技能生成 Markdown 研报与排版精美的 HTML/PDF。
2. 放入本仓库并提交推送。
3. Cloudflare Pages 自动触发全球边缘节点部署。
