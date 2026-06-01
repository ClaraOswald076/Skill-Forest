import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Modal,
  Input,
  Form,
  Button,
  message,
  Tree,
  Card,
  Typography,
  Space,
  Tag,
  Divider,
} from 'antd';
import { useJobStore, useUIStore, useSkillStore, useTodoStore } from '@/store';
import AnalysisProgress from '@/components/analysis/AnalysisProgress';
import MergePreview from '@/components/analysis/MergePreview';
import type { ExtractedSkill, GeneratedTodo } from '@/types/analysis';

const { TextArea } = Input;
const { Title, Text } = Typography;

export default function JobInputModal() {
  const navigate = useNavigate();
  const { jobInputModalOpen, closeJobInput } = useUIStore();
  const { isAnalyzing, analysisResult, mergeDecisions, startAnalysis, setMergeDecision, confirmAndSave, clearAnalysis } =
    useJobStore();
  const { fetchSkillTree } = useSkillStore();
  const { fetchTodos } = useTodoStore();
  const [form] = Form.useForm();
  const [saving, setSaving] = useState(false);

  const [analysisStep, setAnalysisStep] = useState(0);

  const handleAnalyze = useCallback(async () => {
    const values = await form.validateFields();
    if (!values.raw_text?.trim()) {
      message.warning('请输入岗位要求文本');
      return;
    }

    // Simulate progress steps
    setAnalysisStep(0);
    const timer = setInterval(() => {
      setAnalysisStep((prev) => (prev < 3 ? prev + 1 : prev));
    }, 1200);

    try {
      await startAnalysis(values.raw_text, values.title, values.company, values.url);
      setAnalysisStep(4); // Complete
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : '分析失败，请重试';
      message.error(msg);
    } finally {
      clearInterval(timer);
    }
  }, [form, startAnalysis]);

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      const job = await confirmAndSave();
      if (job) {
        message.success(`岗位「${job.title}」已保存，共 ${job.skills.length} 项技能，${job.todos.length} 个任务`);
        // Refresh stores
        await fetchSkillTree();
        await fetchTodos();
        // Reset
        form.resetFields();
        clearAnalysis();
        closeJobInput();
        navigate(`/jobs/${job.id}`);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : '保存失败';
      message.error(msg);
    } finally {
      setSaving(false);
    }
  }, [confirmAndSave, fetchSkillTree, fetchTodos, form, clearAnalysis, closeJobInput, navigate]);

  const handleCancel = () => {
    form.resetFields();
    clearAnalysis();
    closeJobInput();
  };

  // Build skill preview tree
  const buildPreviewTree = (skills: ExtractedSkill[]) => {
    const l1Map: Record<string, Record<string, ExtractedSkill[]>> = {};
    for (const s of skills) {
      if (!l1Map[s.category_l1]) l1Map[s.category_l1] = {};
      if (!l1Map[s.category_l1][s.category_l2]) l1Map[s.category_l1][s.category_l2] = [];
      l1Map[s.category_l1][s.category_l2].push(s);
    }
    return Object.entries(l1Map).map(([l1, l2Map]) => ({
      key: `preview:${l1}`,
      title: <span className="font-bold">{l1}</span>,
      children: Object.entries(l2Map).map(([l2, skills]) => ({
        key: `preview:${l1}/${l2}`,
        title: <span className="font-medium">{l2}</span>,
        children: skills.map((s) => ({
          key: `preview:${l1}/${l2}/${s.name}`,
          title: (
            <span>
              {s.name}
              <Tag color="blue" className="ml-2 text-xs">
                {s.proficiency}
              </Tag>
              {s.merge_with_existing_id && (
                <Tag color="orange" className="ml-1 text-xs">
                  待合并
                </Tag>
              )}
            </span>
          ),
          isLeaf: true,
        })),
      })),
    }));
  };

  return (
    <>
      <Modal
        title="添加新岗位"
        open={jobInputModalOpen && !analysisResult}
        onCancel={handleCancel}
        onOk={handleAnalyze}
        confirmLoading={isAnalyzing}
        okText="开始分析"
        cancelText="取消"
        width={720}
        centered
      >
        <Form form={form} layout="vertical">
          <Form.Item label="岗位名称（可选，AI 会自动提取）" name="title">
            <Input placeholder="如：算法工程师" />
          </Form.Item>
          <Form.Item label="公司（可选）" name="company">
            <Input placeholder="如：字节跳动" />
          </Form.Item>
          <Form.Item label="岗位链接（可选）" name="url">
            <Input placeholder="如：https://www.zhipin.com/job_detail/xxx.html" />
          </Form.Item>
          <Form.Item
            label="岗位要求文本"
            name="raw_text"
            rules={[{ required: true, message: '请粘贴岗位要求文本' }]}
          >
            <TextArea
              rows={12}
              placeholder={`请粘贴完整的岗位要求（JD）文本，例如：

职位要求
1、2027届本科及以上学历在读；
2、熟练掌握Linux环境下的C/C++、Python语言；
3、具备扎实的计算机科学功底和编程能力...
...`}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* Analysis progress overlay */}
      <AnalysisProgress open={isAnalyzing} currentStep={analysisStep} />

      {/* Results modal */}
      <Modal
        title="分析结果预览"
        open={!!analysisResult && !isAnalyzing}
        onCancel={handleCancel}
        onOk={handleSave}
        confirmLoading={saving}
        okText="确认保存"
        cancelText="取消"
        width={900}
        centered
        style={{ top: 20 }}
      >
        {analysisResult && (
          <div className="max-h-[70vh] overflow-auto">
            {/* Summary */}
            <Card size="small" className="mb-4 bg-blue-50">
              <Text strong>{analysisResult.job_title}</Text>
              {analysisResult.company && (
                <Text> — {analysisResult.company}</Text>
              )}
              <p className="mt-1 text-gray-600 text-sm">{analysisResult.summary}</p>
            </Card>

            {/* Merge suggestions */}
            <MergePreview
              suggestions={analysisResult.merge_suggestions}
              decisions={mergeDecisions}
              onDecisionChange={setMergeDecision}
            />

            {/* Skills preview */}
            <Card
              title={`提取的技能 (${analysisResult.skills.length})`}
              size="small"
              className="mb-4"
            >
              <Tree
                treeData={buildPreviewTree(analysisResult.skills)}
                defaultExpandAll
                blockNode
              />
            </Card>

            {/* Todos preview */}
            <Card
              title={`生成的学习任务 (${analysisResult.todos.length})`}
              size="small"
            >
              {analysisResult.todos.map((todo: GeneratedTodo, i: number) => (
                <div key={i} className="mb-2 pb-2 border-b border-gray-100 last:border-0">
                  <Text>{i + 1}. {todo.description}</Text>
                  <div className="mt-1">
                    <Tag color="green">{todo.proficiency_required}</Tag>
                    {todo.skill_names.map((sn) => (
                      <Tag key={sn}>{sn}</Tag>
                    ))}
                  </div>
                </div>
              ))}
            </Card>
          </div>
        )}
      </Modal>
    </>
  );
}
