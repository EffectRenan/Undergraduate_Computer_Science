#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_FILES 100
#define FILES_SERVER_PATH "./server_files/"
#define FILES_CLIENT_PATH "./client_files/"

int size(FILE* ptr) {
    fseek(ptr, 0, SEEK_END);
    int size = ftell(ptr);
    fseek(ptr, 0 , SEEK_SET);
    return size;
}

// Avoiding . and .. as a valid path
int dot(char *path) {
    const int size = strlen(path);

    if ((size == 1 && path[0] == '.') || 
        (size == 2 && path[0] == '.' && path[1] == '.'))
        return 0;

    return 1;
}

char* read_content(char *name) {

    if (!dot(name))
        return 0;

    char path [strlen(FILES_SERVER_PATH) + strlen(name)];
    memset(path, 0, strlen(path));

    strcat(path, FILES_SERVER_PATH);
    strcat(path, name);

    FILE* ptr;
    
    ptr = fopen(path, "r");

    if (ptr == NULL) {
        return 0;
    }

    int file_size = size(ptr);
    char *buffer = 0;
    buffer = malloc(file_size);

    fscanf(ptr, "%[^\n]", buffer);
    fclose(ptr);

    return buffer;
}

void write_content(char* name, char* content) {
    char path [strlen(FILES_CLIENT_PATH) + strlen(name)];
    memset(path, 0, strlen(path));

    strcat(path, FILES_CLIENT_PATH);
    strcat(path, name);

    FILE* ptr;
    
    ptr = fopen(path, "w");

    if (ptr == NULL) {
    }

    int file_size = size(ptr);

    fprintf(ptr, "%s", content);

    fclose(ptr);

}
