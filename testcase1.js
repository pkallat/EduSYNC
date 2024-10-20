// assignments.test.js
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

// Mock the fetch function
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve([
      { title: "Math Homework 1", dueDate: "2024-10-21" },
      { title: "History Essay", dueDate: "2024-10-23" }
    ])
  })
);

// Import the functions from the original JS file (assuming the logic is separated from the HTML file)
const { fetchAssignments, displayAssignments } = require('./assignments'); // path to your JS file

describe('Assignment fetching and displaying', () => {
  let document;

  beforeEach(() => {
    // Create a fake DOM for testing
    const dom = new JSDOM(`
      <body>
        <div id="assignment-list"></div>
      </body>
    `);
    document = dom.window.document;
  });

  test('should fetch and display assignments successfully', async () => {
    // Call fetchAssignments (it should use the mocked fetch)
    await fetchAssignments();

    // Check if fetch was called
    expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/assignments');

    // Now call displayAssignments to populate the assignment list
    const assignments = await fetch('http://localhost:5000/api/assignments').then(res => res.json());
    displayAssignments(assignments);

    // Check if assignments were added to the DOM
    const assignmentList = document.getElementById('assignment-list');
    expect(assignmentList.innerHTML).toContain('Math Homework 1');
    expect(assignmentList.innerHTML).toContain('History Essay');
  });
});
