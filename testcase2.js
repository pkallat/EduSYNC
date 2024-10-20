test('should display no assignments if none are returned', async () => {
  // Mock fetch to return an empty array
  fetch.mockImplementationOnce(() =>
    Promise.resolve({
      json: () => Promise.resolve([])
    })
  );

  await fetchAssignments();

  // Now test with empty data
  const assignments = await fetch('http://localhost:5000/api/assignments').then(res => res.json());
  displayAssignments(assignments);

  // Check if the assignment list is empty
  const assignmentList = document.getElementById('assignment-list');
  expect(assignmentList.children.length).toBe(0);  // No assignment items should be present
});
