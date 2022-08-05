#include <stdio.h>

void win(void)  {
  system("/bin/sh");
}

char* password = "coolpassword";

int main(void)  {
  char buff[32];
  setbuf(stdout, NULL);
  
  puts("I have a cool password that you'll never guess muahahaha!");
  
  fgets(buff, sizeof(buff), stdin);
  
  printf(buff);
  
  if (buff == password) {
    win();
  }
}