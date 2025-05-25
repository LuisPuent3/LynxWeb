// Script para depurar los servicios en Railway
const express = require('express');
const axios = require('axios');

const app = express();

app.get('/debug/python', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/health', { timeout: 5000 });
        res.json({ 
            status: 'Python service is running', 
            python_response: response.data 
        });
    } catch (error) {
        res.status(500).json({ 
            status: 'Python service not accessible', 
            error: error.message,
            code: error.code 
        });
    }
});

app.get('/debug/processes', (req, res) => {
    const { exec } = require('child_process');
    exec('ps aux', (error, stdout, stderr) => {
        if (error) {
            return res.status(500).json({ error: error.message });
        }
        res.json({ processes: stdout });
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Debug server running on port ${PORT}`);
});
