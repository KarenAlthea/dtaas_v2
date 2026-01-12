from fastapi import APIRouter
from fastapi.responses import HTMLResponse

ui_router = APIRouter()


@ui_router.get("/ui/builder", response_class=HTMLResponse, include_in_schema=False)
def ui_builder():
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>DTaaS – Template Builder UI</title>
  <style>
    body { font-family: system-ui, Arial; max-width: 980px; margin: 40px auto; padding: 0 16px; }
    .row { display:flex; gap:12px; align-items:center; flex-wrap:wrap; }
    button { padding: 10px 14px; cursor: pointer; }
    pre { background:#f6f6f6; padding:12px; overflow:auto; }
    #editor_holder { margin-top: 16px; }
    label { font-weight: 600; }
    input, select { padding: 6px; }
  </style>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@json-editor/json-editor@latest/dist/css/jsoneditor.min.css">
</head>
<body>
  <h2>DTaaS – Template Builder</h2>
  <p>Scegli il caso → la piattaforma genera il template → compili il form → esegui KPI o SimPy.</p>

  <div class="row">
    <label>Num stations</label>
    <input id="num_stations" type="number" min="1" max="10" value="3" />
    <label>Buffers</label>
    <select id="buffers">
      <option value="true" selected>Yes</option>
      <option value="false">No</option>
    </select>
    <button onclick="build()">Generate Form</button>
    <button onclick="runKpi()">Compute KPI</button>
    <button onclick="simulate()">Run SimPy</button>
    <span id="status"></span>
  </div>

  <div id="editor_holder"></div>

  <h3>Output</h3>
  <pre id="out">—</pre>

  <p style="margin-top:20px;">
    API Docs: <a href="/docs">/docs</a>
  </p>

  <script src="https://cdn.jsdelivr.net/npm/@json-editor/json-editor@latest/dist/jsoneditor.min.js"></script>
  <script>
    let editor = null;

    async function build() {
      const status = document.getElementById('status');
      status.textContent = 'Generating...';

      const num_stations = parseInt(document.getElementById('num_stations').value || '1');
      const buffer_between = (document.getElementById('buffers').value === 'true');

      const res = await fetch('/api/template-builder/schema', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ case: { num_stations, buffer_between } })
      });
      const schema = await res.json();

      if (editor) { editor.destroy(); editor = null; }

      editor = new JSONEditor(document.getElementById('editor_holder'), {
        schema: schema,
        disable_collapse: true,
        disable_properties: true,
        no_additional_properties: true,
        required_by_default: true
      });

      const initStations = Array.from({length:num_stations}).map((_,i)=>({
        id: `S${i+1}`,
        type: (i%2===0?'assembly':'welding'),
        cycle_time_s: 20,
        availability_pct: 92,
        scrap_rate_pct: 1.0
      }));

      const initBuffers = buffer_between
        ? Array.from({length:Math.max(0,num_stations-1)}).map((_,i)=>({ id: `B${i+1}${i+2}`, capacity: 10 }))
        : [];

      editor.setValue({
        line: { line_name: "Line_A", target_throughput_pph: 180, shift_hours: 8 },
        stations: initStations,
        buffers: initBuffers,
        sim: { horizon_s: 3600, interarrival_s: 5 }
      });

      status.textContent = 'Ready';
      document.getElementById('out').textContent = '—';
    }

    function getInstanceOrShowErrors() {
      const status = document.getElementById('status');
      const out = document.getElementById('out');

      if (!editor) { status.textContent = 'Generate form first'; return null; }

      const errors = editor.validate();
      if (errors.length) {
        status.textContent = 'Fix validation errors';
        out.textContent = JSON.stringify(errors,null,2);
        return null;
      }
      return editor.getValue();
    }

    async function runKpi() {
      const status = document.getElementById('status');
      const out = document.getElementById('out');
      out.textContent = '—';

      const instance = getInstanceOrShowErrors();
      if (!instance) return;

      status.textContent = 'Computing KPI...';
      const res = await fetch('/api/compute-kpi', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ instance })
      });
      const data = await res.json();
      status.textContent = res.ok ? 'OK' : ('Error ' + res.status);
      out.textContent = JSON.stringify(data, null, 2);
    }

    async function simulate() {
      const status = document.getElementById('status');
      const out = document.getElementById('out');
      out.textContent = '—';

      const instance = getInstanceOrShowErrors();
      if (!instance) return;

      status.textContent = 'Running SimPy...';
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ instance })
      });
      const data = await res.json();
      status.textContent = res.ok ? 'OK' : ('Error ' + res.status);
      out.textContent = JSON.stringify(data, null, 2);
    }

    build();
  </script>
</body>
</html>
"""
