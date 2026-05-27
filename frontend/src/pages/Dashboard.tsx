import { useState } from 'react';
import { api } from '../api/client';

interface Question {
  question: string;
  options: Record<string, string>;
  correct?: string;
  skill?: string;
}

export default function Dashboard() {
  const [userId, setUserId] = useState('test_user');
  const [language, setLanguage] = useState('es');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Assessment state
  const [diagnosticQuestions, setDiagnosticQuestions] = useState<Question[]>([]);
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [assessmentResult, setAssessmentResult] = useState<any>(null);

  const startAssessment = async () => {
    setLoading(true);
    setError(null);
    setDiagnosticQuestions([]);
    setUserAnswers({});
    setAssessmentResult(null);

    try {
      const res: any = await api.startAssessment({ user_id: userId, target_language: language });
      setDiagnosticQuestions(res.questions || []);
    } catch (e: any) {
      setError(e.message || 'Failed to start assessment');
    } finally {
      setLoading(false);
    }
  };

  const selectAnswer = (qIndex: number, optionKey: string) => {
    setUserAnswers(prev => ({ ...prev, [qIndex]: optionKey }));
  };

  const submitAssessment = async () => {
    if (diagnosticQuestions.length === 0) return;

    setLoading(true);
    setError(null);

    try {
      const answers = diagnosticQuestions.map((q, index) => ({
        question: q,
        selected: userAnswers[index] || 'A'
      }));

      const result = await api.submitAssessment({
        user_id: userId,
        target_language: language,
        answers
      });

      setAssessmentResult(result);
      setDiagnosticQuestions([]); // Hide questions after submit
    } catch (e: any) {
      setError(e.message || 'Failed to submit assessment');
    } finally {
      setLoading(false);
    }
  };

  const allAnswered = diagnosticQuestions.length > 0 && 
    Object.keys(userAnswers).length === diagnosticQuestions.length;

  return (
    <div className="max-w-4xl">
      <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
      <p className="text-gray-600 mb-8">Test the full adaptive learning process.</p>

      {/* Assessment Section */}
      <div className="bg-white border rounded-2xl p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4">1. Diagnostic Assessment (Onboarding)</h2>

        <div className="flex gap-4 mb-6">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">User ID</label>
            <input
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full border rounded-lg px-4 py-2"
            />
          </div>
          <div className="w-48">
            <label className="block text-sm font-medium mb-1">Target Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full border rounded-lg px-4 py-2"
            >
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="it">Italian</option>
            </select>
          </div>
        </div>

        {!diagnosticQuestions.length && !assessmentResult && (
          <button
            onClick={startAssessment}
            disabled={loading}
            className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Starting Assessment...' : 'Start Diagnostic Assessment'}
          </button>
        )}

        {/* Show Questions */}
        {diagnosticQuestions.length > 0 && (
          <div className="mt-6">
            <h3 className="font-medium mb-4">Answer the following questions:</h3>
            <div className="space-y-6">
              {diagnosticQuestions.map((q, index) => (
                <div key={index} className="border rounded-xl p-5">
                  <p className="font-medium mb-3">{index + 1}. {q.question}</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {Object.entries(q.options || {}).map(([key, value]) => (
                      <button
                        key={key}
                        onClick={() => selectAnswer(index, key)}
                        className={`text-left px-4 py-2 rounded-lg border transition ${
                          userAnswers[index] === key 
                            ? 'border-indigo-500 bg-indigo-50' 
                            : 'hover:bg-gray-50'
                        }`}
                      >
                        <span className="font-medium mr-2">{key}.</span> {value as string}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <button
              onClick={submitAssessment}
              disabled={!allAnswered || loading}
              className="mt-6 px-8 py-3 bg-emerald-600 text-white rounded-xl font-medium disabled:opacity-50 hover:bg-emerald-700"
            >
              {loading ? 'Submitting...' : 'Submit Assessment'}
            </button>
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">
            <div className="font-medium">Assessment Error</div>
            <div className="mt-1 font-mono text-xs break-all">{error}</div>
            <div className="mt-2 text-xs">Check that the backend is running and you have restarted it after recent changes.</div>
          </div>
        )}

        {assessmentResult && (
          <div className="mt-6 p-5 bg-emerald-50 border border-emerald-200 rounded-2xl">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-semibold text-emerald-800">Assessment Complete!</h3>
                <p className="text-sm text-emerald-700">
                  Estimated level: <strong>{assessmentResult.assessment_results?.estimated_cefr}</strong> • 
                  Blocks created: <strong>{assessmentResult.curriculum_blocks_created}</strong>
                </p>
              </div>
              <button 
                onClick={async () => {
                  try {
                    const overview = await api.getCurriculumOverview(userId);
                    setAssessmentResult(prev => ({ ...prev, curriculum_overview: overview }));
                  } catch (e: any) { setError(e.message); }
                }}
                className="text-xs px-3 py-1.5 bg-white border rounded-lg hover:bg-gray-50"
              >
                Refresh Curriculum
              </button>
            </div>

            {assessmentResult.assessment_results?.weak_areas?.length > 0 && (
              <div className="mb-4">
                <div className="text-xs font-medium text-emerald-700 mb-1">Weak areas identified (these should now have lower mastery and may have triggered remedial blocks):</div>
                <div className="flex flex-wrap gap-1.5">
                  {assessmentResult.assessment_results.weak_areas.map((area: string, i: number) => (
                    <span key={i} className="text-xs bg-white px-2.5 py-0.5 rounded-full border">{area}</span>
                  ))}
                </div>
              </div>
            )}

            {assessmentResult.curriculum_overview && (
              <div className="mb-4 p-3 bg-white rounded-lg text-sm border">
                <div className="font-medium mb-1">Current Curriculum Status</div>
                <div>Total blocks: {assessmentResult.curriculum_overview.total_blocks} • Active: {assessmentResult.curriculum_overview.active_count}</div>
                {assessmentResult.curriculum_overview.next_block && (
                  <div className="mt-1 text-emerald-700 text-xs">Next focus: {assessmentResult.curriculum_overview.next_block.title}</div>
                )}
              </div>
            )}

            <details className="text-xs">
              <summary className="cursor-pointer font-medium">Show raw response (for debugging)</summary>
              <pre className="bg-white p-3 rounded mt-2 overflow-auto max-h-64 text-[10px]">
                {JSON.stringify(assessmentResult, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>

      {assessmentResult && (
        <div className="mt-4">
          <button
            onClick={async () => {
              try {
                const overview = await api.getCurriculumOverview(userId);
                // Show curriculum in a simple way
                alert("Curriculum Overview (check console or enhance UI):\n" + JSON.stringify(overview, null, 2));
              } catch (e: any) {
                setError(e.message);
              }
            }}
            className="text-sm px-4 py-2 border rounded-lg hover:bg-gray-50"
          >
            View Current Curriculum Overview
          </button>
        </div>
      )}

      <div className="mt-6">
        <button
          onClick={async () => {
            try {
              const overview = await api.getCurriculumOverview(userId);
              setAssessmentResult(prev => ({ ...prev, curriculum_overview: overview }));
            } catch (e: any) {
              setError(e.message);
            }
          }}
          className="text-sm px-4 py-2 border rounded-lg hover:bg-gray-50"
        >
          Refresh Current Curriculum Overview
        </button>
      </div>

      <div className="mt-6 text-sm text-gray-500">
        After assessment, go to the <a href="/lessons" className="text-blue-600 underline font-medium">Lessons page</a> to generate a lesson and test the full practice + automatic adaptation loop.
      </div>
    </div>
  );
}
