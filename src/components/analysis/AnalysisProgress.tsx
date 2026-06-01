import { Modal, Steps } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

const steps = [
  { title: '提交文本', description: '发送到 AI 分析' },
  { title: '提取技能', description: '识别技术能力' },
  { title: '分类整理', description: '建立技能层次' },
  { title: '生成任务', description: '创建学习计划' },
];

interface Props {
  open: boolean;
  currentStep: number;
}

export default function AnalysisProgress({ open, currentStep }: Props) {
  return (
    <Modal
      open={open}
      closable={false}
      footer={null}
      title="正在分析岗位要求..."
      centered
    >
      <div className="py-6">
        <div className="text-center mb-6">
          <LoadingOutlined style={{ fontSize: 48, color: '#1677ff' }} />
          <p className="mt-4 text-gray-500">
            AI 正在分析您提供的岗位描述，请稍候...
          </p>
        </div>
        <Steps
          current={currentStep}
          items={steps}
          direction="vertical"
          size="small"
        />
      </div>
    </Modal>
  );
}
