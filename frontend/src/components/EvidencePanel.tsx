import { useState } from "react";
import { requestJson } from "../api";
import type { DocumentRecord, SearchResult } from "../types";

export function EvidencePanel({ documents }: { documents: DocumentRecord[] }) {
  const [query, setQuery] = useState("SSO security review");
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [searching, setSearching] = useState(false);

  async function searchEvidence() {
    setSearching(true);
    setError(null);
    try {
      const body = await requestJson<{ query: string; results: SearchResult[] }>("/api/documents/search", {
        method: "POST",
        body: JSON.stringify({ query, limit: 4 })
      });
      setResults(body.results);
    } catch (caught) {
      setResults(null);
      setError(caught instanceof Error ? caught.message : "Search failed.");
    } finally {
      setSearching(false);
    }
  }

  return (
    <div className="stack">
      <div className="panel">
        <div className="panel__title">Company evidence</div>
        <form
          className="search-row"
          onSubmit={(event) => {
            event.preventDefault();
            void searchEvidence();
          }}
        >
          <label htmlFor="evidence-query">Search company evidence</label>
          <div>
            <input
              id="evidence-query"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
            <button type="submit" className="primary" disabled={searching}>
              {searching ? "Searching..." : "Search evidence"}
            </button>
          </div>
        </form>
        {error && <p className="run-status__error">{error}</p>}
        {results && results.length === 0 && <p className="empty">No matching chunks for that query.</p>}
        {results && results.length > 0 && (
          <div className="stack">
            {results.map((result) => (
              <article className="evidence-hit" key={`${result.source}-${result.chunk_index}`}>
                <header>
                  <strong>{result.source}</strong>
                  <span>chunk {result.chunk_index}</span>
                  <span>score {result.score}</span>
                </header>
                <p>{result.content}</p>
              </article>
            ))}
          </div>
        )}
      </div>
      <div className="doc-grid">
        {documents.map((document) => (
          <article className="doc-card" key={document.source}>
            <span>{document.chunks} chunks</span>
            <strong>{document.source}</strong>
            <p>{document.preview}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
