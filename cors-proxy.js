const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const { v4: uuidv4 } = require('uuid');

const app = express();
const sessionStore = {}; // In-memory session store for development

// This middleware intercepts the response from the server.
// If the server sends back a session ID, we store it for future requests from that client.
const handleSessionResponse = (proxyRes, req, res) => {
  const clientIp = req.ip;
  const serverSentSessionId = proxyRes.headers['mcp-session-id'];

  if (serverSentSessionId) {
    if (!sessionStore[clientIp] || sessionStore[clientIp] !== serverSentSessionId) {
      sessionStore[clientIp] = serverSentSessionId;
      console.log(`[Proxy Session] Captured/Updated session ID ${serverSentSessionId} for client ${clientIp}`);
    }
  }
  // Also, add the required CORS headers to every response.
  proxyRes.headers['Access-Control-Allow-Origin'] = req.headers.origin || '*';
  proxyRes.headers['Access-Control-Allow-Credentials'] = 'true';
};


// This middleware intercepts the request from the client.
// If we have a stored session ID for this client, we add it to the request header.
const handleSessionRequest = (proxyReq, req, res) => {
    const clientIp = req.ip;
    if (sessionStore[clientIp]) {
        const sessionId = sessionStore[clientIp];
        proxyReq.setHeader('mcp-session-id', sessionId);
        console.log(`[Proxy Session] Injected session ID ${sessionId} for client ${clientIp}`);
    } else {
        console.log(`[Proxy Session] No session ID found for client ${clientIp}. Sending request without it.`);
    }
};

// The OPTIONS preflight request must be handled for CORS.
app.options('/mcp/', (req, res) => {
    console.log(`[CORS] Handling OPTIONS request from origin: ${req.headers.origin}`);
    res.setHeader('Access-Control-Allow-Origin', req.headers.origin || '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, mcp-protocol-version, mcp-session-id');
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.sendStatus(200);
});

// Create the proxy middleware with our custom handlers.
const mcpProxy = createProxyMiddleware({
  target: 'http://127.0.0.1:8001',
  changeOrigin: true,
  ws: true,
  logLevel: 'debug',
  onProxyReq: handleSessionRequest,
  onProxyRes: handleSessionResponse,
  onError: (err, req, res) => {
    console.error('[Proxy Error]', err);
    res.status(500).send('Proxy error. Could not connect to the backend server.');
  }
});

// Apply the proxy middleware.
app.use('/mcp/', mcpProxy);


const PORT = 8002;
app.listen(PORT, () => {
  console.log(`🚀 CORS proxy server running on http://127.0.0.1:${PORT}`);
  console.log("   Forwarding requests from /mcp/ to http://127.0.0.1:8001/mcp/");
}); 