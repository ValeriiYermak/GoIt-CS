1. You can run the application locally or using Docker. If you want to run it locally, follow these steps:
2. Create a .env file with the following content:
    {MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
    MONGO_HOST=
    MONGO_PORT=27017
    MONGO_DB_NAME=chat_db
    MONGO_USER=
    MONGO_PASSWORD=
    }
3. Run the application with the following command:
   python main.py
4. Access the application at http://localhost:3000
5. If you want to run it using Docker, follow these steps:
6. Build the Docker image with the following command:
   docker build -t socket_server .
7. Run the Docker container with the following command:
   docker run -d --name socket_server_container -p 3000:3000 -p 5000:5000 --env-file .env socket_server
8. Access the application at http://localhost:3000
9. If you want to run it using Docker-Compose, follow these steps:
10. Run the Docker-Compose file with the following command:
   docker-compose up
11. Access the application at http://localhost:3000

Have a nice day!



