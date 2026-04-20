const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/logs', (req, res) => {
  const filename = req.query.file || 'opencode-debug-with-events.jsonl';
  const logPath = path.join(__dirname, '..', 'references', filename);
  
  if (!fs.existsSync(logPath)) {
    return res.status(404).json({ error: 'Log file not found' });
  }

  try {
    const fileContent = fs.readFileSync(logPath, 'utf8');
    const lines = fileContent.split('\n').filter(line => line.trim() !== '');
    
    const logs = lines.map(line => {
      try {
        return JSON.parse(line);
      } catch (e) {
        return { error: 'Failed to parse line', raw: line };
      }
    });

    res.json(logs);
  } catch (error) {
    res.status(500).json({ error: 'Failed to read log file' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
