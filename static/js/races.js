document.addEventListener('DOMContentLoaded', async () => {
    const today = new Date()
    const options = {weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'};
    document.getElementById('todaydate').textContent = `Today's Date: ${today.toLocaleDateString(undefined, options)}`;
    try {
        const res = await fetch('/api/allraces');
        const data = await res.json();
        console.log(data);
        const upcomingDisplay = document.getElementById('upcomingRaces');
        const pastDisplay = document.getElementById('pastRaces');
        if(!upcomingDisplay || !pastDisplay) {
            console.error('Missing race containers in HTML.');
            return;
        }
        if(data.upcomingraces && data.upcomingraces.length > 0) {
            upcomingDisplay.innerHTML = '';
            data.upcomingraces.forEach((race, index) => {
                const raceDate = new Date(race.date);
                const timeDiff = raceDate.getTime() - today.getTime();
                const daysRemaining = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
                const raceEntry = document.createElement('div');
                raceEntry.className = 'race-entry';
                raceEntry.innerHTML = `${index + 1}. ${race.title} : in ${daysRemaining} days.`;
                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = 'Delete';
                deleteBtn.style.marginLeft = '10px';
                deleteBtn.style.backgroundColor = '#617961';
                deleteBtn.style.color = 'white';
                deleteBtn.style.border = 'none';
                deleteBtn.style.borderRadius = '4px';
                deleteBtn.style.cursor = 'pointer';
                deleteBtn.style.padding = '2px 6px';
                deleteBtn.addEventListener('click', async () => {
                    if (confirm(`Delete "${race.title}"?`)) {
                        const response = await fetch(`/api/deleterace/${race.id}`, {
                            method: 'DELETE'
                        });
                        const result = await response.json();
                        if (result.success) {
                            raceEntry.remove();
                        } else {
                            alert('Failed to delete race: ' + result.error);
                        }
                    }
                });
                raceEntry.appendChild(deleteBtn);
                upcomingDisplay.appendChild(raceEntry);
            })
        } else {
            upcomingDisplay.textContent = 'No upcoming races.';
        }
        if(data.pastraces && data.pastraces.length > 0) {
            let pastText = '';
            data.pastraces.forEach((race, index) => {
                pastText += `${index + 1}. ${race.title} : on ${new Date(race.date).toLocaleDateString()}<br>`;
            });
            pastDisplay.innerHTML = pastText;
        } else {
            pastDisplay.textContent = 'No past races.';
        }
        const workoutGraphContext = document.getElementById('workoutGraph').getContext('2d');
        const workoutGraph = new Chart(workoutGraphContext, {
            type: 'bar',
            data: {
                labels: data.weeklystats.map(week => `Week ${week.weekNumber}`),
                datasets: [{
                    label: 'Miles From the Last 5 Weeks',
                    data : data.weeklystats.map(week => week.totalMiles),
                    borderColor: 'rgb(162, 202, 162)',
                    backgroundColor: 'rgb(162, 202, 162)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        console.log("Completion stats:", data.completionstats);
        const completionGraphContext = document.getElementById('completionGraph').getContext('2d');
        const completionGraph = new Chart(completionGraphContext, {
            type: 'bar',
            data: {
                labels: ['Completed', 'Total'],
                datasets: [{
                    label: 'Workouts',
                    data: [
                        Number(data.completionstats[0].completecount), 
                        Number(data.completionstats[0].totalcount)
                    ],
                    backgroundColor: ['#a2caa2', '#a2caa2'],
                    borderColor: ['#a2caa2', '#a2caa2'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true, 
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } catch(err) {
        console.error("Error fetching race data: ", err);
        document.getElementById('upcomingRaces').textContent = 'Error fetching upcoming race data.';
        document.getElementById('pastRaces').textContent = 'Error fetching previous race data.';
    }
}); async function deleteRace(raceId) {
    try {
        const response = await fetch(`/api/deleterace/${raceId}`, {
            method: 'DELETE',
        });
        const data = await response.json();
        if(response.ok) {
            alert(data.message);
            location.reload();
        } else {
            alert('Error deleting race');
        }
    } catch(err) {
        console.error("Error deleting race: ", err);
    }
}