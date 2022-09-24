#include <arpa/inet.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <string.h>

#include "file.c"

#define MAX_FILENAME 100
#define MAX_CONNECTIONS 50 
#define PORT 8989

pthread_t tid;
pthread_t client_threads[MAX_CONNECTIONS];
int client_sockets[MAX_CONNECTIONS];

void* client(void* arg)
{
    int new_socket = *((int *) arg);
    char command[MAX_FILENAME];
    char invalid_command[] = "Invalid command";
    char bye[] = "Bye";
    char *content = 0;
    char *token = 0;

    char* instructions = "INSTRUCTIONS\n\nServer directory files: ./server_files/\nGet file: get <file>\nQuit: quit\n";
    send(new_socket, instructions, strlen(instructions), 0);

    while (strcmp(command, "quit")) {

        printf("Waiting client %d ...\n", new_socket);

        if (!recv(new_socket, command, MAX_FILENAME, 0))
            break;

        if (strlen(command) < strlen("quit")) {
            if(!send(new_socket, invalid_command, strlen(invalid_command), 0))
                break;

            continue;
        }

        printf("From client %d: %s\n", new_socket, command);
        token = strtok(command, " ");

        if (strcmp(token, "get") == 0) {
            token = strtok(NULL, " ");

            if (token != NULL) {
                content = read_content(token);
                if (content != 0) {
                    if(!send(new_socket, content, strlen(content), 0))
                        break;

                    memset(content, 0, strlen(content));
                } else {
                    if(!send(new_socket, invalid_command, strlen(invalid_command), 0))
                        break;
                }
            }
        } else if (strcmp(command, "quit") == 0) {
            send(new_socket, bye, strlen(bye), 0);
            break;
        } else {
            if(!send(new_socket, invalid_command, strlen(invalid_command), 0))
                break;
        }

        memset(token, 0, strlen(token));
    }

    printf("Close client %d\n", new_socket);
    close(new_socket);
	pthread_exit(NULL);
}

int main()
{
	int serverSocket, new_socket;
	struct sockaddr_in serverAddr;
	struct sockaddr_storage serverStorage;

	socklen_t addr_size;

	serverSocket = socket(AF_INET, SOCK_STREAM, 0);
	serverAddr.sin_addr.s_addr = INADDR_ANY;
	serverAddr.sin_family = AF_INET;
	serverAddr.sin_port = htons(PORT);

	bind(serverSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr));

	if (listen(serverSocket, MAX_CONNECTIONS) == 0)
		printf("Listening\n");
	else
		printf("Error\n");

	pthread_t tid[MAX_CONNECTIONS + 10];

	int i = 0;
	while (1) {
		addr_size = sizeof(serverStorage);

		client_sockets[i] = accept(serverSocket,
						(struct sockaddr*)&serverStorage,
						&addr_size);

        pthread_create(&client_threads[i], NULL, client, &client_sockets[i]);

		if (++i >= MAX_CONNECTIONS) {
            int j = 0;
            while (j < MAX_CONNECTIONS / 2) {
                pthread_join(client_threads[j], NULL);
                client_sockets[j++] = 0;
            }
		}
	}

	return 0;
}

