const request = require('supertest');
const express = require('express');
const { Sequelize, DataTypes } = require('sequelize');
const bodyParser = require('body-parser');

// Setup an express app for testing
const app = express();
app.use(bodyParser.json());

// Setup an in-memory SQLite database for testing
const sequelize = new Sequelize('sqlite::memory:');

// Define Assignment model
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

// Routes for testing
app.get('/api/assignments', async (req, res) => {
    try {
        const assignments = await Assignment.findAll();
        res.json(assignments);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch assignments' });
    }
});

app.post('/api/assignments', async (req, res) => {
    try {
        const { title, dueDate } = req.body;
        const newAssignment = await Assignment.create({ title, dueDate });
        res.json(newAssignment);
    } catch (err) {
        res.status(500).json({ error: 'Failed to create assignment' });
    }
});

// Test setup
beforeAll(async () => {
    await sequelize.sync({ force: true }); // Recreate the tables before each test run
});

// Test cases
describe('Assignments API', () => {
    test('should return an empty list of assignments initially', async () => {
        const response = await request(app).get('/api/assignments');
        expect(response.statusCode).toBe(200);
        expect(response.body.length).toBe(0);
    });

    test('should create a new assignment', async () => {
        const newAssignment = { title: 'Math Homework', dueDate: '2024-10-21' };
        const response = await request(app).post('/api/assignments').send(newAssignment);
        
        expect(response.statusCode).toBe(200);
        expect(response.body.title).toBe(newAssignment.title);
        expect(response.body.dueDate).toBe(newAssignment.dueDate);
    });

    test('should return a list of assignments after one is created', async () => {
        const response = await request(app).get('/api/assignments');
        
        expect(response.statusCode).toBe(200);
        expect(response.body.length).toBe(1);  // Should contain the previously added assignment
        expect(response.body[0].title).toBe('Math Homework');
    });
});

