const fetchMock = require('fetch-mock');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

// Mock the fetch function
global.fetch = fetchMock.sandbox();

// Define the HTML structure and mock document
const { window } = new JSDOM(`
    <body>
        <div id="assignment-list"></div>
    </body>
`);
global.document = window.document;

// The function being tested (this would be in your real JS file)
async function fetchAssignments() {
    try {
        const response = await fetch('http://localhost:5000/api/assignments');
        const assignments = await response.json();
        displayAssignments(assignments);
    } catch (error) {
        console.error('Error fetching assignments:', error);
    }
}

function displayAssignments(assignments) {
    const assignmentList = document.getElementById('assignment-list');
    assignmentList.innerHTML = '';

    if (assignments.length === 0) {
        assignmentList.innerHTML = '<p>No assignments found.</p>';
        return;
    }

    assignments.forEach(assignment => {
        const assignmentDiv = document.createElement('div');
        assignmentDiv.className = 'assignment';
        assignmentDiv.innerHTML = `
            <h3>${assignment.title}</h3>
            <p>Due: ${new Date(assignment.dueDate).toLocaleDateString()}</p>
        `;
        assignmentList.appendChild(assignmentDiv);
    });
}

// Test cases
describe('Fetch and display assignments', () => {
    afterEach(() => {
        fetch.reset();
    });

    test('should fetch and display assignments', async () => {
        // Mock successful API response
        fetch.get('http://localhost:5000/api/assignments', [
            { title: 'Math Homework', dueDate: '2024-10-21' }
        ]);

        await fetchAssignments();

        const assignmentList = document.getElementById('assignment-list');
        expect(assignmentList.innerHTML).toContain('Math Homework');
    });

    test('should display no assignments message if none are returned', async () => {
        // Mock API response with no assignments
        fetch.get('http://localhost:5000/api/assignments', []);

        await fetchAssignments();

        const assignmentList = document.getElementById('assignment-list');
        expect(assignmentList.innerHTML).toContain('No assignments found.');
    });

    test('should handle fetch error', async () => {
        // Mock fetch failure
        fetch.get('http://localhost:5000/api/assignments', 500);

        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

        await fetchAssignments();

        expect(consoleSpy).toHaveBeenCalledWith('Error fetching assignments:', expect.any(Error));
        consoleSpy.mockRestore();
    });
});

