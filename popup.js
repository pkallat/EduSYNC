document.getElementById('sync').addEventListener('click', function() {
  chrome.identity.getAuthToken({ 'interactive': true }, function(token) {
      if (chrome.runtime.lastError) {
          console.error("Full Authentication Error: ", chrome.runtime.lastError);
          alert("Failed to authenticate. Please check the console for more details.");
      } else {
          console.log('OAuth Token: ', token);
          getClassroomCourses(token);
      }
  });
});
