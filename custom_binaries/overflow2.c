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
  int c;
  while ((c = getchar()) != '\n' && c != EOF);
  if (buff == password) {
    win();
  }
  
  puts("Try again h4x0r!");
  
  gets(buff);
  
  if (buff == password) {
    win();
  }
}