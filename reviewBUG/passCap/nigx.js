// Generate a simple Node.js server that accepts one or more parameters

const http = require('http');
const url = require('url');

const server = http.createServer((req, res) => {
  const queryObject = url.parse(req.url, true).query;

  console.log('Received parameters:', queryObject);
  
  // Log received parameters
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end(`Parameters received: ${JSON.stringify(queryObject)}`);
});

const PORT = 8080;
server.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
  console.log('Example usage: http://localhost:8080?param1=value1&param2=value2');
});

// Handle server errors
server.on('error', (error) => {
  if (error.code === 'EADDRINUSE') {
    console.error(`Port ${PORT} is already in use. Please try a different port.`);
  } else {
    console.error('Server error:', error);
  }
});
