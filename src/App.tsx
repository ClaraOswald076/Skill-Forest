import { Routes, Route } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import ErrorBoundary from './components/common/ErrorBoundary';
import DashboardPage from './components/dashboard/DashboardPage';
import SkillTreePage from './components/skills/SkillTreePage';
import JobListPage from './components/jobs/JobListPage';
import JobDetailPage from './components/jobs/JobDetailPage';
import TodoListPage from './components/todos/TodoListPage';
import LearningPage from './components/learning/LearningPage';
import ErrorBookPage from './components/learning/ErrorBookPage';

export default function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/skills" element={<SkillTreePage />} />
          <Route path="/jobs" element={<JobListPage />} />
          <Route path="/jobs/:id" element={<JobDetailPage />} />
          <Route path="/todos" element={<TodoListPage />} />
          <Route path="/learn/:todoId" element={<LearningPage />} />
          <Route path="/learn/errors" element={<ErrorBookPage />} />
        </Route>
      </Routes>
    </ErrorBoundary>
  );
}
