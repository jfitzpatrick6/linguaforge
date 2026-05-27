export default function Materials() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">My Study Materials</h1>
      <p className="text-gray-600 mb-6">
        Upload PDFs (grammar guides, dialogues, CEFR materials, etc.). These will be used for RAG when generating lessons.
      </p>

      <div className="bg-white border rounded-xl p-8">
        <p className="mb-4 text-sm text-gray-600">
          For now, use the <strong>Admin tab in the old Gradio app</strong> (or call the backend directly) to ingest PDFs.
        </p>
        <p className="text-sm">
          Once uploaded, they become available for RAG in lesson generation for that language.
        </p>
      </div>
    </div>
  )
}
