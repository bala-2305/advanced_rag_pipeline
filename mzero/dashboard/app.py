"""Embedded HTML/JS Dashboard for mzero."""

def get_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>mzero Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0b0f19;
            --card-bg: rgba(22, 28, 45, 0.7);
            --border: rgba(255, 255, 255, 0.08);
            --accent: #6366f1;
            --accent-hover: #4f46e5;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --success: #10b981;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
        body { background: var(--bg); color: var(--text-primary); padding: 2rem; min-height: 100vh; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
        .logo { font-size: 1.8rem; font-weight: 700; background: linear-gradient(135deg, #a5b4fc, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .badge { background: rgba(99, 102, 241, 0.2); border: 1px solid var(--accent); padding: 0.3rem 0.8rem; borderRadius: 20px; font-size: 0.85rem; color: #a5b4fc; }

        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        .card { background: var(--card-bg); backdrop-filter: blur(12px); border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem; }
        .card h3 { font-size: 0.85rem; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 0.5rem; letter-spacing: 0.05em; }
        .card .value { font-size: 2rem; font-weight: 700; color: #fff; }

        .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
        @media (max-width: 900px) { .main-content { grid-template-columns: 1fr; } }

        .panel { background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem; display: flex; flex-direction: column; }
        .panel h2 { font-size: 1.2rem; margin-bottom: 1rem; font-weight: 600; }

        .chat-box { flex: 1; min-height: 250px; border: 1px solid var(--border); border-radius: 12px; padding: 1rem; background: rgba(0,0,0,0.2); overflow-y: auto; margin-bottom: 1rem; }
        .input-group { display: flex; gap: 0.5rem; }
        input[type="text"] { flex: 1; background: rgba(255,255,255,0.05); border: 1px solid var(--border); padding: 0.8rem 1rem; border-radius: 8px; color: #fff; outline: none; }
        input[type="text"]:focus { border-color: var(--accent); }
        button { background: var(--accent); color: #fff; border: none; padding: 0.8rem 1.5rem; border-radius: 8px; cursor: pointer; font-weight: 600; transition: background 0.2s; }
        button:hover { background: var(--accent-hover); }

        .doc-list { list-style: none; }
        .doc-item { display: flex; justify-content: space-between; padding: 0.8rem 0; border-bottom: 1px solid var(--border); font-size: 0.9rem; }
        .doc-item:last-child { border-bottom: none; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">mzero Dashboard</div>
        <div class="badge">Zero-Config RAG Active</div>
    </div>

    <div class="grid">
        <div class="card">
            <h3>Documents Indexed</h3>
            <div class="value" id="stat-docs">0</div>
        </div>
        <div class="card">
            <h3>Chunks Stored</h3>
            <div class="value" id="stat-chunks">0</div>
        </div>
        <div class="card">
            <h3>Total Queries</h3>
            <div class="value" id="stat-queries">0</div>
        </div>
        <div class="card">
            <h3>Cache Hit Rate</h3>
            <div class="value" id="stat-cache">0%</div>
        </div>
    </div>

    <div class="main-content">
        <div class="panel">
            <h2>Interactive RAG Playground</h2>
            <div class="chat-box" id="chat-box">
                <p style="color: var(--text-secondary);">Ask any question about your indexed documents...</p>
            </div>
            <div class="input-group">
                <input type="text" id="query-input" placeholder="Type your question...">
                <button onclick="askQuestion()">Ask</button>
            </div>
        </div>

        <div class="panel">
            <h2>Indexed Knowledge Sources</h2>
            <ul class="doc-list" id="doc-list">
                <li style="color: var(--text-secondary);">Loading sources...</li>
            </ul>
        </div>
    </div>

    <script>
        async function loadStats() {
            try {
                const res = await fetch('/status');
                const data = await res.json();
                document.getElementById('stat-docs').innerText = data.total_documents;
                document.getElementById('stat-chunks').innerText = data.total_chunks;
                document.getElementById('stat-queries').innerText = data.total_queries;
                document.getElementById('stat-cache').innerText = Math.round(data.cache_hit_rate * 100) + '%';
            } catch (e) { console.error(e); }
        }

        async function loadSources() {
            try {
                const res = await fetch('/sources');
                const docs = await res.json();
                const listEl = document.getElementById('doc-list');
                listEl.innerHTML = '';
                if (docs.length === 0) {
                    listEl.innerHTML = '<li style="color: var(--text-secondary);">No documents added yet. Use CLI or /upload API.</li>';
                    return;
                }
                docs.forEach(d => {
                    listEl.innerHTML += `<li class="doc-item"><span>📄 ${d.id}</span><span style="color: var(--text-secondary);">${d.type}</span></li>`;
                });
            } catch (e) { console.error(e); }
        }

        async function askQuestion() {
            const input = document.getElementById('query-input');
            const question = input.value.trim();
            if (!question) return;

            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML += `<p style="margin-bottom: 0.8rem;"><strong>You:</strong> ${question}</p>`;
            input.value = '';

            chatBox.innerHTML += `<p id="loading" style="color: var(--text-secondary);">AI is answering...</p>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const res = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: question })
                });
                const data = await res.json();
                document.getElementById('loading').remove();
                chatBox.innerHTML += `<p style="margin-bottom: 0.8rem; color: #a5b4fc;"><strong>mzero:</strong> ${data.answer}</p>`;
                if (data.citations && data.citations.length > 0) {
                    let citeHtml = '<div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;">Sources: ';
                    data.citations.forEach(c => citeHtml += `[${c.source_file}] `);
                    citeHtml += '</div>';
                    chatBox.innerHTML += citeHtml;
                }
                chatBox.scrollTop = chatBox.scrollHeight;
                loadStats();
            } catch (e) {
                document.getElementById('loading').innerText = 'Error fetching answer.';
            }
        }

        loadStats();
        loadSources();
        setInterval(loadStats, 5000);
    </script>
</body>
</html>
"""
