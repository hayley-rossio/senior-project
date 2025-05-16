document.addEventListener('DOMContentLoaded', async () => {
    const today = new Date();
    const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
    document.getElementById('todaydate').textContent = `Today's Date: ${today.toLocaleDateString(undefined, options)}`;
    try {
        const res = await fetch('/api/nextrace');
        const data = await res.json();
        const upcomingDisplay = document.getElementById('upcomingRaces');
        if (!upcomingDisplay) {
            console.error('Missing race container in HTML.');
            return;
        }
        if (data.upcomingraces && data.upcomingraces.length > 0) {
            let upcomingText = 'Upcoming Races:<br>';
            data.upcomingraces.forEach((race, index) => {
                const raceDate = new Date(race.date);
                const timeDiff = raceDate.getTime() - today.getTime();
                const daysRemaining = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
                upcomingText += `${index + 1}. ${race.title} : in ${daysRemaining} day(s).<br>`;
            });
            upcomingDisplay.innerHTML = upcomingText;
            console.log(data.upcomingraces);
        } else {
            upcomingDisplay.textContent = 'No upcoming races.';
        }
    } catch (err) {
        console.error("Error fetching race data: ", err);
        document.getElementById('upcomingRaces').textContent = 'Error fetching upcoming race data.';
    }
});