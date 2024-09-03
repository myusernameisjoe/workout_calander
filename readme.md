# Workout Planner

This is an improved workout planner application that allows you to schedule workouts and set rules for workout spacing. It includes a database for persistence, improved error handling, and the ability to edit and delete events and rules.

## Setup Instructions

1. Make sure you have Python installed on your system (Python 3.7 or higher is recommended).

2. Clone this repository or download the files to your local machine.

3. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

4. Install the required Python packages:
   ```
   pip install flask flask-sqlalchemy
   ```

5. Create the following directory structure:
   ```
   workout_planner/
   ├── app.py
   ├── templates/
   │   └── index.html
   └── static/
       └── styles.css
   ```

6. Place the provided `app.py`, `index.html`, and `styles.css` files in their respective directories.

7. Run the Flask application:
   ```
   python app.py
   ```

8. Open a web browser and go to `http://localhost:5000` to use the application.

## Usage

- To add an event, fill in the "Event Title", "Tags", and "Date" fields in the "Add/Edit Event" form and click "Save Event".
- To edit an event, click on it in the calendar. The event details will populate the "Add/Edit Event" form. Make your changes and click "Save Event".
- To delete an event, click on it in the calendar and then click the "Delete" button that appears.
- To add a rule, fill in the "Tag 1", "Tag 2", and "Minimum Days" fields in the "Add/Edit Rule" form and click "Save Rule".
- To edit a rule, click the "Edit" button next to the rule in the "Current Rules" list. The rule details will populate the "Add/Edit Rule" form. Make your changes and click "Save Rule".
- To delete a rule, click the "Delete" button next to the rule in the "Current Rules" list.
- You can drag and drop events on the calendar to move them. The application will check if the move violates any rules.

## Features

- Data persistence using SQLite database
- Improved error handling with specific error messages
- Ability to edit and delete events and rules
- Enhanced UI/UX design with responsive layout
- Drag-and-drop functionality for events

## Notes

- The database file (`workouts.db`) will be created in the same directory as `app.py` when you run the application for the first time.
- Error messages are displayed as alerts in the browser.

## Future Improvements

- Implement user authentication
- Add more advanced rule types
- Create a dashboard with workout statistics
- Implement a mobile app version

## Contributing

Feel free to fork this project and submit pull requests with any improvements or bug fixes.
