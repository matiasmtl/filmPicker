# My Python Project

## Overview
This project is a Python application that includes various modules and utility functions. It serves as a template for building Python applications.

## Project Structure
```
my-python-project
├── src
│   ├── main.py
│   └── utils
│       └── helper.py
├── requirements.txt
├── .vscode
│   ├── launch.json
│   └── settings.json
└── README.md
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd my-python-project
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute the following command:
```
python src/main.py
```

## Deployment with Docker

### Option 1: Using docker-compose.yml directly
No additional setup required. Default environment variables are included.

### Option 2: Using custom environment variables
1. Create a .env file in your deployment directory:
```bash
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your_secret_key_here
MOVIES_FILE=/app/src/movies.json
```

2. Update the docker-compose.yml to use your .env file:
```yaml
services:
  web:
    image: matiasmtl/movie-picker:latest
    env_file:
      - .env
    # ... rest of configuration
```

## Contributing
Feel free to submit issues or pull requests for improvements and bug fixes.