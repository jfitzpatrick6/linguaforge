import { useState } from 'react';
import { api } from '../api/client';

export default function Curriculum() {
  const [userId, setUserId] = useState('test_user');
  const [overview, setOverview] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadOverview = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getCurriculumOverview(userId);
      setOverview(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">My Curriculum</h1>

      <div className="flex gap-3 mb-6">
        <input
          value={userId}
          onChange={e => setUserId(e.target.value)}
          className="border px-3 py-2 rounded-lg w-64"
          placeholder="User ID"
        />
        <button
          onClick={loadOverview}
          disabled={loading}
          className="px-5 py-2 bg-gray-800 text-white rounded-lg text-sm"
        >
          {loading ? 'Loading...' : 'Load Current Curriculum'}
        </button>
      </div>

      {error && <div className="text-red-600 mb-4">{error}</div>}

      {overview && (
        <div className="bg-white border rounded-2xl p-6">
          <div className="grid grid-cols-3 gap-4 mb-6 text-center">
            <div>
              <div className="text-2xl font-semibold">{overview.total_blocks}</div>
              <div className="text-sm text-gray-500">Total Blocks</div>
            </div>
            <div>
              <div className="text-2xl font-semibold text-emerald-600">{overview.active_count}</div>
              <div className="text-sm text-gray-500">Active</div>
            </div>
            <div>
              <div className="text-2xl font-semibold text-blue-600">{overview.completed_count}</div>
              <div className="text-sm text-gray-500">Completed</div>
            </div>
          </div>

          {overview.next_block && (
            <div className="mb-6">
              <div className="text-sm font-medium text-gray-500 mb-1">Next Focus</div>
              <div className="font-semibold text-lg">{overview.next_block.title}</div>
              <div className="text-sm text-gray-600">{overview.next_block.description}</div>
            </div>
          )}

          <pre className="text-xs bg-gray-50 p-4 rounded-xl overflow-auto">
            {JSON.stringify(overview, null, 2)}
          </pre>
        </div>
      )}

      {!overview && (
        <div className="text-gray-500 text-sm">
          Run an assessment on the Dashboard first, then load your curriculum here.
        </div>
      )}
    </div>
  );
}
