document.addEventListener('DOMContentLoaded', function() {
    var myCal = document.getElementById('calendar');
    var cal = new FullCalendar.Calendar(myCal, {
        initialView: 'dayGridMonth',
        events: '/api/events', // The endpoint for fetching calendar events
        eventClick: function(info) {
            alert('Workout: ' + info.event.title);  // You can customize the alert to show more info
        },
        eventContent: function(arg) {
            let deleteButton = document.createElement('button');
            deleteButton.innerText = 'X';
            deleteButton.classList.add('delete-btn');
            deleteButton.style.marginLeft = '15px';
            deleteButton.style.background = '#a2caa2';
            deleteButton.addEventListener('click', function(e) {
                e.stopPropagation(); // Prevent default event click
                console.log("Event extendedProps:", arg.event.extendedProps); 
                const workoutID = arg.event.extendedProps.workoutID;
                if (confirm("Delete this workout?")) {
                    console.log("sending workoutid: ", workoutID);
                    $.ajax({
                        url: '/api/deleteWorkout',
                        method: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({ workoutID: workoutID }),
                        success: function(response) {
                            console.log('Workout deleted:', response);
                            arg.event.remove(); // Remove event from calendar
                            cal.refetchEvents();
                        },
                        error: function(xhr, status, error) {
                            console.error('Error deleting workout:', xhr.responseText);
                        }
                    });
                }
            });
            return {
                domNodes: [
                    document.createTextNode(arg.event.title),
                    deleteButton
                ]
            };
        }
    });
    cal.render();
    // Fetch today's workouts
    fetchTodaysWorkouts();
    // Function to fetch today's workouts
    function fetchTodaysWorkouts() {
        $.ajax({
            url: '/api/todaysworkout',  // Ensure the backend endpoint matches
            method: 'GET',
            success: function(data) {
                displayTodaysWorkouts(data);
            },
            error: function() {
                console.log('Error fetching today\'s workouts');
            }
        });
    }
    // Function to display today's workouts above the calendar
    function displayTodaysWorkouts(workouts) {
        var workoutList = $('#todays-workout-list');  // The div to show today's workouts
        workoutList.empty();  // Clear existing workouts
        if(workouts.length === 0) {
            workoutList.append('<p>No workouts today.</p>');
        } else {
            workouts.forEach(function(workout) {
                var isComplete = workout.isCompleted;
                var checkedAtt = isComplete ? 'checked' : '';
                var disableAtt = isComplete ? 'disabled' : '';
                var greyout = isComplete ? 'completed-workout' : '';
                workoutList.append(
                    `<div class="workout-item ${greyout}">
                        <h3 class="workout-title">${workout.type}</h3>
                        <div class="workout-row">
                            <div class="workout-col1">
                                <span class="label"><strong>Distance:</strong> ${workout.distance} miles</span>
                                <span class="label"><strong>Duration:</strong> ${workout.duration} minutes</span>
                                <span class="label"><strong>Shoes:</strong> ${workout.shoe_name}</span>
                            </div>
                            <div class="workout-col2">
                            <span class="label"><strong>Completed?</strong>  
                                <input type="checkbox" id="completed-${workout.id}" class="complete-workout"
                                    data-id="${workout.id}" data-equipment-id="${workout.equipment_id}"
                                    data-distance="${workout.distance}" ${checkedAtt} ${disableAtt}></span>
                                <span class="label"><strong>Notes:</strong></span>
                                <span class="value">${workout.notes}</span>
                            </div>
                        </div>
                    </div>`                    
                );
            });
        }
    }
    $.get('/api/todaysworkout', function(workouts) {
        displayTodaysWorkouts(workouts);
    })
    // Submit new workout via AJAX
    // Example form submission for adding a workout (this needs to match your form structure)
    $('form').on('submit', function(e) {
        e.preventDefault();  // Prevent default form submission
        var formData = new FormData(this);  // Collect form data
        fetch('/api/addWorkout', {
            method: 'POST', 
            body: formData
        }).then(res => {
            if(res.ok) {
                cal.refetchEvents();  // Refetch FullCalendar events after adding a workout
                fetchTodaysWorkouts();  // Re-fetch today's workouts as well
            }
        }).catch(error => {
            console.log('Error adding workout:', error);
        });
    });
    $(document).on('change', '.complete-workout', function() {
        console.log("checking the box");
        var checkbox = $(this);
        var isCompleted = checkbox.prop('checked');
        if(!isCompleted) {
            return;
        }
        var workoutID = checkbox.data('id');
        var equipID = checkbox.data('equipmentId')
        var distance = checkbox.data('distance')
        console.log("Marked complete:", workoutID)
        $.ajax({
            url: '/api/markComplete',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                workoutID: workoutID,
                equipmentID: equipID,
                distance: distance
            }),
            success: function(response) {
                console.log("completed");
                checkbox.prop('disabled', true);
                checkbox.closest('.workout-item').addClass('completed-workout');
                if(typeof response.newMiles === 'number') {
                    $('#miles-display'.text(response.newMiles.toFixed(2)));
                }
                alert('Update shoe mileage: ' + response.newMiles.toFixed(0) + ' miles.');
            },
            error: function(xhr, status, error) {
                console.log('Error marking complete: ', status, error);
                checkbox.prop('checked', false);
            }
        })
    });
});

