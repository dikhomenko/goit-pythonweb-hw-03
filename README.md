# Project Setup

## Prerequisites

- Docker
- Docker Compose

## Running the Application

1. **Ensure Docker is Installed and Running**:

2. **Ensure the `storage` Directory Exists**:

   - Make sure the `storage` directory exists in the same directory as your `docker-compose.yml` file.
   - The `storage` directory should contain the `data.json` file, otherwise it will be created.

3. **Build and Run the Docker Container**:

   - Navigate to the project directory and run the following command to build and start the application:
     ```sh
     docker-compose up --build
     ```

## Stopping the Application

- To stop the application, press `Ctrl+C` in the terminal where the application is running.
- Alternatively, you can stop the Docker container using the following command:
  ```sh
  docker-compose down
  ```
