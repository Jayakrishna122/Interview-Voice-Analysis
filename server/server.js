const express = require('express');
const multer = require('multer');
const path = require('path');
const cors = require('cors'); // Import the CORS middleware

// Initialize express app
const app = express();
const port = 3000;

// Enable CORS for all routes
app.use(cors()); // This will allow all origins. You can configure it further if needed.

// Set up storage configuration for Multer
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/'); // save files to the 'uploads' directory
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname)); // give the file a unique name
  }
});

const upload = multer({ storage: storage });

// Create the uploads folder if it doesn't exist
const fs = require('fs');
if (!fs.existsSync('uploads')) {
  fs.mkdirSync('uploads');
}

// Serve static files from the 'uploads' folder
app.use('/uploads', express.static('uploads'));

// Handle POST request for file upload
app.post('/upload', upload.single('audio'), (req, res) => {
  if (req.file) {
    // Return the file path if upload is successful
    res.json({ file_path: `${req.file.filename}` });
  } else {
    res.status(400).json({ error: 'No file uploaded' });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
