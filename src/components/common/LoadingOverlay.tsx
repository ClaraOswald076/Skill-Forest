import { Spin } from 'antd';

interface Props {
  tip?: string;
}

export default function LoadingOverlay({ tip = '加载中...' }: Props) {
  return (
    <div className="flex items-center justify-center h-64">
      <Spin size="large" tip={tip}>
        <div className="p-12" />
      </Spin>
    </div>
  );
}
