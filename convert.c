#include <string.h>
  
struct InteropString 
{ 
   const unsigned char *content;
   unsigned int len;
}; 
  
struct InteropString convert(char string[])  
{ 
   struct InteropString obj; 
  	obj.content = string;
  	obj.len = strlen(string);
   // Accessing members of point p1 
  
   return obj; 
}

// #include <string.h>
// typedef struct {
//     const unsigned char *content;
//    	unsigned int len;
// } InteropString;

// InteropString convert(char string) 
// {
// 	struct Point obj = {string, strlen(string);};
//     return obj;
// }
