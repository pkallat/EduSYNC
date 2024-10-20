const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(cors()); // Allow requests from other origins (needed for web extensions)

mongoose.connect('mongodb://localhost:27017/assignmentsDB', {
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(() => console.log('Connected to MongoDB'))
.catch((err) => console.log('Error connecting to MongoDB:', err));

// Define an Assignment model
const Assignment = mongoose.model('Assignment', {
    title: String,
    dueDate: String
});

// API endpoint to get all assignments
app.get('/api/assignments', async (req, res) => {
    try {
        const assignments = await Assignment.find();
        res.json(assignments);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch assignments' });
    }
});

// Server start
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
