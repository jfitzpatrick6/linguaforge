import { useState } from 'react';
import { api } from '../api/client';

export default function Lessons() {
  const [userId, setUserId] = useState('test_user');
  const [language, setLanguage] = useState('es');
  const [topic, setTopic] = useState('ser vs estar');
  const [level, setLevel] = useState('A1');

  const [lesson, setLesson] = useState<any>(null);
  const [practice, setPractice] = useState<any>(null);
  const [practiceResult, setPracticeResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateLesson = async () => {
    setLoading(true);
    setError(null);
    setLesson(null);
    setPractice(null);
    setPracticeResult(null);

    try {
      const res = await api.generateLesson({
        user_id: userId,
        language,
        topic,
        skill_level: level,
      });
      setLesson(res);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const generatePractice = async () => {
    if (!lesson) return;
    setLoading(true);
    setError(null);

    try {
      const res = await api.generatePractice({
        user_id: userId,
        language,
        topic,
        level,
      });
      setPractice(res);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const [selectedPracticeAnswers, setSelectedPracticeAnswers] = useState<Record<number, string>>({});

  const submitRealPractice = async () => {
    if (!practice) return;

    const questions = practice.questions || [];
    const answers = questions.map((q: any, i: number) => ({
      question: q,
      selected: selectedPracticeAnswers[i] || Object.keys(q.options || {})[0],
    }));

    setLoading(true);
    setError(null);

    try {
      const res = await api.submitPractice({
        user_id: userId,
        language,
        topic,
        level,
        answers,
      });
      setPracticeResult(res);
      setSelectedPracticeAnswers({});
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const selectPracticeAnswer = (qIndex: number, option: string) => {
    setSelectedPracticeAnswers(prev => ({ ...prev, [qIndex]: option }));
  };

  return (
    <div className="max-w-4xl">
      <h1 className="text-3xl font-bold mb-2">Generate Lessons + Practice Loop</h1>
      <p className="text-gray-600 mb-6">
        This page lets you test the full adaptive cycle: Lesson → Practice → Mastery Update → Curriculum Adaptation.
      </p>

      <div className="bg-white border rounded-2xl p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">User ID</label>
            <input value={userId} onChange={e => setUserId(e.target.value)} className="border w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Language</label>
            <select value={language} onChange={e => setLanguage(e.target.value)} className="border w-full px-3 py-2 rounded-lg">
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Topic / Skill</label>
            <input value={topic} onChange={e => setTopic(e.target.value)} className="border w-full px-3 py-2 rounded-lg" placeholder="ser vs estar, present perfect..." />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Level</label>
            <select value={level} onChange={e => setLevel(e.target.value)} className="border w-full px-3 py-2 rounded-lg">
              <option value="A1">A1</option>
              <option value="A2">A2</option>
              <option value="B1">B1</option>
            </select>
          </div>
        </div>

        <button
          onClick={generateLesson}
          disabled={loading || !topic.trim()}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium disabled:opacity-50"
        >
          {loading ? 'Working...' : 'Generate Lesson'}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-200 text-red-700 p-4 rounded-2xl mb-6">
          {error}
        </div>
      )}

      {lesson && (
        <div className="bg-white border rounded-2xl p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold">{lesson.title}</h2>
            <span className="text-xs px-3 py-1 bg-gray-100 rounded-full">{level}</span>
          </div>

          <div className="prose max-w-none mb-6">
            <p>{lesson.explanation}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div>
              <div className="font-medium mb-2">Examples</div>
              <ul className="list-disc pl-5 space-y-1">
                {lesson.examples?.map((ex: string, i: number) => <li key={i}>{ex}</li>)}
              </ul>
            </div>
            <div>
              <div className="font-medium mb-2">Practice Ideas</div>
              <ul className="list-disc pl-5 space-y-1">
                {lesson.practice_items?.map((p: string, i: number) => <li key={i}>{p}</li>)}
              </ul>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t">
            <button
              onClick={generatePractice}
              disabled={loading}
              className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm font-medium"
            >
              {loading ? 'Generating practice...' : 'Generate Practice Questions'}
            </button>
          </div>
        </div>
      )}

      {practice && (
        <div className="bg-white border rounded-2xl p-6">
          <h3 className="font-semibold mb-4 text-lg">Practice Questions</h3>

          <div className="space-y-5 mb-8">
            {practice.questions?.map((q: any, i: number) => (
              <div key={i} className="border rounded-xl p-4">
                <div className="font-medium mb-3">{i + 1}. {q.question}</div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                  {Object.entries(q.options || {}).map(([key, val]) => (
                    <div key={key} className="px-3 py-1.5 bg-gray-50 rounded border text-gray-700">
                      {key}. {val as string}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => submitPractice('strong')}
              disabled={loading}
              className="px-5 py-2 bg-green-600 hover:bg-green-700 text-white rounded-xl text-sm font-medium"
            >
              Submit as Strong Performance
            </button>
            <button
              onClick={() => submitPractice('weak')}
              disabled={loading}
              className="px-5 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-xl text-sm font-medium"
            >
              Submit as Weak Performance
            </button>
          </div>

          {practiceResult && (
            <div className="mt-6 p-5 bg-gray-50 border rounded-2xl">
              <div className="font-medium mb-2">Practice Result + Adaptation</div>
              <pre className="text-xs bg-white p-4 rounded-xl overflow-auto max-h-[400px]">
                {JSON.stringify(practiceResult, null, 2)}
              </pre>
              <p className="text-xs text-gray-500 mt-3">
                Look for "adaptation" in the response to see if remedial blocks were created.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
