import { useEffect } from 'react';
import { Typography, Spin } from 'antd';
import SkillTree from './SkillTree';
import SkillDetailPanel from './SkillDetailPanel';
import { useSkillStore } from '@/store';
import EmptyState from '@/components/common/EmptyState';

const { Title } = Typography;

export default function SkillTreePage() {
  const { skillTree, selectedSkill, loading, fetchSkillTree, selectSkill } =
    useSkillStore();

  useEffect(() => {
    fetchSkillTree();
  }, [fetchSkillTree]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spin size="large" tip="加载技能树..." />
      </div>
    );
  }

  if (skillTree.length === 0) {
    return (
      <EmptyState
        description="还没有技能数据"
        actionText="去添加岗位"
        onAction={() => (window.location.href = '/jobs')}
      />
    );
  }

  return (
    <div>
      <Title level={3} className="mb-6">🌳 技能树</Title>
      <div className="flex gap-6" style={{ minHeight: 500 }}>
        {/* Left: Tree */}
        <div className="w-2/5 bg-white rounded-lg p-4 border border-gray-200 overflow-auto">
          <SkillTree tree={skillTree} onSelectSkill={selectSkill} />
        </div>

        {/* Right: Detail panel */}
        <div className="w-3/5">
          {selectedSkill ? (
            <SkillDetailPanel skill={selectedSkill} />
          ) : (
            <div className="flex items-center justify-center h-full bg-white rounded-lg border border-gray-200 text-gray-400">
              点击左侧技能查看详情
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
