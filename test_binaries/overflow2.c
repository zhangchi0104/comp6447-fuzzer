#include <stdio.h>

void win(void)  {
  system("/bin/sh");
}

char* password = "coolpassword";



int main(void)  {
  char buff[32];
  setbuf(stdout, NULL);
  
  puts("Your fuzzer will never reach the end :0");
  
  fgets(buff, sizeof(buff), stdin);
  int c;
  while ((c = getchar()) != '\n' && c != EOF);
  
  fgets(buff, sizeof(buff), stdin);
  while ((c = getchar()) != '\n' && c != EOF);
  
  puts("Not even close :p");
  
  fgets(buff, sizeof(buff), stdin);
  while ((c = getchar()) != '\n' && c != EOF);
  
  fgets(buff, sizeof(buff), stdin);
  while ((c = getchar()) != '\n' && c != EOF);
  
  fgets(buff, sizeof(buff), stdin);
  while ((c = getchar()) != '\n' && c != EOF);
  
  puts("Wait you're getting there :0");
  
  fgets(buff, sizeof(buff), stdin);
  while ((c = getchar()) != '\n' && c != EOF);
  
  fgets(buff, sizeof(buff), stdin);
  while ((c = getchar()) != '\n' && c != EOF);
  
  puts(":(");
  
  gets(buff);
  
  puts(":(");
}