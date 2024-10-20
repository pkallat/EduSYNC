const express = require('express');
const cors = require('cors');
const { Sequelize, DataTypes } = require('sequelize');

// Initialize express and middleware
const app = express();
app.use(cors());
app.use(express.json());

// Initialize SQLite Database using Sequelize
const sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: 'assignmentsDB.sqlite'  // SQLite stores the DB in this file
});

// Define Assignment Model
const Assignment = sequelize.define('Assignment', {
    title: {
        type: DataTypes.STRING,
        allowNull: false
    },
    dueDate: {
        type: DataTypes.DATE,
        allowNull: false
    }
});

// Sync the database (creates tables if not exists)
sequelize.sync().then(() => {
    console.log('Database synced successfully.');
}).catch((err) => {
    console.error('Error syncing database:', err);
});

// API endpoint to get all assignments
app.get('/api/assignments', async (req, res) => {
    try {
        const assignments = await Assignment.findAll();
        res.json(assignments);
    } catch (err) {
        console.error('Failed to fetch assignments:', err);
        res.status(500).json({ error: 'Failed to fetch assignments' });
    }
});

// API endpoint to create a new assignment (for testing)
app.post('/api/assignments', async (req, res) => {
    try {
        const { title, dueDate } = req.body;
        const newAssignment = await Assignment.create({ title, dueDate });
        res.json(newAssignment);
    } catch (err) {
        console.error('Failed to create assignment:', err);
        res.status(500).json({ error: 'Failed to create assignment' });
    }
});

// Start the server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
