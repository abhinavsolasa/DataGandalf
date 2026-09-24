# Frontend for Data Gandalf

## Running Locally

In order to run the backend locally, a [Node.js](https://nodejs.org/en) version of 20.5 or higher is required. The following steps can be run to get the frontend running.

1. Install the dependencies.

    ```bash
    npm install
    ```

2. Run the frontend. This will run in development mode.

    ```bash
    npm run dev
    ```

3. Set the location of the backend if needed. This can be done using environment variables. By default, this is set to <http://localhost:8080> and should work loacally.

    ```bash
    export BACKEND_ADDRESS="address:port of the backend"
    ```

4. Access the webpage though [127.0.0.1:3000](127.0.0.1:3000).

## Running with Docker

1. In order to run the backend in a container, Docker needs to be installed and the image needs to be built.

    ```bash
    docker build . -t frontend
    ```

2. Once built, the container can be run in the background. This currently runs in development mode.

    ```bash
    docker run -dit --name frontend -p 3000:3000 frontend
    ```

3. If the location of the backend is not <http://localhost:8080>, use the following command.

    ```bash
    docker run -dit --name frontend -e BACKEND_ADDRESS="address:port of the backend" -p 3000:3000 frontend
    ```

4. The webpage can then be accessed at [127.0.0.1:3000](127.0.0.1:3000).

