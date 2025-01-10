const express = require('express');
const cors = require('cors');
const schedulerRoutes = require('./scheduler');

const app = express();

// Enable CORS and JSON parsing
app.use(cors());
app.use(express.json({ limit: '50mb' })); // Increased limit for large attachments

// Use the scheduler routes
app.use(schedulerRoutes);

const PORT = 3001; // Different from React's port
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});