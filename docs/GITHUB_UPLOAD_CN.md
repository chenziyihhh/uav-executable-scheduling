# 上传与论文描述调整

## 上传顺序
1. 解压 UAV_GitHub_Documents.zip，将其中内容直接放在 GitHub 仓库根目录，保留 reproducibility/、figures/、docs/ 结构。
2. 将 UAV_Experiment_Evidence.zip 作为同一仓库的 Release 附件上传；不要把大检查点逐个拖进网页文件编辑区。
3. 选择并固定发布标签（例如 v1.0），记录实际仓库链接和该 Release 链接。
4. 在 README.md 中补入实际链接。确认作者有权发布的代码和第三方材料范围后设置相应许可证；本包未擅自指定开源许可证。

## 论文路径对应
| 论文提及内容 | 仓库路径 |
|---|---|
| 指标、事件顺序、计时边界 | reproducibility/METRIC_PROTOCOL.md |
| 非线性质量证书输入 | reproducibility/certificate_inputs.json |
| 质量界依赖与验证范围 | reproducibility/CERTIFICATE_DEPENDENCIES.md |
| 固定任务、方法配置、证据入口 | reproducibility/experiment_spec.json |
| 全部160个比较结果及成本 | reproducibility/all_method_costs.csv |
| 绘图数据及脚本 | figures/ |
| 原始比较记录、构造数组及检查点 | Release 附件 UAV_Experiment_Evidence.zip |

## 建议替换论文的 Reproducibility 段落
在真实仓库及 Release 发布后使用以下文字，将所有占位符替换为实际地址：

> Supplementary materials are available at [REPOSITORY_URL], release [RELEASE_TAG]. The repository provides the metric protocol, fixed comparison specifications, all 160 method–condition outcomes and costs, figure data and plotting scripts, and full-precision quality-profile inputs. The accompanying release archive provides saved protocol records, certificate construction artifacts, and the associated code dependencies. The documented replay procedure reconstructs metrics from saved records; the certificate documentation specifies the scope of the saved checks and the requirements for full enclosure reconstruction.

LaTeX 链接写法：\url{实际仓库地址}；固定版本可链接实际 release/tag 页面。

无需逐项把本机 E: 路径写进论文。两份原始 MD 中的路径相对于证据压缩包中嵌套的原实验项目目录；保留此目录布局以使旧 codec 的相对路径可解析。

本次只整理既有文件，没有新增实验、修改结果或重建完整非线性质量证明。上传完成不等于已经独立验证所有历史运行。
