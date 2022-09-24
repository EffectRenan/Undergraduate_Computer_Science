#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

#include "file.c"

#define MAX_SERVER_REPLY 10000
#define MAX_MESSAGE 1000

#define IP "127.0.0.1"
#define PORT 8989

int main(int argc , char *argv[])
{
	int sock;
	struct sockaddr_in server;
	char message[MAX_MESSAGE];
    char server_reply[MAX_SERVER_REPLY];
	
	sock = socket(AF_INET, SOCK_STREAM, 0);
	if (sock == -1) {
		printf("Error: Create socket");
        return 1;
	}
	
	server.sin_addr.s_addr = inet_addr(IP);
	server.sin_family = AF_INET;
	server.sin_port = htons(PORT);

	if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0){
		printf("Error: Connect failed");
		return 1;
	}

    recv(sock, server_reply, MAX_SERVER_REPLY, 0);
    printf("%s", server_reply);
    memset(server_reply, 0, strlen(server_reply));
	
	while(1) {
		printf("\nCommand: ");
        fgets(message, MAX_MESSAGE, stdin);
        
        if (message[0] == '\n') { 
            message[0] = 0;
            continue;
        }

		if(send(sock, message, strlen(message) - 1, 0) < 0) {
			puts("Send failed");
			return 1;
		}
		
		if(recv(sock, server_reply, MAX_SERVER_REPLY, 0) < 0) {
			puts("Recv failed");
			break;
		}
		

		puts("Server reply:");
		printf("%s\n", server_reply);
        
        if (strcmp(server_reply, "Bye") == 0) {
            break;
        } else if (strcmp(server_reply, "Invalid command") != 0) {
            char *name = strtok(message, " ");
            name = strtok(NULL, "\n");

            write_content(name, server_reply);
        }

        memset(message, 0, strlen(message));
        memset(server_reply, 0, strlen(server_reply));
	}
	
	close(sock);
	return 0;
}
