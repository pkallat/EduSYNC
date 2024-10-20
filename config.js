const mysql = require('mysql');

const dbConfig = {
    host: 'localhost',
    user: 'root',              // Replace with your database username
    password: 'your_password', // Replace with your database password
    database: 'blackboard_assignments' // Name of your database
};

const connection = mysql.createConnection(dbConfig);

connection.connect((err) => {
    if (err) {
        console.error('Error connecting to the database:', err.stack);
        return;
    }
    console.log('Connected to the database as ID', connection.threadId);
});

module.exports = connection; // Export the connection for use in other files
