# Task Management Web Application

## Overview
This is a task management and collaboration web application developed as a practical project for the Web Application Frameworks course. The project uses Flask as the backend framework and aims to provide users with a platform to create, manage, and collaborate on tasks.

## Features
- **User Registration and Login**: Users can register and securely log in.
- **Task and Category Management**: Create categories and tasks within those categories, mark them as completed, and organize them based on priorities.
- **Collaboration**: Share tasks with other users and manage access through roles (e.g., Admin, Editor).
- **Dashboard**: View and filter tasks, visualize completed tasks, and track overall progress.
- **Calendar Integration**: Set deadlines, work sessions, and recurring tasks, visualized through an integrated calendar.
- **Role-Based Access Control**: Assign roles such as Admin, Editor, or Viewer to different users for shared tasks.

## Getting Started
### Prerequisites
- Python 3.x
- Flask
- Other dependencies as mentioned in `requirements.txt`

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd task_management_app
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the environment variables:
   - Create a `.env` file to store your Flask secret key and other configurations.
5. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

### Running the Application
To run the application locally, use the following command:
```bash
flask run
```
Access the application at `http://127.0.0.1:5000/`.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Flask documentation
